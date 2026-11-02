"""Assignments, linked states, reversible runtime hooks and native form behavior."""
from copy import deepcopy
import importlib
import json
import os
from pathlib import Path
import sys
import tempfile
from threading import Thread
import unittest
from unittest.mock import patch
from urllib.request import ProxyHandler, build_opener
from tests.test_game_workshop import serve, TEST_ROOT
from button_bridge import storage
from button_usage import ButtonUsage, UsageConflict
from source_buttons import SourceButtons

ROOT=serve.ROOT


class ButtonUsageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources=SourceButtons()
        cls.start='approved-guesstimate-start-action'
        cls.asset=next(a for a in cls.sources.assets() if a['label']=='spielen →' and a['game']=='Guesstimate')

    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=TEST_ROOT)
        self.directory=Path(self.temp.name)
        self.store=storage.RecipeStore(self.directory/'buttons')
        self.usage=ButtonUsage(self.directory/'library',self.store,self.sources)
        original=self.sources.recipe(self.asset['id'],storage.CATALOG)
        original['name']='Gemeinsamer grüner Testbutton'
        original['settings'].update(accent='#246b43',depth=8)
        original['base']['surface_mode']='custom'
        self.recipe=self.store.save(original)

    def tearDown(self):self.temp.cleanup()

    def update(self,recipe_id,models,revision=None):
        return self.usage.update(dict(revision=revision,recipe_id=recipe_id,models=models))

    def test_linked_start_states_form_one_atomic_group_and_do_not_implicitly_include_similar_buttons(self):
        row=next(r for r in self.usage.catalog()['models'] if r['id']==self.start)
        self.assertTrue(row['supported']);self.assertEqual(len(row['uses']),2)
        result=self.update(self.recipe['id'],[self.start])
        self.assertEqual(self.usage.state()['bindings'],{self.start:self.recipe['id']})
        self.assertEqual(next(r for r in result['models'] if r['id']==self.start)['active_name'],self.recipe['name'])

    def test_additional_group_reset_and_stale_revision_preserve_other_assignments_and_recipes(self):
        path=self.store.directory/(self.recipe['id']+'.json');before=path.read_bytes()
        extra=next(r['id'] for r in self.usage.models.values() if any('alle 3 verpassten' in u['label'] for u in r['uses']))
        a=self.update(self.recipe['id'],[self.start,extra])
        with self.assertRaises(UsageConflict):self.update(None,[self.start])
        b=self.update(None,[self.start],a['revision'])
        self.assertEqual(self.usage.state()['bindings'],{extra:self.recipe['id']})
        self.assertEqual(len(list(self.usage.directory.glob('usage-*.json'))),2)
        self.assertEqual(path.read_bytes(),before)
        self.assertNotIn('notes',self.usage.runtime()['recipes'][self.recipe['id']])
        self.assertNotEqual(a['revision'],b['revision'])

    def test_unknown_models_shapes_and_unsupported_components_cannot_be_activated(self):
        unsupported=next(r['id'] for r in self.usage.models.values() if not r['supported'])
        for models in ([unsupported],['../../x'],[{}],[self.start,self.start],[]):
            with self.assertRaises(ValueError):self.update(self.recipe['id'],models)
        value=deepcopy(self.recipe);value['kind']='shape';shape=self.store.save(value)
        with self.assertRaises(ValueError):self.update(shape['id'],[self.start])
        self.assertIsNone(self.usage.state()['revision'])

    def test_identical_looking_unapproved_sources_remain_separate_choices(self):
        seen={}
        for row in self.usage.models.values():
            if row['model_id'].startswith('approved-'):continue
            if row['model_id'] in seen:
                self.assertNotEqual(row['id'],seen[row['model_id']]);return
            seen[row['model_id']]=row['id']
        self.fail('Kein Paar vergleichbarer, unabhängiger Quellen gefunden.')

    def test_editor_reopens_exact_assigned_version_in_both_linked_states_and_reset_returns_original(self):
        revision=self.update(self.recipe['id'],[self.start])['revision']
        newer=deepcopy(self.recipe);newer['parent_id']=self.recipe['id'];newer['settings']['font_scale']=150
        unassigned=self.store.save(newer)
        before={path:path.read_bytes() for path in self.store.directory.glob('*.json')}
        for use in self.usage.models[self.start]['uses']:
            result=self.usage.editor_recipe(use['id'],storage.CATALOG)
            self.assertTrue(result['persisted'])
            self.assertEqual(result['recipe'],self.recipe)
            self.assertNotEqual(result['recipe']['id'],unassigned['id'])
            runtime=self.usage.runtime()['recipes'][result['recipe']['id']]
            for key in ('settings','base','contour'):
                self.assertEqual(result['recipe'][key],runtime[key])
        self.update(None,[self.start],revision)
        result=self.usage.editor_recipe(self.asset['id'],storage.CATALOG)
        self.assertFalse(result['persisted'])
        self.assertEqual(result['recipe'],self.sources.recipe(self.asset['id'],storage.CATALOG))
        self.assertEqual({path:path.read_bytes() for path in before},before)

    def test_editor_reports_unreadable_assignment_instead_of_silently_loading_original(self):
        self.update(self.recipe['id'],[self.start])
        path=self.store.directory/(self.recipe['id']+'.json')
        path.write_text('{}',encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'zugeordnete Buttonentwurf'):
            self.usage.editor_recipe(self.asset['id'],storage.CATALOG)
        with self.assertRaisesRegex(ValueError,'nicht registriert'):
            self.usage.editor_recipe('unknown',storage.CATALOG)

    def test_editor_http_route_uses_assignment_in_both_workshops_and_leaves_original_reference_intact(self):
        from button_bridge import BUTTON_DIR
        spec=importlib.util.spec_from_file_location('button_workshop_reopen_serve',BUTTON_DIR/'serve.py')
        standalone=importlib.util.module_from_spec(spec)
        with patch.object(sys,'path',[str(BUTTON_DIR),*sys.path]):
            spec.loader.exec_module(standalone)
        factories=(lambda base:serve.make_server(0,base/'library',base/'buttons'),
                   lambda base:standalone.make_server(0,base/'buttons'))
        opener=build_opener(ProxyHandler({}))
        for index,factory in enumerate(factories):
            with self.subTest(workshop=index):
                server=factory(self.directory/str(index))
                usage=server.library.button_usage if hasattr(server,'library') else server.button_usage
                recipe=usage.recipes.save(self.recipe)
                usage.update(dict(revision=None,recipe_id=recipe['id'],models=[self.start]))
                thread=Thread(target=server.serve_forever,daemon=True);thread.start()
                base='http://127.0.0.1:'+str(server.server_port)
                try:
                    with opener.open(base+'/api/button-usage/'+self.asset['id']+'/editor',timeout=5) as response:
                        result=json.load(response)
                    self.assertTrue(result['persisted']);self.assertEqual(result['recipe'],recipe)
                    with opener.open(base+'/api/game-buttons/'+self.asset['id']+'/recipe',timeout=5) as response:
                        original=json.load(response)['recipe']
                    self.assertNotEqual(original['settings']['accent'],recipe['settings']['accent'])
                finally:
                    server.shutdown();server.server_close();thread.join(3)

    def test_template_instrumentation_preserves_original_sources_and_native_actions(self):
        path=ROOT/'templates/home.html';before=path.read_bytes()
        result=self.usage.instrument('home.html',before.decode('utf-8'))
        self.assertEqual(result.count('data-workshop-model="'+self.start+'"'),2)
        self.assertIn("url_for('start_round')",result)
        self.assertIn("url_for('result')",result)
        self.assertIn('name="csrf_token"',result)
        self.assertEqual(path.read_bytes(),before)
        for row in self.usage.models.values():
            if not row['supported']:continue
            for use in row['uses']:
                name=use['path'].removeprefix('templates/')
                source=(ROOT/use['path']).read_text(encoding='utf-8')
                self.assertIn('data-workshop-model="'+row['id']+'"',self.usage.instrument(name,source),row['name'])


class LocalRuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bootstrap=tempfile.TemporaryDirectory(dir=TEST_ROOT)
        sys.path.insert(0,str(ROOT/'.deps'))
        with patch.dict(os.environ,{'QUIZ_DATABASE':str(Path(cls.bootstrap.name)/'bootstrap.sqlite3'),'QUIZ_SECRET_KEY':'qa-only','QUIZ_LOCAL_DEVELOPMENT':'0','QUIZ_MAIL_USER':'','QUIZ_MAIL_TO':''}):
            cls.module=importlib.import_module('app')

    @classmethod
    def tearDownClass(cls):cls.bootstrap.cleanup()

    def test_local_runtime_is_opt_in_and_preserves_native_game_routes(self):
        with tempfile.TemporaryDirectory(dir=TEST_ROOT) as folder:
            base=Path(folder)
            config=dict(TESTING=True,SECRET_KEY='qa-only',DATABASE=str(base/'game.sqlite3'),LOCAL_DEVELOPMENT=True,
                        BUTTON_DESIGN_LIBRARY=base/'library',BUTTON_RECIPE_LIBRARY=base/'buttons')
            from workshop_buttons import register_workshop_buttons
            app=self.module.create_app(config);register_workshop_buttons(app);client=app.test_client()
            self.assertEqual(client.get('/_local/button-models').json['bindings'],{})
            self.assertIn('game-runtime.js',client.get('/login').text)
            for path in ('/button-editor/game-runtime.js','/button-editor/media-renderer.js','/button-editor/game-runtime.css','/shared/comic-button.css','/button-editor/matched-media.css'):
                with client.get(path) as response:self.assertEqual(response.status_code,200,path)
            usage=app.extensions['workshop_buttons']
            asset=next(a for a in usage.sources.assets() if a['label']=='spielen →' and a['game']=='Guesstimate')
            recipe=usage.recipes.save(usage.sources.recipe(asset['id'],storage.CATALOG))
            usage.update(dict(revision=None,recipe_id=recipe['id'],models=['approved-guesstimate-start-action']))
            self.assertEqual(client.get('/_local/button-models').json['bindings'],{'approved-guesstimate-start-action':recipe['id']})
            config.update(DATABASE=str(base/'disabled.sqlite3'),LOCAL_DEVELOPMENT=False)
            disabled_app=self.module.create_app(config);register_workshop_buttons(disabled_app);disabled=disabled_app.test_client()
            self.assertEqual(disabled.get('/_local/button-models').status_code,404)
            self.assertNotIn('game-runtime.js',disabled.get('/login').text)


if __name__=='__main__':unittest.main()

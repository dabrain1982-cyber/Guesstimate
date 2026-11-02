"""Source buttons retain their real markup/styles and cannot run game actions."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tempfile
from threading import Thread
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import ProxyHandler,build_opener

from tests.test_game_workshop import serve,TEST_ROOT
from tests.test_workshop_collections import empty_project,payload
from source_buttons import SourceButtons,ButtonParser
from workspace_store import ProjectLibrary
from button_bridge import storage
from library_store import InvalidDesign


class SourceButtonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.source=SourceButtons()

    def test_guesstimate_start_buttons_use_the_real_template_and_styles(self):
        original=(serve.ROOT/'templates/home.html').read_bytes()
        rows=[a for a in self.source.assets() if a['game']=='Guesstimate' and a['usage']=='Startseite']
        play=next(a for a in rows if a['label']=='spielen →')
        self.assertIn('class="primary-button"',play['snapshot']['markup'])
        self.assertIn(play['snapshot']['markup'],original.decode().replace('\r\n','\n'))
        self.assertEqual(play['snapshot']['source_sha256'],hashlib.sha256(original).hexdigest())
        page=self.source.preview(play['id'])
        self.assertIn('/shared/quiz-arena.css',page)
        self.assertIn('variant-a-action',page)
        self.assertIn('<body inert>',page)
        self.assertNotIn('<script',page)
        self.assertTrue(play['editable'])
        self.assertTrue(any('verpasste' in a['label'] for a in rows))
        self.assertEqual((serve.ROOT/'templates/home.html').read_bytes(),original)

    def test_every_registered_preview_is_built_and_unregistered_paths_fail(self):
        assets=self.source.assets()
        self.assertGreater(len(assets),100)
        self.assertEqual(len({a['id'] for a in assets}),len(assets))
        for asset in assets:
            self.assertIn('<!doctype html>',self.source.preview(asset['id']))
        with self.assertRaises(InvalidDesign):self.source.preview('../../app.py')

    def test_original_can_be_collected_twice_without_creating_a_button_copy(self):
        with tempfile.TemporaryDirectory(dir=TEST_ROOT) as directory:
            store=ProjectLibrary(Path(directory)/'library',Path(directory)/'buttons')
            asset=next(a for a in store.assets() if a.get('source')=='game' and a['game']=='Guesstimate' and a['label']=='spielen →')
            before=list(store.buttons_directory.glob('*.json'))
            p=empty_project('Erste Idee');p['items']=[dict(kind='buttons',id=asset['id'])]
            first=store.save_project(p)
            p=empty_project('Zweite Idee');p['items']=[dict(kind='buttons',id=asset['id'])]
            second=store.save_project(p)
            self.assertEqual(first['items'][0]['snapshot'],second['items'][0]['snapshot'])
            self.assertEqual(first['items'][0]['snapshot'],asset['snapshot'])
            self.assertEqual(list(store.buttons_directory.glob('*.json')),before)
            self.assertEqual(store.handoff(first['id'])['project']['items'][0]['snapshot'],asset['snapshot'])

    def test_shared_conquest_button_can_be_saved_as_a_new_editable_recipe(self):
        asset=next(a for a in self.source.assets() if a.get('canonical'))
        source=serve.ROOT/'offline-preview/conquest-2-5d-v1/button-profile.json';original=source.read_bytes()
        recipe=self.source.recipe(asset['id'],storage.CATALOG)
        with tempfile.TemporaryDirectory(dir=TEST_ROOT) as directory:
            saved=storage.RecipeStore(Path(directory)).save(recipe)
            self.assertEqual(saved['settings']['label'],asset['label'])
            self.assertEqual(saved['contour'],asset['snapshot']['recipe']['contour'])
        self.assertEqual(source.read_bytes(),original)
        not_bound=next(a for a in self.source.assets() if not a.get('canonical'))
        self.assertEqual(self.source.recipe(not_bound['id'],storage.CATALOG)['schema_version'],4)

    def test_http_preview_preserves_original_css_and_blocks_actions(self):
        with tempfile.TemporaryDirectory(dir=TEST_ROOT) as directory:
            server=serve.make_server(0,Path(directory)/'library',Path(directory)/'buttons')
            thread=Thread(target=server.serve_forever,daemon=True);thread.start()
            base='http://127.0.0.1:'+str(server.server_port);opener=build_opener(ProxyHandler({}))
            try:
                with opener.open(base+'/api/library',timeout=4) as response:data=json.load(response)
                self.assertEqual(len(data['kinds']),15)
                self.assertEqual(len(data['inventory_families']),19)
                source=next(a for a in data['assets'] if a.get('source')=='game' and a['game']=='Guesstimate' and a['label']=='spielen →')
                with opener.open(base+source['preview'],timeout=4) as response:
                    self.assertIn("form-action 'none'",response.headers['Content-Security-Policy'])
                    self.assertIn("script-src 'none'",response.headers['Content-Security-Policy'])
                    self.assertIn('spielen',response.read().decode())
                with opener.open(base+'/shared/quiz-arena.css',timeout=4) as response:
                    self.assertEqual(response.read(),(serve.ROOT/'static/quiz-arena.css').read_bytes())
                with self.assertRaises(HTTPError) as caught:opener.open(base+'/api/game-buttons/not-registered/preview',timeout=4)
                caught.exception.close()
            finally:server.shutdown();server.server_close();thread.join(3)

    def test_all_originals_open_as_editable_recipes_without_restyling(self):
        for asset in self.source.assets():
            with self.subTest(name=asset['name']):
                value=storage.validate_recipe(self.source.recipe(asset['id'],storage.CATALOG))
                if not asset['canonical']:
                    self.assertEqual(value['settings']['shape'],'custom')
                    self.assertEqual(value['source_button']['snapshot'],asset['snapshot'])
                    self.assertIn('contour',value)
                self.assertTrue(asset['editable'])

    def test_source_edits_survive_reopening_and_project_handoff_without_source_writes(self):
        asset=next(a for a in self.source.assets() if a['game']=='Guesstimate' and a['label']=='spielen →')
        protected=[serve.ROOT/asset['snapshot']['source']['path'],*[serve.ROOT/s['path'] for s in asset['snapshot']['styles']]]
        before={p:p.read_bytes() for p in protected}
        with tempfile.TemporaryDirectory(dir=TEST_ROOT) as directory:
            store=ProjectLibrary(Path(directory)/'library',Path(directory)/'buttons')
            value=self.source.recipe(asset['id'],storage.CATALOG)
            value['settings'].update(font_scale=130,accent='#aabbcc',label='Meine Spielidee');value['contour']['points'][0]['round']=20
            saved=store.button_store.save(value);loaded,bad=store.button_store.list()
            self.assertEqual(bad,0);self.assertEqual(loaded[0]['settings'],value['settings'])
            revised=deepcopy(loaded[0]);revised['parent_id']=saved['id'];revised['settings']['font_scale']=150
            newer=store.button_store.save(revised)
            self.assertNotEqual(saved['id'],newer['id'])
            self.assertEqual(json.loads((store.buttons_directory/(saved['id']+'.json')).read_text())['settings'],value['settings'])
            project=empty_project('Original gestalten');project['items']=[dict(kind='buttons',id=newer['id'])]
            saved_project=store.save_project(project)
            self.assertEqual(store.handoff(saved_project['id'])['project']['items'][0]['snapshot']['source_button']['id'],asset['id'])
        for path,raw in before.items():self.assertEqual(path.read_bytes(),raw)

    def test_source_recipes_reject_actions_stylesheet_injection_and_tampered_evidence(self):
        asset=next(a for a in self.source.assets() if not a['canonical'])
        original=dict(schema_version=3,kind='button',name=asset['name'][:80],notes='',parent_id=None,source_button=dict(id=asset['id'],name=asset['name'],snapshot=asset['snapshot']),appearance={})
        for property,value in [('onclick','alert(1)'),('background-image','url(https://example.org/x)'),('color','red;display:none'),('font-family','var(--remote)'),('position','fixed')]:
            recipe=deepcopy(original);recipe['appearance']={'root':{'style':{property:value}}}
            with self.subTest(property=property),self.assertRaises(storage.InvalidRecipe):storage.validate_recipe(recipe)
        recipe=deepcopy(original);recipe['source_button']['snapshot']['markup']='changed'
        with self.assertRaises(storage.InvalidRecipe):storage.validate_recipe(recipe)
        recipe=deepcopy(original);recipe['appearance']={'../../outside':{'style':{'color':'red'}}}
        with self.assertRaises(storage.InvalidRecipe):storage.validate_recipe(recipe)

    def test_model_groups_keep_variants_and_separate_different_styles(self):
        rows=self.source.assets();groups={}
        for row in rows:groups.setdefault(row['model_id'],[]).append(row)
        self.assertEqual(len(groups),85)
        self.assertEqual(sum(len(v) for v in groups.values()),144)
        conquest=[a for a in rows if a['canonical']]
        self.assertEqual(len({a['model_id'] for a in conquest}),1)
        guesstimate=[a for a in rows if a['game']=='Guesstimate']
        play=next(a for a in guesstimate if a['label']=='spielen →')
        result=next(a for a in guesstimate if a['label']=='heutiges ergebnis →')
        self.assertEqual(play['model_id'],result['model_id'])
        self.assertNotEqual(play['context_state'],result['context_state'])
        self.assertEqual(play['model_name'],'Guesstimate · Startseitenaktion')
        answers=[a for a in rows if a['label']=='antwort einloggen' and a['game'] in ('Guesstimate','Guesstimate Party')]
        self.assertEqual(len(answers),2)
        self.assertEqual(len({a['model_id'] for a in answers}),1)
        question=next(a for a in guesstimate if a['label']=='Beispielantwort')
        self.assertNotEqual(play['model_id'],question['model_id'])
        record=deepcopy(self.source.records[question['id']]);record['id']='gamebutton-'+'0'*22
        self.assertNotEqual(self.source.model_id(record),question['model_id'])

    def test_text_only_saved_variants_share_a_model_but_style_changes_do_not(self):
        with tempfile.TemporaryDirectory(dir=TEST_ROOT) as directory:
            library=ProjectLibrary(Path(directory)/'library',Path(directory)/'buttons')
            asset=next(a for a in library.assets() if a.get('source')=='game' and a['game']=='Guesstimate' and a['label']=='spielen →')
            value=self.source.recipe(asset['id'],storage.CATALOG)
            value['settings']['label']='Eigener Text'
            value=storage.validate_recipe(value)
            self.assertEqual(library.button_model(value),asset['model_id'])
            value['settings']['accent']='#ccbb00'
            self.assertNotEqual(library.button_model(value),asset['model_id'])

    def test_guesstimate_uses_shared_contour_recipe_with_independent_purple_depth(self):
        asset=next(a for a in self.source.assets() if a['game']=='Guesstimate' and a['label']=='weiter zu frage 2')
        recipe=self.source.recipe(asset['id'],storage.CATALOG)
        self.assertEqual(recipe['schema_version'],4)
        self.assertEqual((recipe['base']['width'],recipe['base']['height']),(430,50))
        self.assertEqual(recipe['settings']['material'],'plain')
        self.assertEqual(recipe['settings']['depth_color'],'#8e80ff')
        self.assertEqual(len(recipe['contour']['points']),4)
        recipe['contour']['points'].insert(1,dict(x=50,y=20,round=0))
        with tempfile.TemporaryDirectory(dir=TEST_ROOT) as directory:
            store=storage.RecipeStore(Path(directory));saved=store.save(recipe);loaded,bad=store.list()
            self.assertEqual(bad,0);self.assertEqual(loaded[0]['contour'],recipe['contour'])
            self.assertEqual(loaded[0]['base'],saved['base'])

    def test_saved_browser_capture_of_markup_only_source_keeps_library_and_reopening_available(self):
        from profile_recipe import from_profile
        with tempfile.TemporaryDirectory(dir=TEST_ROOT) as directory:
            server=serve.make_server(0,Path(directory)/'library',Path(directory)/'buttons')
            sources=server.library.source_buttons
            source=next(a for a in sources.assets() if not a['canonical'] and a['id'] not in sources.profiles)
            original=sources.recipe(source['id'],storage.CATALOG)
            self.assertEqual(original['schema_version'],3)
            measured=next(a for a in sources.assets() if a['game']=='Guesstimate' and a['label']=='spielen →')
            # The browser produces this full editable format after measuring
            # a source that only has original markup on the server.
            profile=deepcopy(sources.profiles[measured['id']]);profile['text']=source['label']
            value=from_profile(profile,original['source_button'],storage.CATALOG)
            value['settings'].update(font='letter-comic',depth=3)
            first=server.library.button_store.save(value)
            revised=deepcopy(first);revised['parent_id']=first['id'];revised['settings']['font_scale']=130
            second=server.library.button_store.save(revised)
            before={path:path.read_bytes() for path in server.library.buttons_directory.glob('*.json')}
            thread=Thread(target=server.serve_forever,daemon=True);thread.start()
            base='http://127.0.0.1:'+str(server.server_port);opener=build_opener(ProxyHandler({}))
            try:
                with opener.open(base+'/api/library',timeout=8) as response:data=json.load(response)
                for saved in (first,second):
                    asset=next(a for a in data['assets'] if a['id']==saved['id'])
                    self.assertEqual(asset['snapshot'],saved)
                    self.assertTrue(asset['model_id'].startswith(sources.model_id(sources.records[source['id']])))
                with opener.open(base+'/api/recipes',timeout=5) as response:recipes=json.load(response)
                self.assertEqual(recipes['unreadable'],0)
                self.assertEqual(next(r for r in recipes['recipes'] if r['id']==second['id']),second)
                self.assertEqual({path:path.read_bytes() for path in before},before)
            finally:server.shutdown();server.server_close();thread.join(3)

    def test_imported_components_reject_executable_graphics_and_external_images(self):
        asset=next(a for a in self.source.assets() if not a['canonical'])
        recipe=self.source.recipe(asset['id'],storage.CATALOG)
        for key,value in [('background','url(https://example.org/tracker)'),('font_family','Inter;display:none'),('svg','<svg><script>alert(1)</script></svg>')]:
            bad=deepcopy(recipe);bad['base'][key]=value
            with self.subTest(key=key),self.assertRaises(storage.InvalidRecipe):storage.validate_recipe(bad)

    def test_overview_wrappers_and_shared_controls_are_discovered_for_each_game(self):
        for template in ('party_index.html','nerd_index.html','card_table_index.html','dice_table_index.html','conquest_index.html'):
            self.assertIn(template,self.source.active_templates)
        create=next(a for a in self.source.assets() if a['label']=='lobby erstellen')
        for game in ('Playtable','Conquest','Perfect','Guesstimate Party','Würfeltisch','Kniffel','Mäxchen'):
            self.assertIn(game,create['games'])
        edit=next(a for a in self.source.assets() if a['label']=='Avatar, Pult und Hintergrund im Profil ändern')
        self.assertEqual(edit['games'],['Guesstimate'])

    def test_generated_factories_open_in_common_editor_with_source_evidence(self):
        generated=[r for r in self.source.records.values() if r.get('capture_key')]
        self.assertEqual(len(generated),4)
        self.assertEqual(self.source.generated_errors,[])
        for record in generated:
            recipe=storage.validate_recipe(self.source.recipe(record['id'],storage.CATALOG))
            self.assertEqual(recipe['schema_version'],4)
            self.assertTrue(record['snapshot']['evidence'])
            self.assertEqual(recipe['source_button']['snapshot'],record['snapshot'])
        held=next(r for r in generated if r['capture_key']=='dice-held')
        self.assertEqual(self.source.recipe(held['id'],storage.CATALOG)['base']['text'],'4')
        self.assertIn('dice-held-zone',self.source.preview(held['id']))

    def test_changed_factory_evidence_is_detected_instead_of_importing_old_captures(self):
        original=Path.read_bytes
        def changed(path):
            value=original(path)
            return value+b'/* changed factory */' if path.as_posix().endswith('/static/dice-table.js') else value
        with patch.object(Path,'read_bytes',changed):source=SourceButtons()
        self.assertEqual(set(source.generated_errors),{'dice-held','dice-tray','kniffel-score'})
        self.assertFalse(any(r.get('capture_key')=='dice-held' for r in source.records.values()))

    def test_kniffel_context_and_hidden_actions_are_only_changed_in_inert_preview(self):
        roll=next(r for r in self.source.records.values() if r['game']=='Kniffel' and 'würfel würfeln' in r['label'])
        self.assertIn('is-kniffel-console',self.source.preview(roll['id']))
        hidden=next(r for r in self.source.records.values() if r['attrs'].get('id')=='clear-selection')
        self.assertIn('hidden',hidden['attrs'])
        example=next(b for b in ButtonParser(self.source.preview(hidden['id'])).buttons if b['attrs'].get('id')=='clear-selection')
        self.assertNotIn('hidden',example['attrs'])
        self.assertIn('hidden',hidden['snapshot']['markup'])

    def test_connected_native_and_dynamic_button_sources_have_a_disposition(self):
        from deploy.audit_button_coverage import audit
        report=audit()
        self.assertEqual(report['missing'],[])
        self.assertEqual(report['stale_captures'],[])
        self.assertEqual(report['registered_uses'],144)
        self.assertTrue(any(r.get('capture_keys')==['kniffel-score'] for r in report['dynamic_factories']))
        self.assertTrue(any('Truppenmarke' in r['disposition'] for r in report['other_element_bindings']))

    def test_symbol_only_buttons_keep_accessibility_name_separate_from_visible_caption(self):
        icons=[a for a in self.source.assets() if a['label'].startswith('Mit ') and 'Angriffswürfel' in a['label']]
        self.assertEqual(len(icons),3)
        for asset in icons:
            value=storage.validate_recipe(self.source.recipe(asset['id'],storage.CATALOG))
            self.assertEqual(value['base']['label_visible'],0)
            self.assertTrue(value['base']['svg'])
            self.assertEqual(value['settings']['label'],asset['label'])


if __name__=='__main__':unittest.main()

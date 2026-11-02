"""Exercise durable append-only recipes and the actual local HTTP boundary."""
import copy
from http.client import HTTPConnection
import json
from pathlib import Path
import tempfile
import threading
import unittest

from serve import make_server
from storage import CATALOG, InvalidRecipe, RecipeStore, validate_recipe


def recipe():
    return dict(schema_version=2, name='Mein Schiefer', notes='Bewegung gut, Oberfläche offen.',
                settings=copy.deepcopy(CATALOG['defaults']),
                contour={'template':'cut','points':[dict(x=x,y=y,round=r) for x,y,r in CATALOG['contours']['cut']]},
                review={key: 'like' if key == 'motion' else 'open'
                        for key, _ in CATALOG['review_dimensions']}, parent_id=None)


class WorkshopTests(unittest.TestCase):
    def setUp(self):
        workspace_temp = Path(__file__).resolve().parents[2] / 'runtime/button-workshop-v1-tests'
        workspace_temp.mkdir(parents=True, exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(prefix='case-', dir=workspace_temp)
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.store = RecipeStore(self.directory)

    def test_saved_versions_survive_restart_without_overwriting(self):
        first = self.store.save(recipe())
        original = (self.directory / (first['id'] + '.json')).read_bytes()
        next_recipe = recipe()
        next_recipe['parent_id'] = first['id']
        next_recipe['settings']['finish'] = 'gloss'
        second = self.store.save(next_recipe)
        loaded, unreadable = RecipeStore(self.directory).list()
        self.assertEqual(unreadable, 0)
        self.assertEqual(len(loaded), 2)
        self.assertNotEqual(first['id'], second['id'])
        self.assertEqual(loaded[0]['parent_id'], first['id'])
        self.assertEqual(loaded[0]['notes'], next_recipe['notes'])
        self.assertEqual(loaded[0]['review']['motion'], 'like')
        self.assertEqual((self.directory / (first['id'] + '.json')).read_bytes(), original)

    def test_bad_imports_are_rejected_without_files(self):
        cases = [dict(schema_version=True), dict(name=''), dict(parent_id='../outside')]
        for change in cases:
            payload = recipe(); payload.update(change)
            with self.subTest(change=change), self.assertRaises(InvalidRecipe):
                self.store.save(payload)
        for key, value in [('depth', 100), ('size', True), ('duration', 900),
                           ('material', 'plastic'), ('accent', 'url(x)'), ('label', '')]:
            payload = recipe(); payload['settings'][key] = value
            with self.subTest(key=key), self.assertRaises(InvalidRecipe):
                self.store.save(payload)
        payload = recipe(); payload['review']['motion'] = []
        with self.assertRaises(InvalidRecipe): self.store.save(payload)
        self.assertEqual(list(self.directory.iterdir()), [])

    def test_unreadable_file_is_reported_and_preserved(self):
        good = self.store.save(recipe())
        bad = self.directory / ('a' * 32 + '.json')
        bad.write_text('{broken', encoding='utf-8')
        loaded, count = self.store.list()
        self.assertEqual([row['id'] for row in loaded], [good['id']])
        self.assertEqual(count, 1)
        self.assertEqual(bad.read_text(), '{broken')
        bad_data = dict(good, id='a' * 32, created_at=[])
        bad.write_text(json.dumps(bad_data), encoding='utf-8')
        self.assertEqual(self.store.list()[1], 1)

    def test_import_validation_preserves_settings_without_saving(self):
        payload = recipe(); payload['settings']['label'] = '<b>weiter</b>'
        normalized = validate_recipe(payload)
        self.assertEqual(normalized['settings'], payload['settings'])
        self.assertEqual(normalized['review'], payload['review'])
        self.assertEqual(list(self.directory.iterdir()), [])

    def test_old_recipe_loads_without_modifying_original_file(self):
        old=recipe();old['schema_version']=1;old.pop('contour');old['settings'].pop('style');old['settings'].pop('font_link');old['review'].pop('style')
        old.update(id='b'*32,created_at='2026-10-25T12:00:00+00:00')
        path=self.directory/(old['id']+'.json');path.write_text(json.dumps(old),encoding='utf-8');raw=path.read_bytes()
        rows,errors=self.store.list()
        self.assertEqual(errors,0);self.assertEqual(rows[0]['schema_version'],2)
        self.assertEqual(rows[0]['settings']['style'],'comic')
        self.assertEqual(rows[0]['settings']['font_link'],'manual')
        self.assertEqual(rows[0]['contour']['points'][0],{'x':7,'y':0,'round':0})
        self.assertEqual(rows[0]['review']['motion'],'like');self.assertEqual(rows[0]['review']['style'],'open')
        self.store.save(rows[0]);self.assertEqual(path.read_bytes(),raw)

    def test_version_two_without_font_link_preserves_chosen_font(self):
        data=recipe();data['settings'].pop('font_link');data['settings']['font']='fredoka'
        normalized=validate_recipe(data)
        self.assertEqual(normalized['settings']['font_link'],'manual')
        self.assertEqual(normalized['settings']['font'],'fredoka')

    def test_existing_version_two_without_new_surface_fields_is_preserved(self):
        data=recipe()
        for key in ('gradient_to','opacity','font_scale','shadow'):data['settings'].pop(key)
        data.update(id='c'*32,created_at='2026-10-25T12:00:00+00:00')
        path=self.directory/(data['id']+'.json');path.write_text(json.dumps(data),encoding='utf-8');raw=path.read_bytes()
        rows,errors=self.store.list()
        self.assertEqual(errors,0)
        for key,value in data['settings'].items():self.assertEqual(rows[0]['settings'][key],value)
        self.assertEqual(path.read_bytes(),raw)
        self.store.save(rows[0]);self.assertEqual(path.read_bytes(),raw)

    def test_game_surface_variants_roundtrip_and_reject_invalid_values(self):
        for material in ('plain','gradient','translucent'):
            data=recipe();data['settings'].update(material=material,gradient_to='#d9bc7e',opacity=0,font_scale=150,shadow=40)
            saved=self.store.save(data)
            row=next(r for r in self.store.list()[0] if r['id']==saved['id'])
            self.assertEqual(row['settings'],data['settings'])
        for key,value in [('opacity',-5),('opacity',105),('opacity',True),('gradient_to','url(x)'),('font_scale',165),('shadow',65)]:
            data=recipe();data['settings'][key]=value
            with self.subTest(key=key,value=value),self.assertRaises(InvalidRecipe):self.store.save(data)

    def test_shape_templates_are_distinct_append_only_records(self):
        data=recipe();data['kind']='shape';data['name']='Meine gezackte Form'
        first=self.store.save(data);raw=(self.directory/(first['id']+'.json')).read_bytes()
        data['parent_id']=first['id'];data['contour']['points'][0]['round']=17
        second=self.store.save(data);rows,errors=RecipeStore(self.directory).list()
        self.assertEqual(errors,0);self.assertEqual(len(rows),2)
        self.assertTrue(all(row['kind']=='shape' for row in rows))
        self.assertEqual(rows[0]['parent_id'],first['id'])
        self.assertNotEqual(first['id'],second['id'])
        self.assertEqual((self.directory/(first['id']+'.json')).read_bytes(),raw)

    def test_custom_rounded_contour_and_style_survive_restart(self):
        data=recipe();data['settings'].update(shape='custom',style='natural')
        data['contour']['points'][0].update(x=9.25,y=7.5,round=22)
        saved=self.store.save(data);loaded=RecipeStore(self.directory).list()[0][0]
        self.assertEqual(loaded['contour'],data['contour']);self.assertEqual(loaded['settings']['style'],'natural')
        self.assertEqual(saved['id'],loaded['id'])

    def test_crossed_degenerate_and_invalid_contours_do_not_save(self):
        bad_points=[
            [{'x':0,'y':0,'round':0},{'x':100,'y':100,'round':0},{'x':0,'y':100,'round':0},{'x':100,'y':0,'round':0}],
            [{'x':0,'y':0,'round':0},{'x':50,'y':0,'round':0},{'x':100,'y':0,'round':0}],
            [{'x':0,'y':0,'round':0},{'x':100,'y':0,'round':51},{'x':100,'y':100,'round':0}],
            [{'x':False,'y':0,'round':0},{'x':100,'y':0,'round':0},{'x':100,'y':100,'round':0}],
        ]
        for points in bad_points:
            data=recipe();data['contour']['points']=points
            with self.subTest(points=points),self.assertRaises(InvalidRecipe):self.store.save(data)
        self.assertEqual(list(self.directory.iterdir()),[])

    def test_http_save_reload_import_and_rejected_foreign_origin(self):
        server = make_server(0, self.directory)
        thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
        self.addCleanup(server.server_close); self.addCleanup(server.shutdown)
        port = server.server_port
        def call(path, data=None, origin=None):
            client = HTTPConnection('127.0.0.1', port, timeout=3)
            headers = {'Content-Type': 'application/json'}
            if origin: headers['Origin'] = origin
            client.request('GET' if data is None else 'POST', path,
                           None if data is None else json.dumps(data), headers)
            response = client.getresponse(); status = response.status; body = response.read()
            client.close()
            return status, body
        self.assertEqual(call('/api/recipes', recipe(), 'http://example.com')[0], 403)
        self.assertEqual(call('/api/validate', recipe())[0], 200)
        self.assertEqual(list(self.directory.iterdir()), [])
        status, body = call('/api/recipes', recipe(), f'http://127.0.0.1:{port}')
        self.assertEqual(status, 201)
        saved = json.loads(body)['recipe']
        status, body = call('/api/recipes')
        self.assertEqual(json.loads(body)['recipes'][0]['id'], saved['id'])
        self.assertEqual(call('/../../runtime/pc-local/quiz.sqlite3')[0], 404)
        self.assertEqual(call('/api/recipes', {'schema_version': 99})[0], 400)
        self.assertEqual(len(list(self.directory.glob('*.json'))), 1)


if __name__ == '__main__':
    unittest.main()

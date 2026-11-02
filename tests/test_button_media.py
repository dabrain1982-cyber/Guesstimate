"""Curated media is opt-in; legacy recipes, assets and game renderers stay exact."""
from copy import deepcopy
from hashlib import sha256
import importlib.util,json,sys
from pathlib import Path
import tempfile
from threading import Thread
import unittest
from urllib.request import build_opener,ProxyHandler
from tests.test_game_workshop import serve,TEST_ROOT
from tests.test_workshop_collections import empty_project
from button_bridge import storage
from media_selection import SELECTION,FILES,matched_css
from workspace_store import ProjectLibrary
from source_buttons import SourceButtons

ROOT=serve.ROOT


class ButtonMediaTests(unittest.TestCase):
    def test_catalog_adds_seven_fixed_styles_thirteen_sounds_without_replacing_old_choices(self):
        old=json.loads((ROOT/'offline-preview/button-workshop-v1/catalog.json').read_text(encoding='utf-8'))
        self.assertEqual(storage.CATALOG['defaults'],old['defaults'])
        self.assertEqual(len(SELECTION['fonts']),7);self.assertEqual(len(SELECTION['sounds']),13)
        self.assertEqual(len(storage.FIELDS),29)
        for key in ('font','sound'):
            before=next(f['options'] for f in old['fields'] if f['key']==key)
            after=storage.FIELDS[key]['options']
            self.assertEqual([r for r in after if not r[0].startswith(('media-','letter-'))],before)
        legacy=json.loads((ROOT/'offline-preview/button-workshop-v1/assets/audio/catalog.json').read_text(encoding='utf-8'))['sounds']
        self.assertEqual([r for r in storage.CATALOG['sounds'] if not r.get('media_short')],legacy)
        for row in SELECTION['sounds']:
            self.assertEqual(row['button_offset'],0)
            self.assertEqual(row['button_duration'],row['duration'])
            self.assertEqual(sha256(FILES['/assets/audio/'+row['file']].read_bytes()).hexdigest(),row['sha256'])

    def test_all_old_source_recipes_are_byte_equivalent_as_values(self):
        legacy=json.loads((ROOT/'offline-preview/button-workshop-v1/catalog.json').read_text(encoding='utf-8'))
        source=SourceButtons()
        before={a['id']:storage.validate_recipe(source.recipe(a['id'],legacy)) for a in source.assets()}
        after={a['id']:storage.validate_recipe(source.recipe(a['id'],storage.CATALOG)) for a in source.assets()}
        self.assertEqual(len(after),144);self.assertEqual(before,after)
        unchanged={
            'offline-preview/button-workshop-v1/renderer.js':'22854cb2f1aa07ab09ab7e500fb744402a5978d8aa188a1e4afc8887a43868ef',
            'offline-preview/button-workshop-v1/sound.js':'8499e1eec02c02315bf70f9d03e014589f008dfdb29e6dcaf60d766ccdc19187',
            'offline-preview/game-workshop-v1/media-stage.css':'bc910b54dcd31b1a359316d6e5d523ca7effee02ec6d2457aa6b65432b8a567c',
        }
        for path,digest in unchanged.items():
            self.assertEqual(sha256((ROOT/path).read_bytes()).hexdigest(),digest)

    def test_seven_styles_and_all_sounds_save_reopen_and_handoff_without_changing_base_or_old_file(self):
        with tempfile.TemporaryDirectory(dir=TEST_ROOT) as folder:
            store=ProjectLibrary(Path(folder)/'library',Path(folder)/'buttons')
            source=store.source_buttons
            asset=next(a for a in source.assets() if a['game']=='Guesstimate' and a['label']=='spielen →')
            original=source.recipe(asset['id'],storage.CATALOG)
            first=store.button_store.save(original);path=store.buttons_directory/(first['id']+'.json');before=path.read_bytes()
            saved=[]
            for i,font in enumerate(SELECTION['fonts']):
                value=deepcopy(original);value['parent_id']=first['id'];value['settings']['font']=font['value'];value['settings']['font_link']='manual'
                value['settings']['sound']=SELECTION['sounds'][i]['id'];value['name']=font['name']
                saved.append(store.button_store.save(value))
            for row in SELECTION['sounds']:
                value=deepcopy(original);value['settings']['sound']=row['id']
                self.assertEqual(storage.validate_recipe(value)['settings']['sound'],row['id'])
            again=ProjectLibrary(store.directory,store.buttons_directory)
            records,bad=again.button_store.list();self.assertEqual(bad,0)
            self.assertEqual(len(records),8)
            p=empty_project('Neue Medien');p['items']=[dict(kind='buttons',id=r['id']) for r in saved]
            project=again.save_project(p);handoff=again.handoff(project['id'])['project']
            self.assertEqual(handoff['items'],project['items'])
            for item,record in zip(handoff['items'],saved):
                self.assertEqual(item['snapshot'],record)
                self.assertEqual(item['snapshot']['base'],original['base'])
                for key in ('material','accent','lettering','depth','height_ratio','label'):
                    self.assertEqual(item['snapshot']['settings'][key],original['settings'][key])
            self.assertEqual(path.read_bytes(),before)

    def test_both_services_serve_same_styles_and_original_media_files(self):
        spec=importlib.util.spec_from_file_location('button_media_standalone',ROOT/'offline-preview/button-workshop-v1/serve.py')
        standalone=importlib.util.module_from_spec(spec)
        previous_path=sys.path[:]
        try:
            sys.path.insert(0,str(ROOT/'offline-preview/button-workshop-v1'))
            spec.loader.exec_module(standalone)
        finally:sys.path[:]=previous_path
        with tempfile.TemporaryDirectory(dir=TEST_ROOT) as folder:
            base=Path(folder)
            servers=[serve.make_server(0,base/'library',base/'buttons'),standalone.make_server(0,base/'standalone-buttons')]
            threads=[Thread(target=s.serve_forever,daemon=True) for s in servers]
            for thread in threads:thread.start()
            opener=build_opener(ProxyHandler({}))
            try:
                for index,server in enumerate(servers):
                    url='http://127.0.0.1:'+str(server.server_port)
                    with opener.open(url+'/api/catalog') as response:catalog=json.load(response)
                    self.assertEqual(catalog['button_media'],SELECTION)
                    css_path='/button-editor/matched-media.css' if index==0 else '/matched-media.css'
                    with opener.open(url+css_path) as response:
                        self.assertIn('text/css',response.headers['Content-Type']);css=response.read().decode('utf-8')
                    self.assertEqual(css,matched_css())
                    for row in SELECTION['fonts']:
                        self.assertIn('[data-media-font="'+row['style']+'"]',css)
                    self.assertIn('--button-face-font',css)
                    for path,file in FILES.items():
                        with opener.open(url+path) as response:self.assertEqual(response.read(),file.read_bytes())
            finally:
                for server in servers:server.shutdown();server.server_close()
                for thread in threads:thread.join(3)

    def test_independent_lettering_and_explicit_surface_edit_survive_reopening_and_handoff(self):
        with tempfile.TemporaryDirectory(dir=TEST_ROOT) as folder:
            store=ProjectLibrary(Path(folder)/'library',Path(folder)/'buttons')
            asset=next(a for a in store.source_buttons.assets() if a['game']=='Guesstimate' and a['label']=='spielen →')
            original=store.source_buttons.recipe(asset['id'],storage.CATALOG)
            first=store.button_store.save(original)
            first_path=store.buttons_directory/(first['id']+'.json');before=first_path.read_bytes()
            variants=[]
            for font in SELECTION['fonts']:
                value=deepcopy(original);value['parent_id']=first['id']
                value['settings'].update(font='letter-'+font['style'],font_link='manual',accent='#246b43',ink_mode='manual',ink_color='#fff2d4',depth_mode='manual',depth_color='#19382b',depth=8)
                value['base']['surface_mode']='custom'
                variants.append(store.button_store.save(value))
            again=ProjectLibrary(store.directory,store.buttons_directory)
            records,bad=again.button_store.list();self.assertEqual(bad,0)
            for row in variants:
                self.assertIn(row,records)
                self.assertEqual(row['settings']['accent'],'#246b43')
                self.assertEqual(row['settings']['ink_color'],'#fff2d4')
                self.assertEqual(row['base']['surface_mode'],'custom')
            p=empty_project('Getrennte Schriftfarben');p['items']=[dict(kind='buttons',id=r['id']) for r in variants]
            project=again.save_project(p)
            self.assertEqual(again.handoff(project['id'])['project']['items'],project['items'])
            self.assertEqual(first_path.read_bytes(),before)


if __name__=='__main__':unittest.main()

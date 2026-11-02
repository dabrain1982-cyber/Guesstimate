"""Project properties stay separate from asset snapshots, games and private drafts."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
from threading import Thread
import unittest
from urllib.error import HTTPError
from urllib.request import build_opener, ProxyHandler
from tests.test_game_workshop import serve, TEST_ROOT
from tests.test_workshop_collections import empty_project, payload
from workspace_store import ProjectLibrary
from library_store import InvalidDesign


class PropertyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory(dir=TEST_ROOT)
        cls.store=ProjectLibrary(Path(cls.temp.name)/'library',Path(cls.temp.name)/'buttons',serve.EXISTING_ASSETS)
        cls.assets=cls.store.assets()

    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()

    def test_source_bound_families_three_views_and_fixed_lettering_links(self):
        catalog=self.store.properties.catalog(self.assets)
        self.assertEqual(len(catalog['materials']),10)
        self.assertEqual([v['id'] for v in catalog['views']],['flat','depth','spatial'])
        self.assertEqual(len(serve.ELEMENT_KINDS),17)
        ids={a['id'] for a in self.assets}
        for material in catalog['materials']:
            self.assertTrue(material['evidence'])
            self.assertNotIn(material['id'],ids)
            for ref in material['lettering']:self.assertIn(ref,ids)
            if material['preview']['type']!='button':self.assertIn(material['preview']['id'],ids)
        for view in catalog['views']:self.assertIn(view['example'],ids)
        # The 2.5D example uses the same original spatial board, never a third board model.
        depth=next(a for a in self.assets if a['id']==catalog['views'][1]['example'])
        self.assertEqual(depth['representation'],'3d')

    def test_wishes_roundtrip_and_handoff_keep_exact_original_items_without_catalog_growth(self):
        p=empty_project('Material und Ansicht');p['items']=[dict(kind='board',id='boards-3d-conquest'),dict(kind='cards',id='cards-component-display')]
        p['surfaces']=['wood','cardstock'];p['presentation']['mode']='depth'
        before=[(a['kind'],a['id']) for a in self.assets]
        saved=self.store.save_project(p)
        original={a['id']:a for a in self.assets}
        self.assertEqual(saved['items'],[original[i['id']] for i in p['items']])
        self.assertEqual([m['id'] for m in saved['surfaces']],p['surfaces'])
        self.assertNotIn('preview',saved['surfaces'][0])
        again=ProjectLibrary(self.store.directory,self.store.buttons_directory,serve.EXISTING_ASSETS)
        self.assertEqual([(a['kind'],a['id']) for a in again.assets()],before)
        handoff=again.handoff(saved['id'])
        self.assertEqual(handoff['project']['surfaces'],saved['surfaces'])
        self.assertEqual(handoff['project']['items'],saved['items'])
        self.assertIn('Materialwünsche für das Projekt',handoff['brief'])
        self.assertIn('Holz',handoff['brief']);self.assertIn('Feste Ansicht mit räumlicher Wirkung',handoff['brief'])

    def test_old_maps_omit_new_field_and_old_clients_cannot_erase_existing_wishes(self):
        old=self.store.save_project(empty_project('Ohne Materialwunsch'))
        self.assertNotIn('surfaces',old)
        old_file=self.store.directory/'projects'/(old['id']+'.json');before=old_file.read_bytes()
        updated=payload(old);updated['surfaces']=['felt'];saved=self.store.save_project(updated)
        legacy_client=payload(saved)
        self.assertNotIn('surfaces',legacy_client)
        again=self.store.save_project(legacy_client)
        self.assertEqual(again['surfaces'],saved['surfaces'])
        cleared=self.store.save_project(dict(legacy_client,surfaces=[]))
        self.assertEqual(cleared['surfaces'],[])
        self.assertEqual(old_file.read_bytes(),before)

    def test_frozen_wishes_survive_later_definition_changes(self):
        p=empty_project('Stabile Materialwünsche');p['surfaces']=['metal']
        saved=self.store.save_project(p);original=deepcopy(self.store.properties.materials['metal'])
        try:
            self.store.properties.materials['metal']['name']='Später umbenannt'
            next_value=dict(payload(saved),surfaces=['metal'])
            again=self.store.save_project(next_value)
            self.assertEqual(again['surfaces'],saved['surfaces'])
        finally:self.store.properties.materials['metal']=original

    def test_unknown_duplicate_forged_wishes_and_changed_sources_rejected(self):
        for value in (['unknown'],['wood','wood'],[{'id':'wood','name':'Fremder Inhalt'}],None):
            p=empty_project('Ungültig');p['surfaces']=value
            with self.assertRaises(InvalidDesign):self.store.save_project(p)
        source=self.store.properties.materials['wood']['evidence'][0];original=source['sha256']
        try:
            source['sha256']='0'*64
            with self.assertRaises(InvalidDesign):self.store.save_project(dict(empty_project('Quelle geändert'),surfaces=['wood']))
        finally:source['sha256']=original
        p=self.store.save_project(empty_project('Unvollständige Datei'));p['surfaces']=[dict(id='wood')]
        with self.assertRaises(InvalidDesign):self.store.validate_saved_project(p)

    def test_properties_are_local_metadata_and_existing_element_catalog_unchanged(self):
        server=serve.make_server(0,self.store.directory,self.store.buttons_directory)
        thread=Thread(target=server.serve_forever,daemon=True);thread.start()
        opener=build_opener(ProxyHandler({}));base='http://127.0.0.1:'+str(server.server_port)
        try:
            with opener.open(base+'/api/library') as response:catalog=json.load(response)
            self.assertEqual(len(catalog['properties']['materials']),10)
            self.assertEqual(len(catalog['kinds']),17)
            self.assertEqual([a['id'] for a in catalog['assets']],[a['id'] for a in self.assets])
            for path in ('/properties.js','/properties.css'):
                with opener.open(base+path) as response:self.assertTrue(response.read())
            for path in ('/api/materials/wood/preview','/api/materials'):
                with self.assertRaises(HTTPError) as error:opener.open(base+path)
                self.assertEqual(error.exception.code,404);error.exception.close()
        finally:server.shutdown();server.server_close();thread.join(3)


if __name__=='__main__':unittest.main()

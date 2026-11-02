"""Piece family granularity, original composition, preservation and local routes."""
from copy import deepcopy
from pathlib import Path
import tempfile
from threading import Thread
import unittest
from urllib.error import HTTPError
from urllib.request import build_opener, ProxyHandler
from tests.test_game_workshop import serve, TEST_ROOT, project as legacy_project
from tests.test_workshop_collections import empty_project, payload
from piece_library import PieceLibrary, MODELS, COVERAGE, CONQUEST
from dice_library import fragment
from library_store import InvalidDesign, PRESETS
from workspace_store import ProjectLibrary


class PieceLibraryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.pieces=PieceLibrary()

    def test_existing_families_are_finite_equipment_not_instances(self):
        assets=self.pieces.assets()
        self.assertEqual(len(assets),7)
        self.assertEqual({a['model_id'] for a in assets},{'pieces-'+key+'-v1' for key in MODELS})
        self.assertEqual(len(COVERAGE),8)
        self.assertEqual([c['game'] for c in COVERAGE if c['model']],['Conquest'])
        self.assertEqual(sum(a['source']=='game' for a in assets),1)
        for a in assets:
            self.assertTrue({'role','color','count','size','state'}<=set(a['snapshot']['parameters']))
            self.assertNotIn('territories',a['snapshot'])
            self.assertFalse(a['editable'])
            self.assertEqual(a['snapshot']['editor_review'],'deferred')
        for c in COVERAGE:self.assertTrue((CONQUEST.parents[1]/c['source']).is_file())
        assets[-1]['snapshot']['settings']['count']=2000
        self.assertEqual(self.pieces.assets()[-1]['snapshot']['settings']['count'],8)

    def test_original_counter_parts_and_projection_without_game_handlers(self):
        source=(CONQUEST/'territories.js').read_text(encoding='utf-8');factory=self.pieces.conquest_factory()
        for start,end in [('  const baseGeometry =','  function select(id)'),
                          ('    const counter =',"    button.addEventListener('click'"),
                          ('        projected.copy(anchor).project(camera);','\n      }\n      arrowSvg.setAttribute')]:
            self.assertIn(fragment(source,start,end),factory)
        for forbidden in ('createTurnControls','createRemoteTurn','fetch(','addEventListener','world.continents','buildPreviewTerritories'):
            self.assertNotIn(forbidden,factory)
        asset=self.pieces.records['pieces-conquest'];before=deepcopy(asset['snapshot'])
        try:
            asset['snapshot']['evidence'][0]['sha256']='0'*64
            with self.assertRaises(InvalidDesign):self.pieces.preview('pieces-conquest')
        finally:asset['snapshot']=before

    def test_collection_reuse_legacy_and_private_snapshots_remain_exact(self):
        with tempfile.TemporaryDirectory(dir=TEST_ROOT) as folder:
            store=ProjectLibrary(Path(folder)/'library',Path(folder)/'buttons')
            p=empty_project('Spielsteine');p['items']=[dict(kind='pieces',id=key) for key in ('pieces-conquest','pieces-preset-2-3d','pieces-preset-3-2d')]
            saved=store.save_project(p)
            second=empty_project('Wiederverwenden');second['items']=p['items']
            self.assertEqual(store.save_project(second)['items'],saved['items'])
            reopened=ProjectLibrary(store.directory,store.buttons_directory)
            self.assertEqual(reopened.handoff(saved['id'])['project']['items'],saved['items'])
            old=store.save_project(legacy_project());view=store.project_view(old)
            original=deepcopy(next(a for a in view['items'] if a['kind']=='pieces'))
            self.assertEqual(next(a for a in store.save_project(payload(view))['items'] if a['kind']=='pieces'),original)
            draft=store.save_element(dict(kind='pieces',name='Eigener alter Satz',settings=deepcopy(next(p['settings'] for p in PRESETS if p['kind']=='pieces'))))
            path=store.directory/'elements'/(draft['id']+'.json');before=path.read_bytes()
            asset=next(a for a in store.assets() if a['id']==draft['id'])
            self.assertEqual(asset['model_id'],'pieces-chess-v1');self.assertEqual(asset['snapshot'],draft)
            self.assertEqual(path.read_bytes(),before)

    def test_http_preview_factory_and_local_boundary(self):
        with tempfile.TemporaryDirectory(dir=TEST_ROOT) as folder:
            server=serve.make_server(0,Path(folder)/'library',Path(folder)/'buttons');thread=Thread(target=server.serve_forever,daemon=True);thread.start()
            opener=build_opener(ProxyHandler({}));base='http://127.0.0.1:'+str(server.server_port)
            try:
                for path in ('/api/pieces/pieces-conquest/preview?interactive=1','/api/pieces/pieces-preset-2-2d/preview','/piece-components/stage.js','/piece-source/conquest.js','/piece-source/territory-model.js','/piece-source/style.css'):
                    with opener.open(base+path) as response:
                        self.assertEqual(response.status,200)
                        if path.startswith('/api/'):
                            self.assertIn("connect-src 'self'",response.headers['Content-Security-Policy'])
                for path in ('/api/pieces/land-123/preview','/piece-source/../../PROJEKTLOG.md'):
                    with self.assertRaises(HTTPError) as error:opener.open(base+path)
                    self.assertIn(error.exception.code,(400,404));error.exception.close()
            finally:server.shutdown();server.server_close();thread.join(3)


if __name__=='__main__':unittest.main()

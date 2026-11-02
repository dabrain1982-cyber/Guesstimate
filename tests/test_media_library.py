"""Free matched lettering, playable short cues, local sources and project reuse."""
from copy import deepcopy
from pathlib import Path
import tempfile,wave
from threading import Thread
import unittest
from urllib.error import HTTPError
from urllib.request import build_opener,ProxyHandler
from PIL import ImageFont
from tests.test_game_workshop import serve, TEST_ROOT
from tests.test_workshop_collections import empty_project
from media_library import MediaLibrary,ASSETS
from library_store import ROOT,InvalidDesign
from workspace_store import ProjectLibrary


class MediaLibraryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.media=MediaLibrary()

    def test_lettering_is_seven_matched_styles_with_local_free_fonts_and_german_glyphs(self):
        fonts=[a for a in self.media.assets() if a['kind']=='fonts']
        self.assertEqual(len(fonts),7)
        self.assertEqual({a['family'] for a in fonts},{'chalk','stone','iron','stamp','hand','comic','clear'})
        for a in fonts:
            snap=a['snapshot'];self.assertTrue(snap['matched_style']);self.assertFalse(snap['game_integration'])
            self.assertIn(snap['provenance']['license'],('OFL-1.1','Apache-2.0'))
            self.assertTrue((ROOT/snap['provenance']['license_file']).is_file())
            font=ImageFont.truetype(str(ASSETS/'fonts'/snap['settings']['font_key']/'font.ttf'),48)
            missing=bytes(font.getmask(chr(0x10ffff)))
            self.assertTrue(all(bytes(font.getmask(c))!=missing for c in 'ÄÖÜäöüß0123456789'))
            self.assertEqual(snap['editor_review'],'deferred')

    def test_short_sound_cues_are_cc0_valid_wav_and_bound_to_originals(self):
        sounds=[a for a in self.media.assets() if a['kind']=='sounds']
        self.assertEqual(len(sounds),13);self.assertEqual({a['family'] for a in sounds},{'ui','table','result'})
        self.assertTrue({'media-sound-win','media-sound-lose','media-sound-click'}<=set(a['id'] for a in sounds))
        for a in sounds:
            s=a['snapshot'];self.assertEqual(s['provenance']['license'],'CC0-1.0')
            with wave.open(str(self.media.file_path(s['settings']['url']))) as decoded:
                self.assertEqual(decoded.getnchannels(),1);self.assertEqual(decoded.getsampwidth(),2)
                self.assertAlmostEqual(decoded.getnframes()/decoded.getframerate(),s['settings']['duration'],places=3)
                self.assertLess(s['settings']['duration'],4)
        row=self.media.records['media-sound-win'];before=deepcopy(row['snapshot'])
        try:
            row['snapshot']['evidence'][0]['sha256']='0'*64
            with self.assertRaises(InvalidDesign):self.media.preview(row['id'])
        finally:row['snapshot']=before

    def test_resources_reuse_reopen_and_handoff_as_exact_snapshots(self):
        with tempfile.TemporaryDirectory(dir=TEST_ROOT) as folder:
            store=ProjectLibrary(Path(folder)/'library',Path(folder)/'buttons')
            p=empty_project('Schrift und Klang');p['items']=[dict(kind=k,id=i) for k,i in [('fonts','media-lettering-chalk'),('fonts','media-lettering-iron'),('sounds','media-sound-win')]]
            saved=store.save_project(p);other=empty_project('Wiederverwenden');other['items']=p['items']
            self.assertEqual(store.save_project(other)['items'],saved['items'])
            again=ProjectLibrary(store.directory,store.buttons_directory)
            self.assertEqual(again.handoff(saved['id'])['project']['items'],saved['items'])
            self.assertEqual([a for a in store.assets() if a['kind']=='fonts'][0]['snapshot']['settings']['style'],'chalk')

    def test_local_routes_no_remote_font_loading_or_autoplay(self):
        with tempfile.TemporaryDirectory(dir=TEST_ROOT) as folder:
            server=serve.make_server(0,Path(folder)/'library',Path(folder)/'buttons');thread=Thread(target=server.serve_forever,daemon=True);thread.start()
            opener=build_opener(ProxyHandler({}));base='http://127.0.0.1:'+str(server.server_port)
            try:
                for path in ('/api/media/media-lettering-chalk/preview','/api/media/media-sound-win/preview?interactive=1','/media-assets/fonts/cabinsketch/font.ttf','/media-assets/sounds/win.wav','/media-components/stage.js'):
                    with opener.open(base+path) as response:
                        self.assertEqual(response.status,200)
                        if path.startswith('/api/'):
                            self.assertIn("font-src 'self'",response.headers['Content-Security-Policy'])
                            body=response.read().decode('utf-8');self.assertNotIn('autoplay',body);self.assertNotIn('fonts.googleapis',body)
                for path in ('/api/media/unknown/preview','/media-assets/../../PROJEKTLOG.md'):
                    with self.assertRaises(HTTPError) as error:opener.open(base+path)
                    self.assertIn(error.exception.code,(400,404));error.exception.close()
            finally:server.shutdown();server.server_close();thread.join(3)


if __name__=='__main__':unittest.main()

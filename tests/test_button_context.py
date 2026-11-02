"""A usage preview shows a marked control inside its original, inert game page."""
from pathlib import Path
import importlib.util
import re
import sys
import tempfile
from threading import Thread
import unittest
from urllib.request import build_opener, ProxyHandler
from urllib.error import HTTPError

from tests.test_game_workshop import serve, TEST_ROOT
from button_bridge import storage
from button_usage import ButtonUsage
from button_context import ButtonContext
from source_buttons import SourceButtons


class ButtonContextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(dir=TEST_ROOT)
        cls.sources = SourceButtons()
        cls.usage = ButtonUsage(Path(cls.temp.name), storage.RecipeStore(Path(cls.temp.name)/'buttons'), cls.sources)
        cls.view = ButtonContext(cls.usage)

    @classmethod
    def tearDownClass(cls): cls.temp.cleanup()

    def test_each_available_use_can_be_rendered_with_its_target_and_original_page_styles(self):
        for row in self.usage.models.values():
            if not row['supported']: continue
            for use in row['uses']:
                with self.subTest(use=use['id']):
                    page = self.view.render(use['id'])
                    self.assertIn('data-usage-target="true"', page)
                    self.assertRegex(page, r'<link[^>]*href="/shared/[^"?]+\.css')
                    self.assertIn('/button-context.js', page)
                    scripts = re.findall(r'<script\b[^>]*src="([^"]+)"', page)
                    self.assertEqual(scripts, ['/button-context.js'])
                    self.assertNotIn('csrf_token', page)
                    self.assertNotRegex(page, r'\s(?:on\w+|action|formaction)="')

    def test_linked_states_keep_their_distinct_real_home_context_and_original_files(self):
        path = serve.ROOT/'templates/home.html'; before = path.read_bytes()
        uses = self.usage.models['approved-guesstimate-start-action']['uses']
        for use in uses:
            page = self.view.render(use['id'])
            self.assertIn('variant-a-showcase', page)
            self.assertIn('variant-a-ranking', page)
            self.assertIn('profile-window', page)
            expected = 'heutiges ergebnis' if 'abgeschlossen' in use['state'] else 'spielen'
            self.assertRegex(page, r'<(?:button|a)[^>]*data-usage-target="true"[^>]*>'+expected)
            self.assertNotIn('showModal()', page)
        self.assertEqual(before, path.read_bytes())

    def test_unknown_and_unconnected_uses_fail_explicitly(self):
        for identifier in ('../../app.py', 'gamebutton-unknown', next(u['id'] for r in self.usage.models.values() if not r['supported'] for u in r['uses'])):
            with self.assertRaises(ValueError): self.view.render(identifier)

    def test_both_editor_services_provide_context_and_block_actions(self):
        sys.path.insert(0,str(serve.ROOT/'offline-preview/button-workshop-v1'))
        spec=importlib.util.spec_from_file_location('context_standalone',serve.ROOT/'offline-preview/button-workshop-v1/serve.py')
        standalone=importlib.util.module_from_spec(spec);spec.loader.exec_module(standalone)
        with tempfile.TemporaryDirectory(dir=TEST_ROOT) as directory:
            base=Path(directory)
            servers=[serve.make_server(0,base/'library',base/'buttons'),standalone.make_server(0,base/'standalone')]
            opener=build_opener(ProxyHandler({}))
            try:
                for server in servers:
                    Thread(target=server.serve_forever,daemon=True).start()
                    root=f'http://127.0.0.1:{server.server_port}'
                    use=self.usage.models['approved-guesstimate-start-action']['uses'][0]
                    with opener.open(root+use['context_preview']) as response:
                        self.assertIn('form-action \'none\'',response.headers['Content-Security-Policy'])
                        self.assertIn('data-usage-target',response.read().decode())
                    for name in ('button-context.js','button-context.css'):
                        with opener.open(root+'/'+name) as response:self.assertEqual(response.status,200)
                    with self.assertRaises(HTTPError) as caught:opener.open(root+'/api/button-usage/unknown/context')
                    with caught.exception as response:
                        self.assertEqual(response.code,400)
                        self.assertIn('/button-context.js',response.read().decode())
            finally:
                for server in servers:server.shutdown();server.server_close()


if __name__=='__main__':unittest.main()

import threading
import unittest
import urllib.error
import urllib.request
from serve import FILES, make_server


class ReadOnlyBoardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = make_server(0)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = 'http://127.0.0.1:' + str(cls.server.server_port)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def test_all_allowlisted_assets_exist_and_are_reachable(self):
        for route, path in FILES.items():
            with self.subTest(route=route):
                self.assertTrue(path.is_file(), path)
                with urllib.request.urlopen(self.base + route) as response:
                    self.assertEqual(response.status, 200)
                    self.assertGreater(len(response.read()), 0)
                    self.assertEqual(response.headers['Cache-Control'], 'no-store')

    def test_private_files_traversal_and_save_routes_are_unreachable(self):
        for path in ('/runtime/pc-local/quiz.sqlite3', '/profile/../serve.py', '/%2e%2e/AGENTS.md', '/api/recipes', '/serve.py'):
            with self.subTest(path=path), self.assertRaises(urllib.error.HTTPError) as error:
                urllib.request.urlopen(self.base + path)
            self.assertEqual(error.exception.code, 404)
        request = urllib.request.Request(self.base + '/', data=b'{}', method='POST')
        with self.assertRaises(urllib.error.HTTPError) as error:
            urllib.request.urlopen(request)
        self.assertEqual(error.exception.code, 405)


if __name__ == '__main__':
    unittest.main()

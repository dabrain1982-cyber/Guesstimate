"""Integration checks for the 1.01.01 release and permanent question history."""
import json
from pathlib import Path
import tempfile
import unittest
from app import create_app, question_fingerprint, question_pool_status, reserve_question_sets, QuestionPoolExhausted
from questions import QUESTION_BANK
from release_info import PUBLIC_VERSION

ROOT = Path(__file__).resolve().parents[1]

class ReleaseRefillTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.app = create_app(dict(TESTING=True, SECRET_KEY='disposable-release-test',
            DATABASE=str(Path(self.directory.name) / 'test.sqlite3'),
            APPLICATION_ROOT='/guesstimate', PUBLIC_URL='https://example.test/guesstimate'))

    def test_authenticated_date_badge_title_and_health_agree(self):
        with self.app.app_context():
            db = self.app.get_db()
            uid = db.execute("INSERT INTO users(username,display_name,pin_hash,created_at) VALUES('release-test','Release-Test','not-a-login','2026-11-02')").lastrowid
            db.commit()
        client = self.app.test_client()
        with client.session_transaction() as session:
            session['user_id'] = uid
            session['show_catchup_prompt'] = False
        response = client.get('/')
        text = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('data-release-version>V ' + PUBLIC_VERSION, text)
        self.assertIn(' · V ' + PUBLIC_VERSION + '</title>', text)
        self.assertEqual(text.count('data-release-version'), 1)
        self.assertIn('/guesstimate/static/quiz-arena.css?v=73', text)
        self.assertEqual(client.get('/health').get_json()['release'], PUBLIC_VERSION)

    def test_refill_gives_fifty_new_rounds_without_recycling_history(self):
        plan = json.loads((ROOT / 'deploy/question-refill-20261024/import-plan.json').read_text())
        candidates = {question['id'] for entry in plan['files']
            for question in json.loads((ROOT / 'deploy/question-refill-20261024' / entry['payload']).read_text())}
        self.assertEqual(len(candidates), 250)
        with self.app.app_context():
            db = self.app.get_db()
            originals = [(q['id'], question_fingerprint(q,kind),kind,'test','historic-original','2026-10-24')
                for kind, bank in QUESTION_BANK.items() for q in bank if q['id'] not in candidates]
            db.executemany('INSERT INTO question_usage(question_id,content_hash,category,source_type,source_id,used_at) VALUES(?,?,?,?,?,?)', originals)
            db.commit()
            history = [tuple(row) for row in db.execute("SELECT * FROM question_usage WHERE source_id='historic-original' ORDER BY rowid")]
            self.assertEqual(len(history), 1343)
            self.assertEqual(question_pool_status()['complete_rounds'], 50)
            selected = []
            for number in range(50):
                selected.extend(q['id'] for q in reserve_question_sets('test','refill-' + str(number))[0])
            self.assertEqual(len(set(selected)), 250)
            self.assertEqual(set(selected), candidates)
            self.assertEqual([tuple(row) for row in db.execute("SELECT * FROM question_usage WHERE source_id='historic-original' ORDER BY rowid")], history)
            self.assertEqual(question_pool_status()['complete_rounds'], 0)
            with self.assertRaises(QuestionPoolExhausted):
                reserve_question_sets('test','no-recycle')
            self.assertEqual(db.execute('SELECT COUNT(*) FROM question_usage').fetchone()[0], 1593)

"""The reopening exception is limited to one week and rejects stale sessions."""
from datetime import date
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from app import active_round_date, create_app, missed_current_week_dates
from flask import session


class CatchupExceptionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.app = create_app(dict(TESTING=True, SECRET_KEY='catchup-test',
                                   DATABASE=str(Path(self.tmp.name)/'test.sqlite3')))

    def tearDown(self):
        self.tmp.cleanup()

    def test_reopening_sunday_has_no_catchup_days(self):
        with self.app.app_context():
            self.assertEqual(missed_current_week_dates(1, date(2026,11,1)), [])

    def test_following_week_resumes_normally_and_never_includes_excluded_week(self):
        with self.app.app_context():
            self.assertEqual(missed_current_week_dates(1, date(2026,11,2)), [])
            self.assertEqual(missed_current_week_dates(1, date(2026,11,4)),
                             ['2026-11-02','2026-11-03'])
            self.assertEqual(len(missed_current_week_dates(1,date(2026,11,8))),6)

    def test_stale_round_session_cannot_play_excluded_days_through_direct_routes(self):
        with self.app.test_request_context('/runde'), patch('app.today_iso',return_value='2026-11-01'):
            session.update(active_round_date='2026-10-28',catchup_queue=['2026-10-28','2026-11-01'])
            self.assertEqual(active_round_date(),'2026-11-01')
            self.assertNotIn('active_round_date',session)
            self.assertNotIn('catchup_queue',session)
            session['active_round_date']='2026-11-01'
            self.assertEqual(active_round_date(),'2026-11-01')


if __name__ == '__main__':
    unittest.main()

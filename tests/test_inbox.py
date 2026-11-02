"""Recipient boundaries, individual reading, persistent notification dismissal."""
from datetime import date
from pathlib import Path
import tempfile
import unittest

from app import create_app


class InboxTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.app = create_app(dict(TESTING=True, SECRET_KEY='inbox-test',
                                   DATABASE=str(Path(self.tmp.name) / 'mail.sqlite3')))
        with self.app.app_context():
            db = self.app.get_db()
            for login, name in [('stormseed', 'Stormseed'), ('mira', 'Mira'), ('jan', 'Jan')]:
                db.execute('INSERT INTO users(username,display_name,pin_hash,created_at) VALUES(?,?,?,?)',
                           (login, name, 'test-only', '2026-11-01'))
            db.commit()
        self.client = self.as_user(1)

    def tearDown(self):
        self.tmp.cleanup()

    def as_user(self, user_id):
        client = self.app.test_client()
        with client.session_transaction() as session:
            session.update(user_id=user_id, csrf_token='test-token', login_recorded_on=date.today().isoformat())
        return client

    def send(self, client=None, **data):
        return (client or self.client).post('/mail/senden', data=dict(
            csrf_token='test-token', subject='Ein Zettel', body='Hallo!\nViele Grüße', **data))

    def rows(self, table):
        with self.app.app_context():
            return [dict(r) for r in self.app.get_db().execute(f'SELECT * FROM {table}')]

    def test_authentication_and_csrf_protect_every_mutation(self):
        guest = self.app.test_client()
        for url in ('/mail', '/mail/status'):
            self.assertEqual(guest.get(url).status_code, 302)
        for url in ('/mail/senden', '/mail/oeffnen', '/mail/1/lesen'):
            self.assertEqual(self.client.post(url).status_code, 400)
        self.assertEqual(self.rows('inbox_messages'), [])

    def test_player_can_only_send_to_owner_even_with_forged_recipient(self):
        player = self.as_user(2)
        for recipient in ('all', '3', 'not-an-id'):
            self.assertEqual(self.send(player, recipient=recipient).status_code, 403)
        self.assertEqual(self.send(player, recipient='1').status_code, 303)
        self.assertEqual(self.rows('inbox_messages')[0]['sender_id'], 2)
        self.assertEqual([r['user_id'] for r in self.rows('inbox_deliveries')], [1])
        html = player.get('/mail').get_data(as_text=True)
        self.assertIn('An <strong>Stormseed</strong>', html)
        self.assertNotIn('id="mail-recipient"', html)

    def test_owner_single_recipient_is_private_and_sender_keeps_a_copy(self):
        self.assertEqual(self.send(recipient='2').status_code, 303)
        self.assertEqual([r['user_id'] for r in self.rows('inbox_deliveries')], [2])
        self.assertEqual(self.as_user(2).get('/mail?note=1').status_code, 200)
        self.assertEqual(self.as_user(3).get('/mail?note=1').status_code, 404)
        self.assertEqual(self.as_user(3).post('/mail/1/lesen', data={'csrf_token':'test-token'}).status_code, 404)
        self.assertIn('Ein Zettel', self.client.get('/mail?folder=sent&note=1').get_data(as_text=True))

    def test_broadcast_read_status_is_individual(self):
        self.assertEqual(self.send(recipient='all').status_code, 303)
        self.assertEqual(sorted(r['user_id'] for r in self.rows('inbox_deliveries')), [1, 2, 3])
        mira, jan = self.as_user(2), self.as_user(3)
        self.assertEqual(mira.get('/mail/status').json['unread'], 1)
        response = mira.post('/mail/1/lesen', data={'csrf_token':'test-token'}, follow_redirects=True)
        self.assertIn('Hallo!\nViele Grüße', response.get_data(as_text=True))
        self.assertEqual(mira.get('/mail/status').json['unread'], 0)
        self.assertEqual(jan.get('/mail/status').json['unread'], 1)
        before = next(r['read_at'] for r in self.rows('inbox_deliveries') if r['user_id'] == 2)
        mira.post('/mail/1/lesen', data={'csrf_token':'test-token'})
        self.assertEqual(next(r['read_at'] for r in self.rows('inbox_deliveries') if r['user_id'] == 2), before)

    def test_click_stops_attention_across_sessions_but_does_not_mark_read(self):
        self.send(recipient='2')
        mira = self.as_user(2)
        self.assertTrue(mira.get('/mail/status').json['attention'])
        mira.post('/mail/oeffnen', data={'csrf_token':'test-token', 'through':'1'})
        self.assertEqual(self.as_user(2).get('/mail/status').json,
                         dict(unread=1, latest=1, attention=False))
        self.send(recipient='2')
        self.assertTrue(mira.get('/mail/status').json['attention'])

    def test_stale_click_does_not_dismiss_newer_message(self):
        self.send(recipient='2')
        self.send(recipient='2')
        mira = self.as_user(2)
        mira.post('/mail/oeffnen', data={'csrf_token':'test-token', 'through':'1'})
        self.assertTrue(mira.get('/mail/status').json['attention'])
        mira.post('/mail/oeffnen', data={'csrf_token':'test-token', 'through':'2'})
        mira.post('/mail/oeffnen', data={'csrf_token':'test-token', 'through':'1'})
        self.assertFalse(mira.get('/mail/status').json['attention'])

    def test_get_list_and_status_do_not_change_read_or_attention(self):
        self.send(recipient='2')
        mira = self.as_user(2)
        before = (self.rows('inbox_deliveries'), self.rows('inbox_attention'))
        response = mira.get('/mail')
        mira.get('/mail/status')
        self.assertEqual(before, (self.rows('inbox_deliveries'), self.rows('inbox_attention')))
        self.assertEqual(response.headers['Cache-Control'], 'private, no-store')
        self.assertEqual(response.headers['X-Robots-Tag'], 'noindex, nofollow')

    def test_invalid_payload_keeps_text_and_does_not_create_partial_message(self):
        for recipient in ('', '1', '999', 'not-an-id'):
            self.assertEqual(self.send(recipient=recipient).status_code, 400)
        response = self.client.post('/mail/senden', data=dict(csrf_token='test-token',
            recipient='2', subject='Bitte behalten', body='x'*12001))
        self.assertEqual(response.status_code, 400)
        self.assertIn('Bitte behalten', response.get_data(as_text=True))
        self.assertEqual(self.rows('inbox_messages'), [])
        self.assertEqual(self.rows('inbox_deliveries'), [])

    def test_note_content_is_escaped_and_line_breaks_preserved(self):
        self.client.post('/mail/senden', data=dict(csrf_token='test-token', recipient='2',
            subject='<script>alarm()</script>', body='<img src=x onerror=alarm()>\nZweite Zeile'))
        html = self.as_user(2).post('/mail/1/lesen', data={'csrf_token':'test-token'},
                                   follow_redirects=True).get_data(as_text=True)
        self.assertIn('&lt;script&gt;alarm()&lt;/script&gt;', html)
        self.assertIn('&lt;img src=x onerror=alarm()&gt;\nZweite Zeile', html)
        self.assertNotIn('<script>alarm()', html)

    def test_url_prefix_is_preserved_by_mail_routes_and_form_actions(self):
        client = self.as_user(2)
        response = client.get('/mail', environ_overrides={'SCRIPT_NAME':'/guesstimate'})
        self.assertIn('action="/guesstimate/mail/senden"', response.get_data(as_text=True))
        self.assertIn('data-status-url="/guesstimate/mail/status"', response.get_data(as_text=True))

    def test_workshop_button_integration_can_render_mail_with_a_saved_note(self):
        from workshop_buttons import register_workshop_buttons
        self.app.config['LOCAL_DEVELOPMENT'] = True
        register_workshop_buttons(self.app)
        self.send(recipient='2')
        response = self.as_user(2).post('/mail/1/lesen',
            data={'csrf_token':'test-token'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Hallo!\nViele Grüße', response.get_data(as_text=True))


    def test_owner_receives_broadcast_unread_with_own_attention(self):
        self.assertEqual(self.send(recipient='all').status_code,303)
        self.assertEqual(self.client.get('/mail/status').json,dict(unread=1,latest=1,attention=True))
        sent=self.client.get('/mail?folder=sent&note=1')
        self.assertIn('Ein Zettel',sent.get_data(as_text=True))
        self.assertEqual(self.client.get('/mail/status').json['unread'],1)
        self.client.post('/mail/oeffnen',data={'csrf_token':'test-token','through':'1'})
        self.assertEqual(self.client.get('/mail/status').json,dict(unread=1,latest=1,attention=False))
        self.client.post('/mail/1/lesen',data={'csrf_token':'test-token'})
        self.assertEqual(self.client.get('/mail/status').json['unread'],0)
        self.assertEqual(self.as_user(2).get('/mail/status').json['unread'],1)

    def test_broadcast_also_works_when_owner_is_the_only_account(self):
        with self.app.app_context():
            db=self.app.get_db()
            db.execute('DELETE FROM users WHERE id != 1')
            db.commit()
        self.assertEqual(self.send(recipient='all').status_code,303)
        self.assertEqual([r['user_id'] for r in self.rows('inbox_deliveries')],[1])

    def test_latest_old_broadcast_gets_one_sender_copy_without_changing_others(self):
        from inbox import add_latest_broadcast_sender_copy
        self.send(recipient='all')
        self.send(recipient='all')
        with self.app.app_context():
            db=self.app.get_db()
            db.execute('DELETE FROM inbox_deliveries WHERE user_id=1')
            db.execute('INSERT INTO inbox_attention VALUES(1,99)')
            db.execute("UPDATE inbox_deliveries SET read_at='2026-11-02T10:00:00' WHERE user_id=2")
            db.commit()
            before=[tuple(r) for r in db.execute('SELECT * FROM inbox_deliveries WHERE user_id != 1')]
            with db:
                db.execute('BEGIN IMMEDIATE')
                result=add_latest_broadcast_sender_copy(db,1)
            self.assertEqual(result,dict(message_id=2,copy_added=True))
            self.assertEqual([tuple(r) for r in db.execute('SELECT * FROM inbox_deliveries WHERE user_id != 1')],before)
            self.assertEqual(db.execute('SELECT seen_through FROM inbox_attention WHERE user_id=1').fetchone()[0],1)
        self.assertEqual(self.client.get('/mail/status').json,dict(unread=1,latest=2,attention=True))
        self.client.post('/mail/oeffnen',data={'csrf_token':'test-token','through':'2'})
        with self.app.app_context():
            db=self.app.get_db()
            with db:
                db.execute('BEGIN IMMEDIATE')
                self.assertEqual(add_latest_broadcast_sender_copy(db,1),dict(message_id=2,copy_added=False))
        self.assertFalse(self.client.get('/mail/status').json['attention'])

    def test_control_copy_does_nothing_without_owner_broadcast(self):
        from inbox import add_latest_broadcast_sender_copy
        self.send(self.as_user(2),recipient='1')
        before=(self.rows('inbox_messages'),self.rows('inbox_deliveries'))
        with self.app.app_context():
            db=self.app.get_db()
            with db:
                db.execute('BEGIN IMMEDIATE')
                self.assertEqual(add_latest_broadcast_sender_copy(db,1),dict(message_id=None,copy_added=False))
        self.assertEqual((self.rows('inbox_messages'),self.rows('inbox_deliveries')),before)

    def test_deployment_control_copy_preserves_existing_wallet_and_other_receipts(self):
        import inbox
        from deploy.activate_update_1_01_02 import own_copy
        self.send(recipient='all')
        with self.app.app_context():
            db=self.app.get_db()
            db.execute('DELETE FROM inbox_deliveries WHERE user_id=1')
            db.execute("INSERT INTO currency_entries(user_id,amount,source,reference,detail_json,created_at) VALUES(1,500,'blackjack','preserve-for-copy','{}','2026-11-02')")
            db.commit()
            wallet=[tuple(r) for r in db.execute('SELECT * FROM currency_entries')]
            others=[tuple(r) for r in db.execute('SELECT * FROM inbox_deliveries WHERE user_id != 1')]
        result=own_copy(Path(self.app.config['DATABASE']),inbox,'stormseed')
        self.assertTrue(result['copy_added'])
        self.assertTrue(result['status']['attention'])
        with self.app.app_context():
            db=self.app.get_db()
            self.assertEqual([tuple(r) for r in db.execute('SELECT * FROM currency_entries')],wallet)
            self.assertEqual([tuple(r) for r in db.execute('SELECT * FROM inbox_deliveries WHERE user_id != 1')],others)

if __name__ == '__main__':
    unittest.main()

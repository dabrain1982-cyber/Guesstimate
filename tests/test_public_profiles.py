"""Signed-in discovery, public field boundary and read-only profile visits."""
from datetime import date,datetime,timedelta
from pathlib import Path
import tempfile
import unittest
from app import create_app


class PublicProfileTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.app=create_app({'TESTING':True,'SECRET_KEY':'profiles-test','DATABASE':str(Path(self.temp.name)/'test.sqlite3')});self.client=self.app.test_client()
        with self.app.app_context():
            db=self.app.get_db()
            for login,name in [('viewer-secret','Betrachter'),('target-secret','Mitspielerin & <Freunde>'),('new-secret','Neuling')]:
                db.execute('INSERT INTO users(username,display_name,pin_hash,created_at) VALUES(?,?,?,?)',(login,name,'secret-hash','2001-01-01T01:02:03'))
            db.execute("INSERT INTO user_cosmetics(user_id,avatar_id,plaque_id,background_id,phrase_id,developer_enabled,updated_at) VALUES(2,'a05','p01','b02','s01',1,'2001-01-01T01:02:03')")
            for index,score in enumerate((130,180,9999),1):
                day=(date.today()-timedelta(days=index+1)).isoformat()
                rid=db.execute('INSERT INTO daily_rounds(round_date,questions_json,created_at) VALUES(?,?,?)',(day,'[]',day)).lastrowid
                db.execute('INSERT INTO attempts(user_id,round_id,status,score,started_at) VALUES(2,?,?,?,?)',(rid,'completed' if index<3 else 'playing',score,day))
            db.commit()
        with self.client.session_transaction() as s:s.update(user_id=1,csrf_token='test-csrf',login_recorded_on=(date.today()-timedelta(days=1)).isoformat())
    def tearDown(self):self.temp.cleanup()
    def snapshot(self):
        with self.app.app_context():return '\n'.join(self.app.get_db().iterdump())
    def test_signin_required_missing_and_post_rejected(self):
        guest=self.app.test_client()
        for route in ('/spieler','/spieler/2'):
            r=guest.get(route);self.assertEqual(r.status_code,302);self.assertTrue(r.location.endswith('/login'))
        self.assertEqual(self.client.get('/spieler/999999').status_code,404)
        self.assertEqual(self.client.post('/spieler/2',data={'avatar_id':'a01'}).status_code,405)
    def test_other_profile_uses_subject_equipment_and_aggregate_results(self):
        r=self.client.get('/spieler/2');html=r.get_data(as_text=True);self.assertEqual(r.status_code,200)
        for value in ('Mitspielerin &amp; &lt;Freunde&gt;','a05-waschbaer.webp','p01-tavernenschild-tall-v2.png','stormseeds-perfect-clubroom-v1.png','Ich wusste es. Also fast.','310 Punkte','180 Punkte','155 Punkte','Titel von Mitspielerin'):
            self.assertIn(value,html)
        self.assertIn('variant-a-profile-canonical',html);self.assertEqual(html.count('data-profile-window>'),1)
        for private in ('target-secret','secret-hash','2001-01-01','developer_enabled','Entwicklermodus','Aussehen auswählen','/profil/ausruesten/','iKühe','9999'):
            self.assertNotIn(private,html)
        self.assertEqual(r.headers['Cache-Control'],'private, no-store');self.assertIn('noindex',r.headers['X-Robots-Tag'])
    def test_visits_are_read_only_even_after_viewer_session_day_changes(self):
        before=self.snapshot()
        for route in ('/spieler','/spieler/2','/spieler/1','/spieler?q=kein-name','/spieler/999999'):self.client.get(route)
        self.assertEqual(self.snapshot(),before)
    def test_neutral_public_avatar_and_empty_results(self):
        html=self.client.get('/spieler/3').get_data(as_text=True)
        self.assertIn('starter-neutral-public.svg',html);self.assertNotIn('/avatars/starter-neutral.svg',html)
        self.assertIn('Noch keine Daily-Quizrunde abgeschlossen.',html)
        self.assertNotIn('Eigenes Profil bearbeiten',html)
        self.assertIn('Eigenes Profil bearbeiten',self.client.get('/spieler/1').get_data(as_text=True))
    def test_directory_search_names_and_prefix(self):
        r=self.client.get('/spieler?q=MITSpielerin');html=r.get_data(as_text=True)
        self.assertIn('href="/spieler/2"',html);self.assertNotIn('href="/spieler/3"',html);self.assertIn('Mitspielerin &amp; &lt;Freunde&gt;',html)
        self.assertIn('Kein Spieler',self.client.get('/spieler?q=unbekannt').get_data(as_text=True))
        html=self.client.get('/spieler/2',headers={'X-Forwarded-Prefix':'/guesstimate'}).get_data(as_text=True)
        self.assertIn('href="/guesstimate/spieler"',html)
    def test_current_equipment_changes_are_read_on_the_next_visit(self):
        self.client.get('/spieler/2')
        with self.app.app_context():
            db=self.app.get_db();db.execute("UPDATE user_cosmetics SET avatar_id='a03',plaque_id='p02',background_id='b05',phrase_id='s02' WHERE user_id=2");db.commit()
        html=self.client.get('/spieler/2').get_data(as_text=True)
        for value in ('a03-wanderfalke.webp','p02-schiefer-tall-v2.png','background-bergsee-v1.png','Wissen ist Macht.'):
            self.assertIn(value,html)
    def test_existing_profile_and_rankings_offer_entry_points(self):
        with self.client.session_transaction() as s:s['login_recorded_on']=date.today().isoformat()
        own=self.client.get('/profil').get_data(as_text=True);home=self.client.get('/').get_data(as_text=True)
        for value in ('href="/spieler/1"','href="/spieler"','Aussehen auswählen','data-profile-panel="avatar"'):self.assertIn(value,own)
        self.assertIn('href="/spieler/2"',home);self.assertIn('Profil von Mitspielerin',home)
        room=self.client.post('/party/erstellen',data={'csrf_token':'test-csrf'}).location
        guest=self.app.test_client()
        with guest.session_transaction() as s:s.update(user_id=2,csrf_token='guest-csrf',login_recorded_on=date.today().isoformat())
        guest.post(room+'/beitreten',data={'csrf_token':'guest-csrf'})
        self.assertIn('href="/spieler/2"',self.client.get(room).get_data(as_text=True))


if __name__=='__main__':unittest.main()

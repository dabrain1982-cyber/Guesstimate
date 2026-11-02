"""Read-only iKuehe introduction and shared ranking navigation."""
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
import tempfile
import unittest
from app import create_app

class Page(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.tags=[]
        self.copy=[]
        self.feed(html)
    def handle_starttag(self,tag,attrs):
        self.tags.append((tag,dict(attrs)))
    def handle_data(self,data):
        self.copy.append(data)
    def by_id(self,identity):
        return next(attrs for tag,attrs in self.tags if attrs.get('id')==identity)
    @property
    def text(self):
        return ''.join(self.copy)

class CurrencyGuideTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.app=create_app(dict(TESTING=True,SECRET_KEY='disposable-guide-test',
            DATABASE=str(Path(self.temp.name)/'guide.sqlite3'),
            APPLICATION_ROOT='/guesstimate',PUBLIC_URL='https://example.test/guesstimate',
            BLACKJACK_CURRENCY='account-ikuehe'))
        with self.app.app_context():
            db=self.app.get_db()
            db.execute("INSERT INTO users(username,display_name,pin_hash,created_at) VALUES('guide-test','Guide-Test','not-a-login','2026-11-02')")
            db.execute("INSERT INTO daily_rounds(round_date,questions_json,created_at) VALUES('2026-10-01','[]','2026-10-01')")
            db.execute("INSERT INTO attempts(user_id,round_id,status,score,started_at,completed_at) VALUES(1,1,'completed',1500,'2026-10-01T10:00:00','2026-10-01T10:01:00')")
            db.execute("INSERT INTO shop_purchases VALUES(1,'avatar','a01',100,'2026-10-02T10:00:00')")
            db.execute("INSERT INTO currency_entries(user_id,amount,source,reference,detail_json,created_at) VALUES(1,-500,'blackjack','guide-fixture','{}','2026-10-03T10:00:00')")
            db.commit()
        self.client=self.app.test_client()
        with self.client.session_transaction() as session:
            session.update(user_id=1,login_recorded_on=date.today().isoformat(),
                show_catchup_prompt=False,csrf_token='guide-test')
    def get(self,path):
        response=self.client.get(path)
        self.assertEqual(response.status_code,200)
        return Page(response.get_data(as_text=True))
    def test_requires_login_and_explains_existing_account_and_planned_rewards(self):
        anonymous=self.app.test_client().get('/ikuehe')
        self.assertEqual(anonymous.status_code,302)
        self.assertIn('/guesstimate/login',anonymous.location)
        page=self.get('/ikuehe')
        self.assertIn('Der Wettstreit um iKühe',page.text)
        self.assertIn('900',page.text)
        self.assertIn('500 iKühe',page.text)
        self.assertIn('normalen Kontos',page.text)
        self.assertIn('All Time High',page.text)
        self.assertIn('noch nicht freigeschaltet',page.text)
        links={attrs.get('href') for tag,attrs in page.tags if tag=='a'}
        self.assertTrue({'/guesstimate/','/guesstimate/shop',
            '/guesstimate/karten/blackjack','/guesstimate/?rangliste=ikuehe'}<=links)
        self.assertNotIn('rules-button',{attrs.get('id') for tag,attrs in page.tags})
    def test_direct_ranking_link_selects_currency_and_preserves_default_quiz(self):
        for path,selected in [('/','quiz'),('/?rangliste=ikuehe','currency')]:
            with self.subTest(path=path):
                page=self.get(path)
                for key in ('quiz','currency','fame'):
                    tab=page.by_id('rank-group-'+key)
                    panel=page.by_id('rank-group-panel-'+key)
                    self.assertEqual(tab['aria-selected'],str(key==selected).lower())
                    self.assertEqual('hidden' in panel,key!=selected)
                self.assertEqual(page.by_id('tab-currency_current')['aria-selected'],'true')
                self.assertNotIn('hidden',page.by_id('panel-currency_current'))
    def test_reading_information_and_navigation_never_books_or_sends(self):
        tables=('attempts','shop_purchases','currency_entries','question_usage',
                'inbox_messages','inbox_deliveries','inbox_attention','user_notice_views')
        def snapshot():
            with self.app.app_context():
                db=self.app.get_db()
                return {table:[tuple(row) for row in db.execute('SELECT * FROM '+table+' ORDER BY rowid')]
                        for table in tables}
        before=snapshot()
        self.get('/ikuehe')
        self.assertEqual(snapshot(),before)
        # The existing home page prepares today's shared daily round once.
        self.get('/')
        before=snapshot()
        for path in ('/ikuehe','/?rangliste=ikuehe','/shop','/karten'):
            self.get(path)
        self.assertEqual(snapshot(),before)

    def test_intro_once_per_account_survives_a_new_browser_session(self):
        page=self.get('/')
        self.assertTrue(any('data-currency-intro' in attrs for _,attrs in page.tags))
        first=self.client.post('/ikuehe/einfuehrung',data={'csrf_token':'guide-test'})
        self.assertEqual(first.get_json(),{'show':True})
        second=self.app.test_client()
        with second.session_transaction() as session:
            session.update(user_id=1,login_recorded_on=date.today().isoformat(),csrf_token='second-browser')
        page=Page(second.get('/').get_data(as_text=True))
        self.assertFalse(any('data-currency-intro' in attrs for _,attrs in page.tags))
        self.assertEqual(second.post('/ikuehe/einfuehrung',data={'csrf_token':'second-browser'}).get_json(),{'show':False})
        with self.app.app_context():
            self.assertEqual(self.app.get_db().execute('SELECT COUNT(*) FROM user_notice_views').fetchone()[0],1)

    def test_intro_claim_requires_login_csrf_and_is_individual(self):
        self.assertEqual(self.app.test_client().post('/ikuehe/einfuehrung').status_code,302)
        self.assertEqual(self.client.post('/ikuehe/einfuehrung',data={'csrf_token':'wrong'}).status_code,400)
        with self.app.app_context():
            db=self.app.get_db()
            self.assertEqual(db.execute('SELECT COUNT(*) FROM user_notice_views').fetchone()[0],0)
            uid=db.execute("INSERT INTO users(username,display_name,pin_hash,created_at) VALUES('other-guide','Other-Guide','not-a-login','2026-11-02')").lastrowid
            db.commit()
        self.assertEqual(self.client.post('/ikuehe/einfuehrung',data={'csrf_token':'guide-test'}).get_json(),{'show':True})
        other=self.app.test_client()
        with other.session_transaction() as session:
            session.update(user_id=uid,login_recorded_on=date.today().isoformat(),csrf_token='other')
        self.assertEqual(other.post('/ikuehe/einfuehrung',data={'csrf_token':'other'}).get_json(),{'show':True})

if __name__=='__main__':unittest.main()

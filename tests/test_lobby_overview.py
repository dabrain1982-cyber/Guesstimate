"""Shared overview navigation/actions with isolated authenticated players."""
import re
import unittest
from unittest.mock import patch

from lobby_overview import overview_signature, render_overview
import test_card_table as fixtures


class LobbyOverviewTests(unittest.TestCase):
    setUp = fixtures.CardTableTests.setUp
    tearDown = fixtures.CardTableTests.tearDown
    games = [('/party','/party','party','/'),
             ('/karten/kartentisch','/karten','cards','/karten/kartentische'),
             ('/karten/wuerfeltisch','/karten/wuerfeltisch','sandbox','/karten/wuerfeltische'),
             ('/karten/kniffel','/karten/kniffel','kniffel','/karten/wuerfeltische'),
             ('/karten/maexchen','/karten/maexchen','maexchen','/karten/wuerfeltische'),
             ('/nerd','/nerd','perfect','/karten/brettspiele'),
             ('/karten/welteroberung','/karten/welteroberung','conquest','/karten/brettspiele')]

    def test_every_game_has_the_same_empty_overview_and_create_position(self):
        host, token = self.clients[0]
        for index, base, game, back in self.games:
            with self.subTest(game=game):
                response = host.get(index)
                self.assertEqual(response.status_code,200)
                page = response.get_data(as_text=True)
                self.assertEqual(page.count('data-lobby-overview '),1)
                self.assertIn(f'data-overview-game="{game}"',page)
                self.assertIn('Noch keine Lobby.',page)
                toolbar = re.search(r'<header class="lobby-browser-toolbar">.*?</header>',page,re.S)[0]
                self.assertIn(f'action="{base}/erstellen"',toolbar)
                self.assertIn('name="csrf_token"',toolbar)
                self.assertIn('lobby erstellen',toolbar)
                self.assertIn(f'href="{back}"',page)
                self.assertIn('/static/lobby-overview.js?',page)

    def test_join_and_return_actions_and_json_updates_for_all_games(self):
        host, token = self.clients[0]
        guest, guest_token = self.clients[1]
        for index, base, game, _ in self.games:
            with self.subTest(game=game):
                before = guest.get(index,headers={'Accept':'application/json'}).get_json()
                created = host.post(base+'/erstellen',data={'csrf_token':token})
                room = created.headers['Location']
                page = guest.get(index).get_data(as_text=True)
                self.assertIn(f'action="{room}/beitreten"',page)
                self.assertIn('<dt>Host</dt><dd>Host</dd>',page)
                own = host.get(index)
                self.assertEqual(own.status_code,200)  # Perfect must offer its own overview too.
                self.assertIn('zur lobby',own.get_data(as_text=True))
                changed = guest.get(index,headers={'Accept':'application/json'}).get_json()
                self.assertEqual(set(changed),{'signature'})
                self.assertNotEqual(before,changed)
                self.assertEqual(changed,guest.get(index,headers={'Accept':'application/json'}).get_json())
                guest.post(room+'/beitreten',data={'csrf_token':guest_token})
                joined = guest.get(index).get_data(as_text=True)
                self.assertIn('2/',joined)
                self.assertIn(f'href="{room}"',joined)
                self.assertNotIn(f'action="{room}/beitreten"',joined)

    def test_full_running_own_and_reserved_rows_offer_only_valid_actions(self):
        host = self.clients[0][0]
        row = dict(id=71,name='Freunde <script>test</script>',host_name='Host',
                   host_user_id=1,member_count=6,is_member=0,is_reserved=0,
                   status='waiting',victory_mode='missions')
        scenarios = [({},None,'Lobby voll'),
                     ({'status':'playing'},None,'Bereits gestartet'),
                     ({'is_member':1},'zur lobby',None),
                     ({'is_member':1,'status':'playing'},'zurück ins spiel',None),
                     ({'is_member':1,'status':'completed'},'ergebnis ansehen',None),
                     ({'is_reserved':1,'status':'playing'},'zurückkehren',None)]
        for changes,action,blocked in scenarios:
            with self.subTest(changes=changes), patch('conquest._lobby_rows',return_value=[dict(row,**changes)]):
                page = host.get('/karten/welteroberung').get_data(as_text=True)
                body = re.search(r'<article class="lobby-browser-row.*?</article>',page,re.S)[0]
                self.assertNotIn('<script>test</script>',body)
                self.assertIn('&lt;script&gt;test&lt;/script&gt;',body)
                if action:
                    self.assertIn('>'+action+'</',body)
                    if action == 'ergebnis ansehen':self.assertIn('href="/karten/welteroberung/71/lobby"',body)
                    if action == 'zurückkehren':self.assertIn('action="/karten/welteroberung/71/beitreten"',body)
                else:
                    self.assertIn(blocked,body)
                    self.assertNotIn('<form',body)
                    self.assertNotIn('<a ',body)

    def test_signature_tracks_display_changes_and_ignores_private_game_state(self):
        row = dict(id=1,name='Abend',status='playing',member_count=2,is_member=1,
                   host_name='Alex',state_json='private cards',revision=4)
        initial = overview_signature([row])
        self.assertEqual(initial,overview_signature([dict(row,state_json='other cards',revision=5)]))
        for field,value in [('member_count',3),('name','Neue Runde'),('host_name','Robin'),
                            ('status','completed'),('is_member',0),('victory_mode','world')]:
            with self.subTest(field=field):
                self.assertNotEqual(initial,overview_signature([dict(row,**{field:value})]))

    def test_prefix_is_preserved_for_status_forms_and_return_routes(self):
        self.app.add_url_rule('/uebersichten/<game>', 'overview_test',
                              lambda game: render_overview('card_table_index.html', []))
        host = self.clients[0][0]
        page = host.get('/karten/kartentisch',environ_overrides={'SCRIPT_NAME':'/test'}).get_data(as_text=True)
        self.assertIn('data-status-url="/test/karten/kartentisch"',page)
        self.assertIn('action="/test/karten/erstellen"',page)
        self.assertIn('href="/test/karten/kartentische"',page)
        dynamic = host.get('/uebersichten/karten',environ_overrides={'SCRIPT_NAME':'/test'}).get_data(as_text=True)
        self.assertIn('data-status-url="/test/uebersichten/karten"',dynamic)

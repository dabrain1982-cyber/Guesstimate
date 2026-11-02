"""Equipped public portraits are live display data, never saved turn data."""
import copy
import json
import unittest
from datetime import datetime
from pathlib import Path

from player_portrait import public_portrait
import test_conquest as fixtures


class ConquestPortraitTests(unittest.TestCase):
    setUp = fixtures.ConquestTests.setUp
    tearDown = fixtures.ConquestTests.tearDown
    create_lobby = fixtures.ConquestTests.create_lobby

    def start(self, guests=1):
        lobby = self.create_lobby()
        room = f'/karten/welteroberung/{lobby}'
        for client, token in self.clients[1:guests + 1]:
            client.post(room + '/beitreten', data={'csrf_token': token})
        self.clients[0][0].post(room + '/starten', data={'csrf_token': self.clients[0][1]})
        return lobby, room

    def equip(self, user, avatar):
        with self.app.app_context():
            db = self.app.get_db()
            db.execute('INSERT INTO user_cosmetics (user_id,avatar_id,updated_at) VALUES (?,?,?) '
                       'ON CONFLICT(user_id) DO UPDATE SET avatar_id=excluded.avatar_id',
                       (user, avatar, datetime.now().isoformat()))
            db.commit()

    def saved(self, lobby):
        with self.app.app_context():
            return tuple(self.app.get_db().execute('SELECT revision,state_json FROM conquest_lobbies WHERE id=?', (lobby,)).fetchone())

    def test_equipment_changes_refresh_without_mutating_saved_state_or_leaking_private_data(self):
        self.equip(1, 'a05')
        lobby, room = self.start()
        before = self.saved(lobby)
        host = self.clients[0][0]
        first = host.get(room + '/status').get_json()
        player = first['game']['armies'][0]
        self.assertTrue(player['portrait']['url'].endswith('/stage/a05-waschbaer.webp'))
        self.assertEqual(player['color_name'], 'Gold')
        self.assertEqual(set(player['portrait']), {'avatar_id', 'url', 'alt', 'crop'})
        self.equip(1, 'a09')
        second = host.get(room + '/status').get_json()
        self.assertEqual(first['revision'], second['revision'])
        self.assertTrue(second['game']['armies'][0]['portrait']['url'].endswith('/stage/a09-fennek.webp'))
        self.assertEqual(self.saved(lobby), before)
        self.assertNotIn('missions', second['game'])
        self.assertNotIn('hands', second['game'])
        self.assertNotIn('pin_hash', json.dumps(second))
        self.assertIsNone(second['game']['armies'][-1]['portrait'], 'Neutral is an army, not a user')

    def test_default_avatar_respects_self_and_public_views(self):
        _, room = self.start()
        host = self.clients[0][0].get(room + '/status').get_json()['game']['armies']
        guest = self.clients[1][0].get(room + '/status').get_json()['game']['armies']
        self.assertTrue(host[0]['portrait']['url'].endswith('/starter-neutral.svg'))
        self.assertTrue(guest[0]['portrait']['url'].endswith('/starter-neutral-public.svg'))
        self.assertTrue(guest[1]['portrait']['url'].endswith('/starter-neutral.svg'))

    def test_public_card_counts_for_every_army_keep_hands_private_and_state_unchanged(self):
        lobby, room = self.start(3)
        with self.app.app_context():
            db = self.app.get_db()
            state = json.loads(db.execute('SELECT state_json FROM conquest_lobbies WHERE id=?', (lobby,)).fetchone()[0])
            ids = [str(player['id']) for player in state['participants']]
            countries = list(state['territories'])
            state['hands'] = {key: countries[:index + 1] for index, key in enumerate(ids)}
            db.execute('UPDATE conquest_lobbies SET state_json=? WHERE id=?', (json.dumps(state), lobby))
            db.commit()
        before = self.saved(lobby)
        host = self.clients[0][0].get(room + '/status').get_json()['game']
        guest = self.clients[1][0].get(room + '/status').get_json()['game']
        self.assertEqual([player['card_count'] for player in host['armies']], [1, 2, 3])
        self.assertEqual([player['card_count'] for player in guest['armies']], [1, 2, 3])
        self.assertEqual(len(host['inventory']['territory_cards']), 1)
        self.assertEqual(len(guest['inventory']['territory_cards']), 2)
        self.assertNotIn('hands', host)
        self.assertNotIn('missions', host)
        self.assertEqual(self.saved(lobby), before)

    def test_reserved_player_keeps_equipped_portrait(self):
        self.equip(2, 'a14')
        lobby, room = self.start(2)
        self.clients[1][0].post(room + '/verlassen', data={'csrf_token': self.clients[1][1]})
        before = self.saved(lobby)
        rows = self.clients[0][0].get(room + '/status').get_json()['game']['armies']
        self.assertEqual(rows[1]['kind'], 'player')
        self.assertTrue(rows[1]['portrait']['url'].endswith('/stage/a14-somnus-cutout-v2.png'))
        self.assertEqual(self.saved(lobby), before)

    def test_catalog_fallback_prefix_and_shared_module_access(self):
        with self.app.test_request_context(environ_overrides={'SCRIPT_NAME': '/prefix'}):
            catalog = self.app.extensions['player_portraits']
            original = copy.deepcopy(catalog)
            for avatar_id, avatar in catalog.items():
                portrait = public_portrait(avatar_id)
                self.assertTrue(portrait['url'].startswith('/prefix/static/avatars/'))
                asset = avatar['public_asset'] if avatar_id == 'a00' else avatar['stage_asset']
                self.assertTrue((Path(self.app.static_folder) / 'avatars' / asset).is_file())
            self.assertEqual(public_portrait('unknown')['avatar_id'], 'a00')
            self.assertEqual(catalog, original)
        _, room = self.start()
        page = self.clients[0][0].get(room).get_data(as_text=True)
        self.assertIn('player-portrait.css', page)
        self.assertEqual(self.clients[0][0].get('/karten/welteroberung/tisch-assets/player-portrait.js').data,
                         (Path(self.app.static_folder) / 'player-portrait.js').read_bytes())
        self.assertEqual(self.app.test_client().get('/karten/welteroberung/tisch-assets/player-portrait.js').status_code, 302)

    def test_saved_button_uses_the_shared_renderer_and_only_allowlisted_assets(self):
        self.start()
        root = Path(__file__).resolve().parents[1]
        client = self.clients[0][0]
        for name, source in (
            ('button-renderer.js', 'button-workshop-v1/renderer.js'),
            ('geometry.js', 'button-workshop-v1/geometry.js'),
            ('components.js', 'comic-ui-v1/components.js'),
            ('button-materials.css', 'button-workshop-v1/materials.css'),
            ('button-assets/slate-v1.png', 'button-workshop-v1/assets/slate-v1.png'),
        ):
            self.assertEqual(client.get('/karten/welteroberung/tisch-assets/' + name).data,
                             (root / 'offline-preview' / source).read_bytes())
        profile = client.get('/karten/welteroberung/tisch-assets/button-profile.json').get_json()
        self.assertEqual(profile['name'], 'Stormseed´s conquest')
        self.assertEqual(profile['settings']['depth'], 4)
        self.assertEqual(client.get('/karten/welteroberung/tisch-assets/../../runtime/pc-local/quiz.sqlite3').status_code, 404)

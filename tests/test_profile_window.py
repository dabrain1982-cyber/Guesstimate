import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from flask import render_template_string, session

from app import create_app


class ProfileWindowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tempdir = tempfile.TemporaryDirectory()
        cls.app = create_app({'TESTING': True, 'SECRET_KEY': 'profile-window-test',
                              'DATABASE': str(Path(cls.tempdir.name) / 'test.sqlite3')})
        with cls.app.app_context():
            db = cls.app.get_db()
            db.execute("INSERT INTO users (username, display_name, pin_hash, created_at) VALUES (?, ?, ?, ?)",
                       ('fenstertest', 'Fenstertest', 'unused', datetime.now().isoformat()))
            db.commit()

    @classmethod
    def tearDownClass(cls):
        cls.tempdir.cleanup()

    def render_window(self, call='{{ profile_window(cosmetics, trophies, **options) }}', **options):
        with self.app.test_request_context('/profil'):
            session.update(user_id=1, login_recorded_on=datetime.now().date().isoformat())
            self.app.preprocess_request()
            return render_template_string(
                '{% from "_profile_window.html" import profile_window with context %}' + call,
                cosmetics={'avatar_id': 'a05', 'plaque_id': 'p01', 'background_id': 'b00', 'phrase_id': ''},
                trophies={'daily': 2, 'weekly': 3, 'monthly': 4},
                options={'show_edit': False, 'player_balance': 1234, **options},
            )

    def test_existing_profile_and_perfect_values_keep_their_meaning(self):
        profile = self.render_window()
        self.assertIn('1.234 <bdi class="currency-unit">iKühe</bdi>', profile)
        self.assertIn('href="/shop"', profile)
        self.assertIn('Deine Pokale', profile)
        self.assertIn('<b>2</b>', profile)
        perfect = self.render_window(game_points=0, balance_link=False, show_details=False)
        self.assertIn('0 Punkte', perfect)
        self.assertNotIn('🐮', perfect)
        self.assertNotIn('href="/shop"', perfect)
        self.assertNotIn('data-profile-content', perfect)

    def test_custom_fields_status_and_stats_are_separate_from_profile_equipment(self):
        page = self.render_window(show_details=False, podium_fields={'name': 'Andere Anzeige', 'value': 0, 'label': 'Truppen'},
                                  player_status={'text': 'am Zug', 'tone': 'active'},
                                  content_items=[{'key': 'countries', 'label': 'Länder', 'value': 14},
                                                 {'key': 'armies', 'label': 'Truppen', 'value': 1000}])
        self.assertIn('Andere Anzeige</strong>', page)
        self.assertIn('0 Truppen', page)
        self.assertIn('am Zug</p>', page)
        self.assertIn('1.000', page)
        self.assertIn('data-profile-stat="countries"', page)
        self.assertIn('a05-waschbaer.webp', page)
        self.assertIn('p01-tavernenschild-tall-v2.png', page)
        self.assertNotIn('href="/shop"', page)
        self.assertNotIn('tagessiege', page)

    def test_rich_content_uses_the_same_window_and_escapes_player_text(self):
        page = self.render_window(
            '{% call profile_window(cosmetics, trophies, **options) %}<button>karten ansehen</button>{{ "<script>privat</script>" }}{% endcall %}',
            show_details=False, content_size='expanded', content_label='Eigene Karten',
        )
        self.assertEqual(page.count('data-profile-window'), 1)
        self.assertIn('data-profile-slot', page)
        self.assertIn('karten ansehen', page)
        self.assertIn('&lt;script&gt;privat&lt;/script&gt;', page)
        self.assertNotIn('<script>privat', page)
        self.assertIn('aria-label="Eigene Karten"', page)

    def test_empty_content_area_can_be_reserved_or_sized_without_stretching_the_scene(self):
        for size in ('compact', 'standard', 'expanded'):
            with self.subTest(size=size):
                page = self.render_window(show_details=False, content_size=size)
                self.assertIn(f'profile-content-{size}', page)
                self.assertNotIn('tagessiege', page)
        page = self.render_window(show_details=False, content_height=160)
        self.assertIn('--profile-content-height: 160px', page)
        self.assertEqual(page.count('variant-a-profile-scene'), 1)
        hidden = self.render_window(content_height=0)
        self.assertNotIn('data-profile-content', hidden)

    def test_text_and_unknown_display_options_cannot_inject_markup_or_styles(self):
        page = self.render_window(show_details=False,
                                  podium_fields={'name': '<script>x</script>', 'value': '<img src=x>', 'label': 'Text'},
                                  player_status={'text': '<b>bereit</b>', 'tone': 'bad-class'},
                                  content_size='bad-class', content_height='2px; color:red')
        self.assertIn('&lt;script&gt;x&lt;/script&gt;', page)
        self.assertIn('&lt;img src=x&gt; Text', page)
        self.assertIn('&lt;b&gt;bereit&lt;/b&gt;', page)
        self.assertNotIn('<script>x', page)
        self.assertNotIn('bad-class', page)
        self.assertNotIn('color:red', page)

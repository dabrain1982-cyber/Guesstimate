"""Explicit formatting survives saving; old recipes retain their exact settings."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import tempfile
import unittest

from tests.test_game_workshop import serve, TEST_ROOT
from tests.test_workshop_collections import empty_project
from button_bridge import storage
from workspace_store import ProjectLibrary
from source_buttons import SourceButtons
from media_selection import matched_css


class ButtonTypographyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source=SourceButtons()
        asset=next(a for a in source.assets() if a['game']=='Guesstimate' and a['label']=='spielen →')
        cls.original=source.recipe(asset['id'],storage.CATALOG)

    def test_optional_formatting_does_not_change_older_recipes(self):
        value=storage.validate_recipe(self.original)
        self.assertNotIn('font_bold',value['settings'])
        self.assertNotIn('font_italic',value['settings'])
        for key in ('font_bold','font_italic'):
            for invalid in (1,0,'true',None):
                candidate=deepcopy(self.original);candidate['settings'][key]=invalid
                with self.assertRaises(storage.InvalidRecipe):storage.validate_recipe(candidate)

    def test_chalk_and_formatting_save_reopen_and_handoff_without_touching_the_previous_version(self):
        with tempfile.TemporaryDirectory(dir=TEST_ROOT) as directory:
            store=ProjectLibrary(Path(directory)/'library',Path(directory)/'buttons')
            first=store.button_store.save(self.original);path=store.buttons_directory/(first['id']+'.json');before=path.read_bytes()
            value=deepcopy(first);value['parent_id']=first['id']
            value['settings'].update(font='letter-chalk',font_link='manual',lettering='plain',font_bold=False,font_italic=True)
            saved=store.button_store.save(value)
            reopened=ProjectLibrary(store.directory,store.buttons_directory)
            rows,bad=reopened.button_store.list();self.assertEqual(bad,0)
            self.assertEqual(next(r for r in rows if r['id']==saved['id'])['settings'],saved['settings'])
            project=empty_project('Schriftformatierung');project['items']=[dict(kind='buttons',id=saved['id'])]
            project=reopened.save_project(project)
            self.assertEqual(reopened.handoff(project['id'])['project']['items'][0]['snapshot']['settings']['font_italic'],True)
            self.assertEqual(path.read_bytes(),before)

    def test_chalk_uses_both_local_font_cuts_instead_of_a_stripe_mask(self):
        css=matched_css()
        self.assertIn("font-family:'Workshop Cabin Sketch'",css)
        self.assertIn('/assets/fonts/CabinSketch-Regular.ttf',css)
        self.assertIn('/media-assets/fonts/cabinsketch/font.ttf',css)
        self.assertNotIn('mask-image:',css)
        font=serve.ROOT/'offline-preview/button-workshop-v1/assets/fonts/CabinSketch-Regular.ttf'
        self.assertEqual(sha256(font.read_bytes()).hexdigest(),'a6f989fcc910ca321e06cd6a20dbcab20f9e41bce084911432857cfe286355e7')


if __name__=='__main__':unittest.main()

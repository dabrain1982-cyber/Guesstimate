"""Whole custom decks, independent face styles and temporary comparison state."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
from threading import Thread
import unittest
from urllib.error import HTTPError
from urllib.request import build_opener,ProxyHandler,Request
from tests.test_game_workshop import serve,TEST_ROOT
from tests.test_workshop_collections import empty_project
from card_designs import CardDesigns,DEFAULTS,MEMBERS
from library_store import InvalidDesign
from workspace_store import ProjectLibrary

class CardDesignTests(unittest.TestCase):
    def setUp(self):self.temp=tempfile.TemporaryDirectory(dir=TEST_ROOT);self.root=Path(self.temp.name);self.store=CardDesigns(self.root)
    def tearDown(self):self.temp.cleanup()
    def payload(self,**settings):return dict(name='Mein Kartensatz',settings={**DEFAULTS,**settings},members=deepcopy(MEMBERS),parent_id=None)
    def test_member_integrity_limits_and_unknown_fields(self):
        for cards in ([],[MEMBERS[0]]*2,[dict(MEMBERS[0],symbol='url(x)')],[dict(MEMBERS[0],text='x'*501)],[dict(MEMBERS[0],id='../../private')]):
            with self.subTest(cards=cards),self.assertRaises(InvalidDesign):self.store.members(cards)
        cards=[dict(MEMBERS[0],id='card-'+str(index)) for index in range(101)]
        with self.assertRaises(InvalidDesign):self.store.members(cards)
        with self.assertRaises(InvalidDesign):self.store.save({**self.payload(), 'question_bank':'questions.py'})
    def test_size_ranges_and_independent_colours(self):
        for patch in (dict(height=True),dict(height=31),dict(ratio=.57),dict(front='url(https://example.com)'),dict(representation='unknown')):
            with self.assertRaises(InvalidDesign):self.store.save(self.payload(**patch))
        value=self.store.save(self.payload(front='#d9e6d4',back='#254b3f',back_accent='#fff0d0'))
        self.assertEqual(value['settings']['front_accent'],DEFAULTS['front_accent']);self.assertEqual(value['settings']['ink'],DEFAULTS['ink'])
    def test_preview_member_comparison_and_script_escaping_are_not_equipment(self):
        value=self.payload();value['members'][0]['title']='</script><script>bad()</script>'
        view=dict(member_id=MEMBERS[1]['id'],face='both',comparison=True,fit=False,scale=110,tilt=True)
        page=self.store.preview(value['settings'],value['members'],view=view)
        raw=page.split('<script id="card-design-config" type="application/json">')[1].split('</script>')[0]
        self.assertEqual(json.loads(raw)['view'],view);self.assertNotIn('<script>bad()',page)
        record=self.store.save(value);self.assertNotIn('view',record)
        with self.assertRaises(InvalidDesign):self.store.preview(DEFAULTS,MEMBERS,view={**view,'member_id':'missing'})
        with self.assertRaises(InvalidDesign):self.store.preview(DEFAULTS,MEMBERS,view={**view,'scale':True})
    def test_versions_and_handoff_preserve_the_entire_deck(self):
        first=self.store.save(self.payload());path=self.store.directory/(first['id']+'.json');before=path.read_bytes()
        changed=self.payload();changed['members'].append(dict(id='card-3',title='Dritte Karte',text='Eigener Inhalt',symbol='none'));changed['parent_id']=first['id']
        second=self.store.save(changed);self.assertEqual(path.read_bytes(),before);self.assertEqual(CardDesigns(self.root).get(second['id']),second)
        library=ProjectLibrary(self.root,self.root/'buttons');asset=next(a for a in library.assets() if a['id']==second['id']);self.assertEqual(asset['snapshot'],second)
        project=empty_project('Eigene Karten');project['items']=[dict(kind='cards',id=second['id'])];saved=library.save_project(project)
        self.assertEqual(library.handoff(saved['id'])['project']['items'][0]['snapshot']['members'],second['members'])
        self.assertEqual(asset['record_role'],'finite_set')
    def test_corruption_is_preserved_and_paths_are_rejected(self):
        record=self.store.save(self.payload());bad=self.store.directory/('deck-'+'0'*32+'.json');bad.write_text('{',encoding='utf-8')
        rows,count=self.store.list();self.assertEqual(rows,[record]);self.assertEqual(count,1);self.assertEqual(bad.read_text(encoding='utf-8'),'{')
        with self.assertRaises(InvalidDesign):self.store.get('../../private')
    def test_local_http_config_save_preview_member_and_source_body(self):
        server=serve.make_server(0,self.root/'library',self.root/'buttons');thread=Thread(target=server.serve_forever,daemon=True);thread.start()
        opener=build_opener(ProxyHandler({}));base='http://127.0.0.1:'+str(server.server_port)
        def post(path,value,origin=None):return Request(base+path,data=json.dumps(value).encode(),headers={'Content-Type':'application/json','Origin':origin or base})
        try:
            with opener.open(base+'/api/card-designs') as response:self.assertEqual(json.load(response)['defaults'],DEFAULTS)
            with opener.open(post('/api/card-designs/preview',dict(settings=DEFAULTS,members=MEMBERS))) as response:self.assertIn('card-design-config',json.load(response)['html'])
            with opener.open(post('/api/card-designs',self.payload())) as response:asset=json.load(response)['asset'];self.assertEqual(response.status,201)
            with opener.open(base+asset['preview']+'?member=card-2') as response:
                page=response.read().decode();self.assertIn('"member_id": "card-2"',page);self.assertIn("script-src 'self'",response.headers['Content-Security-Policy'])
            for path in ('/card-editor.js','/card-authoring.js','/card-components/body.js'):
                with opener.open(base+path) as response:self.assertEqual(response.status,200);response.read()
            with self.assertRaises(HTTPError) as error:opener.open(post('/api/card-designs',self.payload(),origin='https://example.com'))
            self.assertEqual(error.exception.code,403);error.exception.close()
        finally:server.shutdown();server.server_close();thread.join(3)

if __name__=='__main__':unittest.main()

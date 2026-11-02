"""Image originals, proportional crops and project handoff, entirely in isolated storage."""
from io import BytesIO
from pathlib import Path
import hashlib
import json
import tempfile
from threading import Thread
import unittest
from urllib.error import HTTPError
from urllib.request import Request,ProxyHandler,build_opener
from PIL import Image
from tests.test_game_workshop import serve,TEST_ROOT
from tests.test_workshop_collections import empty_project,payload
from image_store import ImageStore,MAX_BYTES,InvalidDesign,validate_recipe
from workspace_store import ProjectLibrary


def fixture():
    image=Image.new('RGBA',(800,600),(220,45,45,255))
    image.paste((35,170,80,255),(400,0,800,300))
    image.paste((40,90,210,110),(0,300,400,600))
    image.paste((245,200,30,255),(400,300,800,600))
    out=BytesIO();image.save(out,format='PNG');return out.getvalue()


class ImageTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=TEST_ROOT)
        self.root=Path(self.temp.name).resolve()
        self.store=ImageStore(self.root)

    def tearDown(self):
        self.assertTrue(self.root.is_relative_to(TEST_ROOT.resolve()))
        self.temp.cleanup()

    def test_original_bytes_and_filename_are_preserved_and_reopenable(self):
        raw=fixture();record=self.store.import_image(raw,r'C:\Bilder\Meine Idee.png','background')
        self.assertEqual(record['filename'],'Meine Idee.png')
        self.assertEqual((self.root/record['file']).read_bytes(),raw)
        self.assertEqual(record['sha256'],hashlib.sha256(raw).hexdigest())
        reloaded=ImageStore(self.root).info(record['id'])
        self.assertEqual((reloaded['width'],reloaded['height']),(800,600))
        self.assertEqual(len(self.store.records()[0]),1)

    def test_card_back_artwork_reopens_as_variants_of_one_library_component(self):
        raw=fixture()
        first=self.store.import_image(raw,'Black Jack · Samtgrün.png','cards')
        second=self.store.import_image(raw,'Black Jack · Nachtblau.png','cards')
        reopened=ImageStore(self.root)
        assets=reopened.assets()
        self.assertEqual(len(assets),2)
        self.assertEqual({row['kind'] for row in assets},{'cards'})
        self.assertEqual({row['model_id'] for row in assets},{'card-back-image-v1'})
        self.assertEqual({row['record_role'] for row in assets},{'back_artwork'})
        self.assertTrue(all(row['image'].startswith('/library-images/') for row in assets))
        self.assertTrue(all(not row['editable'] for row in assets))
        self.assertEqual((self.root/first['file']).read_bytes(),raw)
        self.assertEqual((self.root/second['file']).read_bytes(),raw)

    def test_crop_preview_and_saved_file_share_the_same_pixels(self):
        original=self.store.import_image(fixture(),'Vier Farben.png','background')
        before=(self.root/original['file']).read_bytes()
        recipe=dict(x=400,y=0,width=400,height=300,output_width=200)
        preview,dimensions,_=self.store.render(original['id'],recipe,preview=True)
        saved=self.store.save_variant(dict(source_id=original['id'],name='Grüner Ausschnitt',kind='titles',recipe=recipe))
        raw=(self.root/saved['file']).read_bytes()
        self.assertEqual(raw,preview)
        self.assertEqual(dimensions,(200,150))
        with Image.open(BytesIO(raw)) as image:
            self.assertEqual(image.size,(200,150))
            self.assertEqual(image.getpixel((100,75)),(35,170,80,255))
        self.assertEqual((self.root/original['file']).read_bytes(),before)
        info=self.store.info(saved['id'])
        self.assertEqual(info['recipe'],recipe)
        self.assertEqual(info['source_id'],original['id'])
        self.assertEqual(len(self.store.records()[0]),2)

    def test_transparency_is_preserved(self):
        original=self.store.import_image(fixture(),'Mit Alpha.png','icons')
        saved=self.store.save_variant(dict(source_id=original['id'],name='Transparente Ecke',kind='icons',
                                          recipe=dict(x=0,y=300,width=400,height=300,output_width=400)))
        with Image.open(self.root/saved['file']) as image:
            self.assertEqual(image.getpixel((200,150))[3],110)

    def test_jpeg_orientation_is_normalized_without_changing_original(self):
        image=Image.new('RGB',(12,8),'red');exif=Image.Exif();exif[274]=6
        out=BytesIO();image.save(out,format='JPEG',exif=exif);raw=out.getvalue()
        saved=self.store.import_image(raw,'Hochkant.jpg','flyers')
        self.assertEqual((saved['width'],saved['height']),(8,12))
        self.assertEqual((self.root/saved['file']).read_bytes(),raw)
        with Image.open(BytesIO(self.store.source_preview(saved['id']))) as view:
            self.assertEqual(view.size,(8,12))

    def test_webp_can_be_imported(self):
        image=Image.new('RGBA',(40,30),(20,90,80,160));out=BytesIO();image.save(out,format='WEBP',lossless=True)
        raw=out.getvalue();record=self.store.import_image(raw,'Webbild.webp','background')
        self.assertEqual(record['format'],'WEBP')
        self.assertEqual((self.root/record['file']).read_bytes(),raw)

    def test_invalid_upload_and_paths_do_not_write_images(self):
        for raw in [b'',b'<svg onload="bad"/>',b'not an image',b'x'*(MAX_BYTES+1)]:
            with self.assertRaises(InvalidDesign):self.store.import_image(raw,'bad.png','background')
        with self.assertRaises(InvalidDesign):self.store.info('../../app')
        with self.assertRaises(InvalidDesign):self.store._path('../elsewhere')
        self.assertFalse((self.root/'images').exists())

    def test_invalid_crop_and_output_are_rejected_without_silent_distortion(self):
        recipe=dict(x=0,y=0,width=800,height=600,output_width=800)
        for field,value in [('x',-1),('width',801),('height',0),('output_width',4097),('x',True),('height',1.5)]:
            altered={**recipe,field:value}
            with self.assertRaises(InvalidDesign):validate_recipe(altered,800,600)
        with self.assertRaises(InvalidDesign):validate_recipe(dict(x=0,y=0,width=10,height=600,output_width=4096),800,600)
        checked,height=validate_recipe({**recipe,'output_width':640},800,600)
        self.assertEqual(height,480)
        self.assertEqual(checked['width'],800)

    def test_projects_freeze_images_and_reuse_them_without_copying_originals(self):
        library=ProjectLibrary(self.root/'library',self.root/'buttons')
        original=library.images.import_image(fixture(),'Mein Bild.png','background')
        variant=library.images.save_variant(dict(source_id=original['id'],name='Mein Icon',kind='icons',
                                               recipe=dict(x=100,y=100,width=300,height=300,output_width=128)))
        refs=[dict(kind='icons',id=variant['id'])]
        a=empty_project('Meine erste Idee');a['items']=refs
        b=empty_project('Meine zweite Idee');b['items']=refs
        first=library.save_project(a);second=library.save_project(b)
        self.assertEqual(first['items'][0]['snapshot'],second['items'][0]['snapshot'])
        self.assertEqual(first['items'][0]['snapshot']['sha256'],variant['sha256'])
        handoff=library.handoff(first['id'])
        self.assertEqual(handoff['project']['items'][0]['snapshot']['file'],variant['file'])
        self.assertEqual(len(library.images.records()[0]),2)
        library=ProjectLibrary(self.root/'library',self.root/'buttons')
        self.assertEqual(len(library.project_groups()),2)
        self.assertTrue(any(v['id']==variant['id'] for v in library.assets()))

    def test_existing_picture_is_read_only_until_variant_is_saved(self):
        asset=next(a for a in serve.EXISTING_ASSETS if a['kind']=='background')
        path=serve.ROOT/asset['snapshot']['asset'];before=path.read_bytes()
        store=ImageStore(self.root,[asset]);info=store.info(asset['id'])
        self.assertFalse((self.root/'images').exists())
        recipe=dict(x=0,y=0,width=min(300,info['width']),height=min(200,info['height']),output_width=240)
        store.save_variant(dict(source_id=asset['id'],name='Eigene Bildvariante',kind='background',recipe=recipe))
        self.assertEqual(path.read_bytes(),before)
        self.assertEqual(len(store.records()[0]),1)

    def test_changed_image_file_is_reported_and_not_removed(self):
        record=self.store.import_image(fixture(),'Original.png','background')
        path=self.root/record['file'];path.write_bytes(b'changed')
        with self.assertRaises(InvalidDesign):self.store.view(record['id'])
        self.assertTrue(path.exists())


class ImageHTTPTests(unittest.TestCase):
    def test_import_preview_save_and_origin_boundary(self):
        with tempfile.TemporaryDirectory(dir=TEST_ROOT) as directory:
            server=serve.make_server(0,Path(directory)/'library',Path(directory)/'buttons')
            thread=Thread(target=server.serve_forever,daemon=True);thread.start()
            base='http://127.0.0.1:'+str(server.server_port);opener=build_opener(ProxyHandler({}))
            try:
                headers={'Content-Type':'image/png','X-Filename':'Mein%20Bild.png','X-Image-Kind':'background'}
                with opener.open(Request(base+'/api/images/import',data=fixture(),headers=headers),timeout=3) as response:
                    original=json.load(response)['asset'];self.assertEqual(response.status,201)
                recipe=dict(x=100,y=50,width=400,height=300,output_width=640)
                with opener.open(Request(base+'/api/images/preview',data=json.dumps(dict(source_id=original['id'],recipe=recipe)).encode(),
                                         headers={'Content-Type':'application/json'}),timeout=3) as response:
                    self.assertEqual(response.headers['Content-Type'],'image/png')
                    with Image.open(BytesIO(response.read())) as image:self.assertEqual(image.size,(640,480))
                with self.assertRaises(HTTPError) as failure:
                    opener.open(Request(base+'/api/images/import',data=fixture(),headers={**headers,'Origin':'https://elsewhere.example'}),timeout=3)
                self.assertEqual(failure.exception.code,403);failure.exception.close()
                with self.assertRaises(HTTPError) as failure:opener.open(base+'/library-images/../../app.py',timeout=3)
                self.assertIn(failure.exception.code,(400,404));failure.exception.close()
                with opener.open(base+'/api/library',timeout=3) as response:
                    value=json.load(response);self.assertEqual(value['project_groups'],[])
                    self.assertTrue(any(a['id']==original['id'] for a in value['assets']))
            finally:server.shutdown();server.server_close();thread.join(3)
            self.assertTrue(Path(directory).resolve().is_relative_to(TEST_ROOT.resolve()))


if __name__=='__main__':unittest.main()

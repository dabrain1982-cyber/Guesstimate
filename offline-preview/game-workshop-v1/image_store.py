"""Immutable raster originals and crop/resize variants; one renderer for preview and file."""
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
from io import BytesIO
import json
import math
from pathlib import Path
import re
from uuid import uuid4
from PIL import Image, ImageOps, UnidentifiedImageError
from library_store import InvalidDesign, ROOT, text_value

IMAGE_KINDS=('background','titles','icons','flyers','avatars','cards')
IMAGE_ID=re.compile(r'^image-[a-f0-9]{32}$')
MAX_BYTES=20*1024*1024
MAX_PIXELS=40_000_000
MAX_SIDE=4096
FORMATS={'PNG':'.png','JPEG':'.jpg','WEBP':'.webp'}


def decode(raw):
    try:
        with Image.open(BytesIO(raw)) as image:
            if image.format not in FORMATS or getattr(image,'n_frames',1)!=1:
                raise InvalidDesign('Bitte ein einzelnes PNG-, JPEG- oder WebP-Bild wählen.')
            if image.width*image.height>MAX_PIXELS:
                raise InvalidDesign('Das Bild darf höchstens 40 Millionen Bildpunkte haben.')
            fmt=image.format
            image.verify()
        with Image.open(BytesIO(raw)) as image:
            normalized=ImageOps.exif_transpose(image).convert('RGBA')
        return normalized,fmt
    except (UnidentifiedImageError,OSError,SyntaxError,Image.DecompressionBombError) as error:
        raise InvalidDesign('Die Datei konnte nicht als PNG-, JPEG- oder WebP-Bild gelesen werden.') from error


def validate_recipe(value,width,height):
    if not isinstance(value,dict) or set(value)!={'x','y','width','height','output_width'}:
        raise InvalidDesign('Der Bildausschnitt ist unvollständig.')
    if any(type(v) is not int for v in value.values()):
        raise InvalidDesign('Bildausschnitt und Größe benötigen ganze Pixelwerte.')
    x,y,w,h,out=(value[k] for k in ('x','y','width','height','output_width'))
    if x<0 or y<0 or w<1 or h<1 or x+w>width or y+h>height:
        raise InvalidDesign('Der Ausschnitt muss vollständig innerhalb des Originals liegen.')
    if not 1<=out<=MAX_SIDE:
        raise InvalidDesign('Die Ausgabe darf höchstens 4096 Pixel je Seite haben.')
    output_height=max(1,math.floor(out*h/w+.5))
    if output_height>MAX_SIDE:
        raise InvalidDesign('Die Ausgabehöhe darf höchstens 4096 Pixel betragen. Bitte die Breite verkleinern.')
    return deepcopy(value),output_height


def png_bytes(image):
    out=BytesIO();image.save(out,format='PNG');return out.getvalue()


class ImageStore:
    def __init__(self,directory,existing=()):
        self.directory=Path(directory).resolve()
        self.existing={a['id']:deepcopy(a) for a in existing if a.get('image') and a['kind'] in IMAGE_KINDS
                       and Path(a['snapshot']['asset']).suffix.lower() in ('.png','.jpg','.jpeg','.webp')}

    def _path(self,relative):
        path=(self.directory/relative).resolve()
        if not path.is_relative_to(self.directory/'images'):
            raise InvalidDesign('Ungültiger Bildpfad.')
        return path

    def get(self,identifier):
        if not isinstance(identifier,str) or not IMAGE_ID.fullmatch(identifier):
            raise InvalidDesign('Diese Bildkennung ist ungültig.')
        try:record=json.loads(self._path('images/records/'+identifier+'.json').read_text(encoding='utf-8'))
        except (OSError,ValueError) as error:raise InvalidDesign('Das gespeicherte Bild wurde nicht gefunden.') from error
        if not isinstance(record,dict) or record.get('id')!=identifier or record.get('schema')!=1 or record.get('kind') not in IMAGE_KINDS:
            raise InvalidDesign('Der gespeicherte Bildeintrag ist ungültig.')
        role=record.get('role');fmt=record.get('format')
        suffix=FORMATS.get(fmt) if role=='original' and isinstance(fmt,str) else '.png' if role=='variant' and fmt=='PNG' else None
        folder='originals' if role=='original' else 'variants'
        if role not in ('original','variant') or not suffix or record.get('file')!='images/'+folder+'/'+identifier+suffix:
            raise InvalidDesign('Der gespeicherte Bildpfad ist ungültig.')
        if not self._path(record['file']).is_file():raise InvalidDesign('Die zugehörige Bilddatei fehlt.')
        text_value(record.get('name'),100,'Bildname',True)
        text_value(record.get('filename'),255,'Dateiname',True)
        if not isinstance(record.get('source_id'),str):raise InvalidDesign('Die Originalzuordnung des Bildes ist ungültig.')
        try:
            if not isinstance(record.get('created'),str) or datetime.fromisoformat(record['created']).tzinfo is None:
                raise ValueError('Missing timestamp')
        except ValueError as error:raise InvalidDesign('Der gespeicherte Zeitpunkt ist ungültig.') from error
        if any(type(record.get(k)) is not int or record[k]<1 for k in ('width','height')):
            raise InvalidDesign('Die gespeicherten Bildmaße sind ungültig.')
        if not isinstance(record.get('sha256'),str) or not re.fullmatch(r'[a-f0-9]{64}',record['sha256']):
            raise InvalidDesign('Die Bildprüfung ist unvollständig.')
        return record

    def records(self):
        result=[];bad=0
        for path in (self.directory/'images/records').glob('*.json'):
            try:result.append(self.get(path.stem))
            except (ValueError,OSError):bad+=1
        return sorted(result,key=lambda v:v['created'],reverse=True),bad

    def as_asset(self,record):
        asset=dict(kind=record['kind'],id=record['id'],name=record['name'],representation='2d',source='saved',
                    variant=record['role'],created=record['created'],image='/library-images/'+record['id']+'/view.png',
                    thumbnail='/library-images/'+record['id']+'/thumb.png',width=record['width'],height=record['height'],snapshot=deepcopy(record))
        if record['kind']=='cards':
            asset.update(component='card-back-image-v1',model_id='card-back-image-v1',model_name='Kartenrücken',
                         family='back',family_name='Kartenrücken',record_role='back_artwork',editable=False,
                         usage='Wiederverwendbares Rückseitenmotiv; Kartenvorderseiten und Spielinhalte bleiben getrennt.')
        return asset

    def assets(self):return [self.as_asset(record) for record in self.records()[0]]

    def _write(self,record,raw):
        target=self._path(record['file']);target.parent.mkdir(parents=True,exist_ok=True)
        with target.open('xb') as out:out.write(raw)
        meta=self._path('images/records/'+record['id']+'.json');meta.parent.mkdir(parents=True,exist_ok=True)
        temporary=meta.with_suffix('.tmp')
        with temporary.open('x',encoding='utf-8') as out:json.dump(record,out,ensure_ascii=False,indent=2,allow_nan=False)
        temporary.rename(meta)
        return record

    def import_image(self,raw,filename,kind):
        if kind not in IMAGE_KINDS:raise InvalidDesign('Bitte eine passende Bildart wählen.')
        if not raw or len(raw)>MAX_BYTES:raise InvalidDesign('Bitte ein Bild mit höchstens 20 MB wählen.')
        image,fmt=decode(raw)
        clean=filename.replace('\\','/').split('/')[-1][:240] or 'Mein Bild'
        name=(Path(clean).stem or 'Mein Bild')[:100]
        identifier='image-'+uuid4().hex
        record=dict(schema=1,id=identifier,role='original',name=name,kind=kind,created=datetime.now(timezone.utc).isoformat(),
                    filename=clean,file='images/originals/'+identifier+FORMATS[fmt],format=fmt,width=image.width,height=image.height,
                    sha256=sha256(raw).hexdigest(),source_id=identifier,recipe=None)
        image.close()
        return self._write(record,raw)

    def _source(self,identifier):
        if isinstance(identifier,str) and identifier in self.existing:
            asset=self.existing[identifier];path=(ROOT/asset['snapshot']['asset']).resolve()
            if not path.is_relative_to(ROOT/'static'):raise InvalidDesign('Ungültige Bildquelle.')
            raw=path.read_bytes()
            if sha256(raw).hexdigest()!=asset['snapshot']['sha256']:
                raise InvalidDesign('Diese Bildquelle wurde inzwischen geändert. Bitte die Werkstatt neu öffnen.')
            image,fmt=decode(raw)
            return image,dict(source_id=identifier,name=asset['name'],filename=path.name,kind=asset['kind'],sha256=sha256(raw).hexdigest(),format=fmt)
        record=self.get(identifier)
        if record['role']=='variant':
            source_id=record.get('source_id')
            if source_id==identifier or (source_id not in self.existing and self.get(source_id)['role']!='original'):
                raise InvalidDesign('Die Originalzuordnung des Bildes ist ungültig.')
            return self._source(source_id)
        raw=self._path(record['file']).read_bytes()
        if sha256(raw).hexdigest()!=record['sha256']:raise InvalidDesign('Das Original wurde außerhalb der Werkstatt verändert.')
        image,fmt=decode(raw)
        return image,dict(source_id=record['id'],name=record['name'],filename=record['filename'],kind=record['kind'],sha256=record['sha256'],format=fmt)

    def info(self,identifier):
        image,info=self._source(identifier)
        record=self.get(identifier) if isinstance(identifier,str) and IMAGE_ID.fullmatch(identifier) else None
        w,h=image.size;image.close()
        width=min(w,1920,MAX_SIDE,math.floor(MAX_SIDE*w/h))
        recipe=dict(x=0,y=0,width=w,height=h,output_width=max(1,width))
        if record and record['role']=='variant':recipe=deepcopy(record['recipe'])
        return {**info,'width':w,'height':h,'name':record['name'] if record else info['name'],'kind':record['kind'] if record else info['kind'],
                'recipe':recipe,'selected_id':identifier,'role':record['role'] if record else 'existing',
                'image_url':'/image-sources/'+info['source_id']+'.png'}

    def source_preview(self,identifier):
        image,_=self._source(identifier);image.thumbnail((1600,1600),Image.Resampling.LANCZOS)
        result=png_bytes(image);image.close();return result

    def render(self,source_id,recipe,preview=False):
        image,info=self._source(source_id)
        try:
            recipe,out_h=validate_recipe(recipe,*image.size)
            cropped=image.crop((recipe['x'],recipe['y'],recipe['x']+recipe['width'],recipe['y']+recipe['height']))
            out_w=recipe['output_width']
            if preview:
                factor=min(1,1000/max(out_w,out_h));out_w=max(1,math.floor(out_w*factor+.5));out_h=max(1,math.floor(out_h*factor+.5))
            resized=cropped.resize((out_w,out_h),Image.Resampling.LANCZOS)
            raw=png_bytes(resized);cropped.close();resized.close()
            return raw,(out_w,out_h),info
        finally:image.close()

    def save_variant(self,payload):
        if not isinstance(payload,dict) or set(payload)!={'source_id','name','kind','recipe'}:
            raise InvalidDesign('Die Bildvariante ist unvollständig.')
        name=text_value(payload['name'],100,'Name der Bildvariante',True).strip()
        if payload['kind'] not in IMAGE_KINDS:raise InvalidDesign('Ungültige Bildart.')
        raw,(w,h),source=self.render(payload['source_id'],payload['recipe'])
        identifier='image-'+uuid4().hex
        record=dict(schema=1,id=identifier,role='variant',name=name,kind=payload['kind'],created=datetime.now(timezone.utc).isoformat(),
                    filename=name+'.png',file='images/variants/'+identifier+'.png',format='PNG',width=w,height=h,sha256=sha256(raw).hexdigest(),
                    source_id=source['source_id'],source_sha256=source['sha256'],recipe=deepcopy(payload['recipe']))
        return self._write(record,raw)

    def view(self,identifier,thumbnail=False):
        record=self.get(identifier)
        raw=self._path(record['file']).read_bytes()
        if sha256(raw).hexdigest()!=record['sha256']:raise InvalidDesign('Die gespeicherte Bilddatei wurde außerhalb der Werkstatt verändert.')
        image,_=decode(raw)
        image.thumbnail((480,360) if thumbnail else (1800,1800),Image.Resampling.LANCZOS)
        result=png_bytes(image);image.close();return result

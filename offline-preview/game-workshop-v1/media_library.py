"""Small free, local collection of matched lettering styles and purpose-based sounds."""
from copy import deepcopy
import json
from urllib.parse import urlsplit,parse_qs
from library_store import HERE,ROOT,InvalidDesign
from dice_library import digest

ASSETS=HERE/'assets/media'
FONT_STYLES=[
 ('chalk','Kreide auf Tafel','cabinsketch','Cabin Sketch',700,'Tafel · raue Kreideschrift','Für Quiztafeln, kurze Fragen und Überschriften.'),
 ('stone','In Stein gemeißelt','cinzel','Cinzel',700,'Stein · vertiefte Inschrift','Für Bretttitel, Wappen und kurze Überschriften.'),
 ('iron','In Eisen gestanzt','stardosstencil','Stardos Stencil',700,'Metall · eingeprägte Industrieschrift','Für Pulte, Marken und kurze Beschriftungen.'),
 ('stamp','Stempel & Schreibmaschine','specialelite','Special Elite',400,'Papier · unregelmäßiger Farbauftrag','Für Aufträge, Akten und kurze Hinweise.'),
 ('hand','Handschrift auf Papier','kalam','Kalam',400,'Papier · lockere Handschrift','Für Notizen und kurze Kartentexte.'),
 ('comic','Comic · kräftig & freundlich','fredoka','Fredoka',600,'Klare Comic-Schrift mit kleinem Schatten','Für Titel und auffällige Spielaktionen.'),
 ('clear','Klar & gut lesbar','inter','Inter',600,'Ruhige Grundschrift ohne Materialeffekt','Für Regeln, Fragen, Menüs und längere Texte.')]
SOUND_FAMILIES={'ui':'Klicks & Bedienung','table':'Karten, Würfel & Spielsteine','result':'Rundenbeginn, Sieg & Niederlage'}


class MediaLibrary:
    def __init__(self):
        self.records={};self.files={'/media-components/stage.js':HERE/'media-stage.js','/media-components/stage.css':HERE/'media-stage.css'}
        self.common=[HERE/'media-stage.html',HERE/'media-stage.css',HERE/'media-stage.js',HERE/'media_library.py']
        fonts=json.loads((ASSETS/'font-provenance.json').read_text(encoding='utf-8'))
        for key,name,font_key,font_name,weight,finish,usage in FONT_STYLES:
            provenance=fonts[font_key];entries=provenance['files']
            file=next(p for p in entries if p['file'].endswith('.ttf'));license_file=next(p for p in entries if p['file'].endswith(('OFL.txt','LICENSE.txt')))
            license_id='Apache-2.0' if font_key=='specialelite' else 'OFL-1.1'
            for row in entries:
                if digest(ROOT/row['file'])!=row['sha256']:raise InvalidDesign('Eine recherchierte Schriftquelle wurde geändert.')
            url='/media-assets/fonts/'+font_key+'/font.ttf';self.files[url]=ROOT/file['file']
            settings=dict(type='font',style=key,font_key=font_key,font=font_name,weight=weight,font_url=url,finish=finish,usage=usage)
            self.register('lettering-'+key,'fonts',key,name,'Schriftstil · '+name,finish,usage,settings,
                dict(author='Google Fonts / jeweilige Schriftgestalter',license=license_id,source=provenance['source'],license_file=license_file['file']),
                [ROOT/p['file'] for p in entries]+[ASSETS/'font-provenance.json'])
        sound_catalog=json.loads((ASSETS/'sounds.json').read_text(encoding='utf-8'))
        for sound in sound_catalog['sounds']:
            file=ROOT/sound['asset'];original=ROOT/sound['original_asset']
            if digest(file)!=sound['sha256'] or digest(original)!=sound['original_sha256']:raise InvalidDesign('Eine recherchierte Klangquelle wurde geändert.')
            url='/media-assets/sounds/'+sound['id']+'.wav';self.files[url]=file
            self.files['/media-assets/sounds/'+sound['id']+'.ogg']=original
            settings=dict(type='sound',url=url,duration=sound['duration'],waveform=sound['waveform'],default_volume=.45,usage=sound['usage'])
            self.register('sound-'+sound['id'],'sounds',sound['family'],sound['name'],SOUND_FAMILIES[sound['family']],SOUND_FAMILIES[sound['family']],sound['usage'],settings,
                dict(author='Kenney',license=sound['license'],source=sound['source'],original=sound['original_file'],license_file=sound['license_file'],transformation=sound['transformation']),
                [file,original,ROOT/sound['license_file'],ASSETS/'sounds.json'])

    def register(self,key,kind,family,name,model_name,family_name,usage,settings,provenance,paths):
        identifier='media-'+key
        snapshot=dict(schema=1,kind=kind,component='workshop-media-v1',settings=deepcopy(settings),provenance=deepcopy(provenance),
            parameters=dict(text='Inhalt der späteren Beschriftung',size='Proportionale Gesamtgröße') if kind=='fonts' else dict(event='Einsatz im späteren Spiel',volume='Wiedergabelautstärke'),
            matched_style=kind=='fonts',editor_review='deferred',game_integration=False,
            evidence=[dict(path=p.relative_to(ROOT).as_posix(),sha256=digest(p)) for p in sorted(set(self.common+paths))])
        self.records[identifier]=dict(id=identifier,kind=kind,name=name,source='preset',game='',games=[],family=family,family_name=family_name,
            model_id='media-'+kind+'-'+family+'-v1',model_name=model_name,component='workshop-media-v1',canonical=False,
            record_role='matched_lettering_style' if kind=='fonts' else 'sound_cue',representation='2d',usage=usage,editable=False,
            preview='/api/media/'+identifier+'/preview',preview_width=640,preview_height=400,snapshot=snapshot)

    def assets(self):return deepcopy(list(self.records.values()))

    def validate_sources(self,identifier):
        asset=self.records.get(identifier)
        if asset is None:raise InvalidDesign('Dieses Schrift- oder Klangbeispiel ist nicht registriert.')
        for entry in asset['snapshot']['evidence']:
            if digest(ROOT/entry['path'])!=entry['sha256']:raise InvalidDesign('Die Medienquelle wurde geändert. Bitte die Werkstatt neu laden.')
        return asset

    def preview(self,identifier,interactive=False):
        asset=self.validate_sources(identifier)
        cfg=dict(settings=asset['snapshot']['settings'],name=asset['name'],interactive=interactive)
        raw=json.dumps(cfg,ensure_ascii=False).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
        return (HERE/'media-stage.html').read_text(encoding='utf-8').replace('<!--config-->',raw)

    def file_path(self,path):return self.files.get(path)

    def http_get(self,handler,path):
        if not path.startswith('/api/media/'):return False
        if not path.endswith('/preview'):raise InvalidDesign('Unbekannte Medienvorschau.')
        query=parse_qs(urlsplit(handler.path).query)
        raw=self.preview(path.removeprefix('/api/media/').removesuffix('/preview'),query.get('interactive')==['1']).encode('utf-8')
        handler.send_response(200);handler.send_header('Content-Type','text/html; charset=utf-8');handler.send_header('Content-Length',str(len(raw)))
        handler.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; media-src 'self'; connect-src 'self'; frame-ancestors 'self'; object-src 'none'; base-uri 'none'; form-action 'none'")
        handler.end_headers();handler.wfile.write(raw);return True

    def report(self):
        return dict(schema=1,checked_on='2026-10-27',fonts=[dict(id=a['id'],name=a['name'],settings=a['snapshot']['settings'],provenance=a['snapshot']['provenance']) for a in self.assets() if a['kind']=='fonts'],
            sounds=[dict(id=a['id'],name=a['name'],family=a['family_name'],settings=a['snapshot']['settings'],provenance=a['snapshot']['provenance']) for a in self.assets() if a['kind']=='sounds'],
            rule='Kleine Auswahl passender Schrift-/Oberflächenkombinationen und kurzer Klänge nach Spielzweck. Keine universelle Effektmatrix.',
            limits=['Alte Buttonrezepte, Schriftauswahl und Klangzuordnungen unverändert lesbar.','Keine automatische Umstellung bestehender Spiele oder Entwürfe.','Klangdateien technisch geprüft; persönliche Klang-/Gestaltungsabnahme und Editoroptionen folgen später.','Originalklänge unverändert erhalten; lokale WAVs nur in Pegel und kurzen Randblenden angepasst.','Schriftdateien lokal; kein Google-Fonts-Ladedienst im Browser nötig.'])

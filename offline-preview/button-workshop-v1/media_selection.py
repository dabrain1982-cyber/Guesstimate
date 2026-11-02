"""Use the curated local workshop media without replacing legacy editor IDs."""
from copy import deepcopy
from pathlib import Path
import json,re,sys

ROOT=Path(__file__).resolve().parents[2]
WORKSHOP=ROOT/'offline-preview/game-workshop-v1'
if str(WORKSHOP) not in sys.path:sys.path.append(str(WORKSHOP))
from media_library import MediaLibrary, ASSETS


def build_selection():
    media=MediaLibrary();fonts=[];sounds=[];files={}
    for asset in media.assets():
        s=asset['snapshot']['settings']
        if asset['kind']=='fonts':
            fonts.append(dict(value='media-'+s['style'],style=s['style'],name=asset['name'],font=s['font'],weight=s['weight'],finish=s['finish'],source_id=asset['id']))
            files[s['font_url']]=media.file_path(s['font_url'])
    catalog=json.loads((ASSETS/'sounds.json').read_text(encoding='utf-8'))
    groups={'ui':'Klicks & Bedienung','table':'Karten, Würfel & Spielsteine','result':'Rundenbeginn, Sieg & Niederlage'}
    for sound in catalog['sounds']:
        identifier='media-'+sound['id'];file=identifier+'.wav'
        sounds.append(dict(id=identifier,name=sound['name'],group=groups[sound['family']],description=sound['usage'],file=file,
            author='Kenney',source=sound['source'],license=sound['license'],license_url='https://creativecommons.org/publicdomain/zero/1.0/',
            duration=sound['duration'],button_offset=0,button_duration=sound['duration'],media_short=True,
            sha256=sound['sha256'],source_id='media-sound-'+sound['id']))
        files['/assets/audio/'+file]=ROOT/sound['asset']
        files['/button-editor/assets/audio/'+file]=ROOT/sound['asset']
    return dict(fonts=fonts,sounds=sounds),files


SELECTION,FILES=build_selection()


def extend_catalog(catalog):
    catalog['button_media']=deepcopy(SELECTION)
    by_key={field['key']:field for field in catalog['fields']}
    by_key['font']['options'].extend([[r['value'],r['name']+' · '+r['font']] for r in SELECTION['fonts']])
    by_key['font']['options'].extend([['letter-'+r['style'],r['font']+' · '+r['name']] for r in SELECTION['fonts']])
    by_key['sound']['options'].extend([[r['id'],r['name']] for r in SELECTION['sounds']])
    catalog['fields'].extend([dict(key='font_bold',group='lettering',label='Fett',type='checkbox'),
                              dict(key='font_italic',group='lettering',label='Kursiv',type='checkbox')])
    catalog['sounds'].extend(deepcopy(SELECTION['sounds']))
    return catalog


def matched_css():
    """Derive the same seven finishes, proportional to the canonical button's type unit."""
    source=(WORKSHOP/'media-stage.css').read_text(encoding='utf-8')
    def declarations(selector):
        match=re.search(r'(?:^|\n)'+re.escape(selector)+r'\{([^}]+)\}',source)
        if not match:raise ValueError('Der passende Schriftstil fehlt: '+selector)
        return dict(part.split(':',1) for part in match[1].split(';') if ':' in part)
    def proportional(value):return re.sub(r'(-?\d*\.?\d+)px',lambda m:'calc(var(--button-face-font, 23px) * '+m[1]+' / 54)',value)
    rules=re.findall(r'@font-face\{[^}]+\}',source)
    rules += ["@font-face{font-family:'Workshop Cabin Sketch';src:url('/assets/fonts/CabinSketch-Regular.ttf');font-weight:400;font-style:normal;font-display:block}",
              "@font-face{font-family:'Workshop Cabin Sketch';src:url('/media-assets/fonts/cabinsketch/font.ttf');font-weight:700;font-style:normal;font-display:block}",
              "@font-face{font-family:'Workshop Stardos Stencil';src:url('/assets/fonts/StardosStencil-Regular.ttf');font-weight:400;font-style:normal;font-display:block}",
              "@font-face{font-family:'Workshop Stardos Stencil';src:url('/media-assets/fonts/stardosstencil/font.ttf');font-weight:700;font-style:normal;font-display:block}"]
    for font in SELECTION['fonts']:
        key=font['style'];v=declarations('.finish-'+key)
        heading=re.search(r'(?:^|\n)\.finish-'+key+r' h1\{([^}]+)\}',source)
        h=dict(p.split(':',1) for p in heading[1].split(';') if ':' in p) if heading else {}
        variables={'family':v['font-family'],'weight':v.get('font-weight','400'),'ink':v['color'],
            'background':proportional(v['background']),'border':v['border-color'],'surface-shadow':proportional(v.get('box-shadow','none')),
            'text-shadow':proportional(h.get('text-shadow',v.get('text-shadow','none'))),'rotation':h.get('transform','none')}
        rules.append('[data-media-font="'+key+'"]{'+''.join('--matched-'+k+':'+value+';' for k,value in variables.items())+'}')
        # The editor's new lettering choices reuse these fonts/effects only.
        rules.append('[data-letter-font="'+key+'"]{'+''.join('--matched-'+k+':'+variables[k]+';' for k in ('family','weight','text-shadow','rotation'))+'}')
    rules.append('''
[data-letter-font="chalk"]{--matched-family:'Workshop Cabin Sketch',sans-serif}
[data-letter-font="iron"]{--matched-family:'Workshop Stardos Stencil',serif}
.preview-button[data-media-font]::before{background:var(--matched-border)}
.preview-button[data-media-font] .comic-button-face{background:var(--matched-border);color:var(--matched-ink)}
.preview-button[data-media-font] .comic-button-face::before{background:var(--matched-background);box-shadow:var(--matched-surface-shadow);background-position:center;background-size:auto}
.preview-button[data-media-font] .comic-button-face::after{display:none}
.preview-button[data-media-font][data-lettering] .comic-button-label{font-family:var(--matched-family);font-weight:var(--matched-weight);color:var(--matched-ink);-webkit-text-fill-color:currentColor;text-shadow:var(--matched-text-shadow);letter-spacing:normal;text-transform:none;background:none;transform:var(--matched-rotation);font-synthesis:none}
.material-surface[data-media-font]{font-family:var(--matched-family);font-weight:var(--matched-weight);color:var(--matched-ink);background:var(--matched-background);border-color:var(--matched-border);box-shadow:var(--matched-surface-shadow)}
.preview-button[data-letter-font][data-lettering] .comic-button-label{font-family:var(--matched-family);font-weight:var(--matched-weight);color:var(--own-ink);-webkit-text-fill-color:currentColor;text-shadow:var(--matched-text-shadow);letter-spacing:normal;text-transform:none;background:none;transform:var(--matched-rotation);font-synthesis:none}
.preview-button[data-letter-font][data-ink-color="auto"] .comic-button-label{color:var(--surface-ink)}
.material-surface[data-letter-font]{font-family:var(--matched-family);font-weight:var(--matched-weight)}
''')
    return '\n'.join(rules)

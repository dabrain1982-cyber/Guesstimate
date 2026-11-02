"""Shared project wishes, with original examples; never additional element assets."""
from copy import deepcopy
from hashlib import sha256
from library_store import ROOT, InvalidDesign

BUTTON='offline-preview/button-workshop-v1/'
WORKSHOP='offline-preview/game-workshop-v1/'


class PropertyCatalog:
    def __init__(self,button_catalog):
        self.materials={}
        self.views=[
            dict(id='flat',name='2D · flache Oberfläche',description='Ein fester Bildaufbau. Passend für Fragenfenster, Menüs und flache Spielflächen.',example='boards-2d-playtable',note='Originale Playtable-Fläche'),
            dict(id='depth',name='2,5D · fester räumlicher Blick',description='Räumliche Elemente aus einem festen schrägen Blickwinkel. 2,5D ist eine Ansicht des 3D-Bausteins.',example='boards-3d-conquest',note='Dasselbe räumliche Conquest-Brett'),
            dict(id='spatial',name='3D · räumliche Ansicht',description='Räumliche Elemente mit veränderbarer Kamera. Bewegung und Physik werden separat gewählt.',example='rooms-conquest',note='Originaler Conquest-Raum; Ansicht wechseln in der Vorschau')]
        button_paths=[BUTTON+p for p in ('catalog.json','materials.css','renderer.js','geometry.js')]
        colors={'wood':'#a36b38','wood-aged':'#23150e','stone':'#536460','metal':'#899ba2','plain':'#315b47','gradient':'#315b47','translucent':'#365d6e'}
        descriptions={
            'wood':('Holz','Holzmaserung und warme Kanten.','Buttons; räumlicher Conquest-Tisch','Farbe, Maserung und Glanz gehören zur jeweiligen Komponente.'),
            'wood-aged':('Altes dunkles Nussbaumholz','Dunkle Holzmaserung mit Patina und Gebrauchsspuren.','Black-Jack-Buttons','Eigene Oberfläche passend zum alten Tisch; bestehendes helles Holz bleibt erhalten.'),
            'stone':('Stein & Tafel','Raue Stein- oder Schieferoberfläche.','Buttons; feste Stein-/Kreideschriftstile','Kreide und Steininschrift sind passende feste Schriftstile.'),
            'metal':('Metall','Metallstruktur mit zurückhaltenden Lichtkanten.','Buttons; fester Metall-Schriftstil','Die eingeprägte Schrift verwendet ihren abgestimmten Metallstil.'),
            'plain':('Farbfläche','Ruhige Farbe ohne Materialstruktur.','Flächige Bedien- und Anzeigeflächen','Farbe ist eine Eigenschaft; ein anderer Farbwert erzeugt kein neues Modell.'),
            'gradient':('Farbverlauf','Zwei Farben auf derselben Fläche.','Grafische Buttons und Flächen','Zweite Farbe ist eine Eigenschaft derselben Fläche.'),
            'translucent':('Durchscheinend','Eine Fläche lässt ihren Hintergrund durchscheinen.','Überlagerte Bedienflächen','Durchscheinen ist Deckkraft, keine zusätzliche Glassimulation.')}
        options=next(field['options'] for field in button_catalog['fields'] if field.get('key')=='material')
        for identifier,_ in options:
            name,description,usage,note=descriptions[identifier]
            recipe=dict(schema_version=2,settings=deepcopy(button_catalog['defaults']),contour=dict(template='comic',points=[dict(x=x,y=y,round=r) for x,y,r in button_catalog['contours']['comic']]))
            recipe['settings'].update(material=identifier,style='natural',accent=colors[identifier],label=name,lettering='plain',finish='satin',wear=12,depth=3)
            paths=button_paths+([BUTTON+'assets/walnut-aged-v1.webp'] if identifier=='wood-aged' else [])
            self.register(identifier,name,description,usage,note,dict(type='button',recipe=recipe),paths)
        self.register('felt','Filz','Weiche Spielfläche für Karten und Würfel.','Vorhandene Playtable-Fläche','Die Struktur gehört zum vorhandenen Tischbild; sie ist hier keine austauschbare 3D-Textur.',dict(type='asset',id='boards-2d-playtable'),['static/card-table.css','static/card-table-felt-v1.png'])
        self.register('paper','Papier','Papierartige Zettel für Einstellungen, Hinweise und Notizen.','Ursprünglicher Perfect-Einstellungszettel','Schreibmaschine und Handschrift bleiben passende feste Schriftstile.',dict(type='model',model_id='window-perfect-settings'),['templates/nerd_mode.html','static/stormseeds-perfect.css'])
        self.register('cardstock','Bedruckter Karton','Bedruckte Kartenfläche mit Vorder- und Rückseite.','Freigegebener flacher Kartenbaustein','Aufdruck und Kartensatz sind Eigenschaften; Fragen bleiben Daten an Fenstern.',dict(type='asset',id='cards-component-display'),[WORKSHOP+'card_library.py','offline-preview/card-comparison-v1/assets/kenney/cardHearts7.png'])
        for identifier,refs in {'stone':['media-lettering-chalk','media-lettering-stone'],'metal':['media-lettering-iron'],'paper':['media-lettering-hand','media-lettering-stamp']}.items():
            self.materials[identifier]['lettering']=refs

    def register(self,identifier,name,description,usage,note,preview,paths):
        self.materials[identifier]=dict(id=identifier,name=name,description=description,usage=usage,note=note,preview=preview,lettering=[],
            evidence=[dict(path=p,sha256=sha256((ROOT/p).read_bytes()).hexdigest()) for p in sorted(set(paths))])

    def catalog(self,assets):
        result=deepcopy(list(self.materials.values()));by_id={a['id']:a for a in assets}
        for row in result:
            preview=row['preview']
            if preview['type']=='model':
                preview['id']=next(a['id'] for a in assets if a.get('model_id')==preview['model_id'])
            if preview['type']!='button' and preview['id'] not in by_id:raise InvalidDesign('Ein Materialbeispiel fehlt im aktuellen Bestand.')
            if any(ref not in by_id for ref in row['lettering']):raise InvalidDesign('Ein verknüpfter Schriftstil fehlt.')
        if any(view['example'] not in by_id for view in self.views):raise InvalidDesign('Ein Ansichtsbeispiel fehlt im aktuellen Bestand.')
        return dict(schema=1,materials=result,views=deepcopy(self.views),
            rule='Materialien und Ansicht sind Projekteigenschaften. Die Auswahl hält Wünsche fest und verändert keine Originaldarstellung.',
            motion=[dict(id='pieces',name='Figuren',description='Verschieben innerhalb derselben Figur; keine neue Figur pro Position.'),
                    dict(id='dice',name='Würfel',description='Vorhandene Physikwürfel und flache Würfelanzeige bleiben zwei Varianten. Physik gehört zu den räumlichen Würfeln.'),
                    dict(id='cards',name='Karten',description='Bewegliche 3D-Karten und flache Anzeigekarten bleiben zwei Grundbausteine.')])

    def select(self,identifiers,previous=()):
        if not isinstance(identifiers,list) or len(identifiers)>len(self.materials):raise InvalidDesign('Bitte eine kleine Materialauswahl verwenden.')
        choices={**deepcopy(self.materials),**{entry['id']:deepcopy(entry) for entry in previous}}
        result=[];seen=set()
        for identifier in identifiers:
            if not isinstance(identifier,str) or identifier not in choices or identifier in seen:raise InvalidDesign('Ungültige oder doppelte Materialwahl.')
            seen.add(identifier);entry=choices[identifier]
            if identifier not in {p['id'] for p in previous}:
                for source in entry['evidence']:
                    if sha256((ROOT/source['path']).read_bytes()).hexdigest()!=source['sha256']:raise InvalidDesign('Die Materialquelle hat sich geändert. Bitte die Werkstatt neu laden.')
            # A wish freezes its source definition, never an extra asset or altered component.
            result.append({k:deepcopy(v) for k,v in entry.items() if k not in ('preview','lettering')})
        return result


def validate_surfaces(value):
    if not isinstance(value,list) or len(value)>32:raise InvalidDesign('Ungültige gespeicherte Materialwünsche.')
    seen=set()
    for row in value:
        if not isinstance(row,dict) or not isinstance(row.get('id'),str) or row['id'] in seen or not isinstance(row.get('name'),str) or not isinstance(row.get('evidence'),list):
            raise InvalidDesign('Unvollständige gespeicherte Materialwünsche.')
        seen.add(row['id'])
    return value

"""The growing element registry, independent of projects and rendering choices."""
from hashlib import sha256
from library_store import ROOT

ELEMENT_KINDS = {
    'fonts': dict(title='Schriften',icon='Aa',editor=None,description='Vorhandene Schriftstile und lokal gespeicherte Schriftdateien ansehen und vergleichen.'),
    'sounds': dict(title='Klänge',icon='♪',editor=None,description='Vorhandene kurze Klänge lokal probehören und für spätere Recherchen vergleichen.'),
    'buttons': dict(title='Buttons',icon='▰',editor='button',description='Vorhandene Buttonmodelle und eigene Entwürfe gestalten. Die Einstellungen richten sich nach dem Aufbau des ausgewählten Buttons.'),
    'windows': dict(title='Fenster',icon='▣',editor=None,description='Fenster aus den vorhandenen Spielen mit ihren konkreten Einsatzorten und Zuständen ansehen.'),
    'inputs': dict(title='Eingaben',icon='☷',editor=None,description='Text- und Zahlenfelder, Auswahlfelder, Schalter, Regler sowie Zuordnen und Sortieren aus den Spielen ansehen.'),
    'indicators': dict(title='Anzeigen',icon='◉',editor=None,description='Punkte, Timer, Fortschritt, Status, Zähler und Ergebnisse aus den Spielen ansehen. Werte und Zeiten sind feste Beispiele.'),
    'players': dict(title='Spieleranzeigen & Pulte',icon='♙',editor=None,description='Profilfenster, Lobbyplätze, Porträts, Ranglisteneinträge und Spielerpulte aus den Spielen ansehen.'),
    'board': dict(title='Bretter',icon='▦',editor=None,description='Vorhandene Spielbretter, Spielflächen und gespeicherte Entwürfe ansehen und vergleichen.'),
    'pieces': dict(title='Figuren & Spielsteine',icon='♟',editor=None,description='Die vorhandene Conquest-Truppenmarke, bisherige Werkstattvorlagen und gespeicherte Entwürfe ansehen.'),
    'background': dict(title='Hintergründe',icon='◒',editor=None,description='Vorhandene Hintergrundbilder, Raumkulissen und gespeicherte Bildvarianten ansehen.'),
    'titles': dict(title='Titelbilder',icon='▣',editor=None,description='Vorhandene Spielmotive, Logos und gespeicherte Bildvarianten ansehen.'),
    'icons': dict(title='Icons',icon='✦',editor=None,description='Vorhandene Symbolsätze und gespeicherte Bildvarianten ansehen.'),
    'flyers': dict(title='Flyer',icon='▤',editor=None,description='Vorhandene Flyer und Spielkacheln mit ihren ursprünglichen Bildern und Beschriftungen ansehen.'),
    'lobby': dict(title='Lobbys & Übersichten',icon='♧',editor=None,description='Lobbys, Übersichten und gespeicherte Entwürfe mit konkreten Spielvarianten ansehen.'),
    'dice': dict(title='Würfel',icon='⚄',editor=None,description='Räumliche Würfeltisch-Würfel mit Physik und flache Würfelanzeigen aus Conquest ansehen.'),
    'cards': dict(title='Karten',icon='▱',editor=None,description='Vorhandene Kartensätze und gespeicherte Entwürfe ansehen; einzelne Karten innerhalb ihres Satzes durchblättern.'),
    'avatars': dict(title='Avatare',icon='♙',editor=None,description='Vorhandene Avatarbilder und gespeicherte Entwürfe ansehen.')
}

PRESENTATION = {
    'mode': {'label':'Darstellung','options':{
        'undecided':'Noch offen · im Interview klären',
        'flat':'Flache Oberfläche · feste Ansicht',
        'depth':'Feste Ansicht mit räumlicher Wirkung',
        'spatial':'Räumliche Ansicht mit Kamera'}},
    'shadows': {'label':'Licht und Schatten','options':{'undecided':'Noch offen','yes':'Gewünscht','no':'Nicht benötigt'}},
    'pieces': {'label':'Bewegung von Figuren','options':{'undecided':'Noch offen','yes':'Gewünscht','no':'Nicht benötigt'}},
    'dice': {'label':'Bewegung von Würfeln','options':{'undecided':'Noch offen','yes':'Gewünscht','no':'Nicht benötigt'}},
    'cards': {'label':'Bewegung von Karten','options':{'undecided':'Noch offen','yes':'Gewünscht','no':'Nicht benötigt'}}
}


def existing_assets(catalogs):
    assets=[]
    def add(kind,identifier,name,path):
        file=ROOT/'static'/path
        if not file.is_file():return
        assets.append(dict(kind=kind,id=identifier,name=name,representation='2d',source='existing',image='/shared/'+path,
                           snapshot=dict(id=identifier,name=name,asset='static/'+path,sha256=sha256(file.read_bytes()).hexdigest())))
    for entry in [catalogs['DEFAULT_BACKGROUND'],*catalogs['BACKGROUND_CATALOG']]:
        add('background','background-'+entry['id'],entry['name'],entry['asset'])
    for key,name,path in [('perfect','Perfect · Clubraum','stormseeds-perfect-clubroom-table-v2.png'),
                          ('cards','Kartenraum','card-tables-background-v1.png'),
                          ('dice','Würfelraum','dice-table-background-v2.png'),
                          ('conquest','Conquest-Raum','conquest-lobby-background-v1.png')]:
        add('background','background-room-'+key,name,path)
    for entry in [catalogs['DEFAULT_AVATAR'],*catalogs['AVATAR_CATALOG']]:
        add('avatars','avatar-'+entry['id'],entry['name'],'avatars/'+entry['stage_asset'])
    return assets

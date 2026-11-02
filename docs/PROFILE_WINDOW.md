# Gemeinsames Profilfenster

Die vollständigen Profilfenster verwenden das Makro `profile_window` aus
`templates/_profile_window.html`. Welche Ansichten dieses Fenster, ein kompaktes
Porträt oder keine zusätzliche Avataranzeige erhalten, legt
[BAUKASTEN.md](BAUKASTEN.md) fest. Die kompakte Variante ist separat in
[PLAYER_PORTRAIT.md](PLAYER_PORTRAIT.md) umgesetzt und bei Conquest angebunden.
Laufende Quizfragen bleiben ohne neue Avatare.
Die Innenkomposition und alle 14 Pult-Feldlagen stehen ausschließlich in
`static/profile-window.css`. `static/profile-stage-v1.js` passt die Beschriftung
an die vorhandenen Felder an, auch nach späterem Einfügen oder Aktualisieren.

Avatar, Hintergrund, Spruch und Pult werden aus `cosmetics` gelesen. Die Szene
behält immer ihr Verhältnis 43:57. Spiele setzen die Breite des gesamten Fensters;
sie verändern keine Positionen oder Proportionen der inneren Bestandteile.
Die Fläche darunter ist davon unabhängig.

## Anzeigen und Inhalte

| Parameter | Bedeutung |
|---|---|
| `podium_fields` | Optionales Dictionary mit `name`, `value`, `label`, `icon`. Fehlender Name verwendet den Spielernamen. Zahlen werden wie bisher mit deutschen Tausenderpunkten formatiert; vorbereitete Texte sind ebenfalls möglich. |
| `player_status` | Text oder Dictionary mit `text` und `tone`. Verfügbare Darstellungen: `neutral`, `ready`, `active`, `waiting`, `out`. |
| `content_items` | Liste aus Dictionaries mit `key`, `label`, `value` und optional `unit`. Die gemeinsame Komponente ordnet diese Werte an. |
| `content_size` | `auto` wächst mit dem Inhalt. `compact`, `standard` und `expanded` bieten drei mit der Fensterbreite skalierende Höhen; längere Inhalte scrollen innerhalb der Zusatzfläche. |
| `content_height` | Optional eine nicht negative Pixelzahl. Begrenzt die Zusatzfläche auf diese Höhe; längere Inhalte scrollen innerhalb der Fläche. `0` blendet die Zusatzfläche aus. |
| `content_label` | Zugängliche Bezeichnung der Zusatzfläche, beispielsweise `Eigene Karten`. |
| Jinja-`caller` | Zusätzlicher Inhalt wie Karten oder Bedienelemente, innerhalb derselben gemeinsamen Zusatzfläche. |

Ohne neue Parameter bleibt das bisherige Verhalten erhalten: iKühe und Shoplink,
bei `show_details=True` die Pokale. `game_points` bleibt als kompatibler älterer
Aufruf für Perfect erhalten. Spielewerte führen nicht zum Shop.
`show_details=False` unterdrückt die Standardpokale; ausdrücklich übergebene neue
Inhalte erscheinen trotzdem. Eine eingestellte Größe kann auch eine zunächst
leere Zusatzfläche reservieren.

## Beispiel mit Status und Werten

```jinja
{% from "_profile_window.html" import profile_window with context %}
{{ profile_window(
    player.cosmetics, {}, show_edit=False, show_details=False,
    player_name=player.display_name, instance_id='player-' ~ player.id,
    podium_fields={'value': player.score, 'label': 'Punkte'},
    player_status={'text': 'am Zug', 'tone': 'active'},
    content_items=[
        {'key': 'countries', 'label': 'Länder', 'value': player.country_count},
        {'key': 'armies', 'label': 'Truppen', 'value': player.army_count}
    ],
    content_size='standard'
) }}
```

## Eigene Karten oder Bedienflächen

```jinja
{% call profile_window(
    player.cosmetics, {}, show_edit=False, show_details=False,
    player_name=player.display_name, instance_id='hand-' ~ player.id,
    podium_fields={'value': player.score, 'label': 'Punkte'},
    content_size='expanded', content_label='Eigene Karten'
) %}
  {% include '_own_cards.html' %}
  <button type="button" data-open-inventory>karten ansehen</button>
{% endcall %}
```

Die Karten und Aktionen liefert das jeweilige Spiel. Es übergibt ausschließlich
für den Betrachter bestimmte Daten; das Profilfenster entscheidet keine Spielrechte.
Texte werden automatisch maskiert. Es ist kein `safe` für Spielertexte nötig.

## Einbindung und Aktualisierung

Die gemeinsame Basisvorlage und Perfect laden das neue Stylesheet bereits.
Eigenständige zukünftige Spielseiten laden die lokalen Schriften aus
`typography-v1.css`, anschließend `profile-window.css`, die gemeinsamen
`ui-conventions.css` und `profile-stage-v1.js` mit `defer`.

`instance_id` ist je dargestelltem Fenster eindeutig. Für Textaktualisierungen
stehen `data-profile-field="name"`, `data-profile-field="value"` und
`data-profile-value` zur Verfügung. Status und Zusatzfläche besitzen ebenfalls
die gemeinsamen Kennzeichnungen `data-profile-status`, `data-profile-content`
und `data-profile-stat`. Neue Fenster werden weiterhin mit demselben Makro
gerendert; ein zweiter HTML-Aufbau im Spielskript ist nicht nötig.

Textänderungen, nachgeladene Fenster und Größenänderungen werden automatisch
berücksichtigt. Bei Bedarf kann ein Spiel `window.ProfileWindow.refresh()`
oder das bestehende Ereignis `profile:updated` auslösen.

Dieser Baustein wird bereits von der Startseite, dem Profil, den Standardlobbys,
perfect und den Würfelspielen verwendet. Die Standardlobbys sind in Punkt 5
angebunden worden. Die kompakte Variante ist bei Conquest separat angeschlossen.
Weitere Spielwerte-Anbindungen bleiben spätere Arbeiten; eine allgemeine
Avatarpflicht für alle Spielansichten besteht nicht. Bestehende Buttons und
Spielanzeigen gelten gemäß [GESTALTUNGSPLAN.md](GESTALTUNGSPLAN.md) noch nicht
als fertige Comicgestaltung.

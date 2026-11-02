# Vorhandener Baukasten: Komponenten, Assets und Werkzeuge

Stand: 25.10.2026 · Nur lokaler Dateibestand in `D:\Guesstimate`.

Die Einsatzentscheidungen stehen in [BAUKASTEN.md](BAUKASTEN.md). Diese Erfassung
liest die Katalogzuordnungen aus `app.py` ohne Anwendungsimport und prüft die
Existenz der verlinkten Dateien. Sie aktiviert, verschiebt oder ersetzt keine Assets.
„Vorhanden“ bedeutet weder automatisch eine gemeinsame Komponente noch eine neue
visuelle oder rechtliche Freigabe. Der Server wurde nicht abgefragt.

Die ergänzende [Dateiliste](BAUKASTEN_DATEIEN.json) enthält zu jedem hier
verlinkten Quellasset bzw. Baustein Dateigröße, SHA-256 und bei Bildern die
gelesenen Maße. Sie ist ein Dokumentationsstand und wird vom Spiel nicht geladen.

## Bestandsstatus

| Status | Bedeutung |
|---|---|
| Gemeinsamer Baustein | Eine von mehreren Ansichten benutzte Implementierung ist vorhanden. |
| Im Spiel gebunden | Datei/Funktion vorhanden, aber noch kein eigenständiges allgemeines Werkzeug. |
| Ältere Darstellung / weitere Variante | Vorhanden und teilweise noch benutzt; kein neuer Standard durch bloßes Vorhandensein. |
| Geplant | Einsatz festgelegt, gemeinsame Implementierung noch offen. |
| Gestaltung offen | Funktionaler Bestand vorhanden; Comicform, räumliche Tiefe und Detailgestaltung noch nicht abschließend erarbeitet. |
| Herkunftsnachweis offen | Datei vorhanden; hier keine zusätzliche Nutzungserlaubnis aus Paketnamen oder früheren Aussagen abgeleitet. |

## 1. Profile und registrierte Grafikfamilien

Im Code registriert: **19 Avatare**,
**14 Pultfamilien**,
**11 Profilhintergründe** und
**40 auswählbare Sprüche** plus neutraler Standardtext.

Die Dateispalten sind die tatsächlichen Katalogfelder. Ein Nutzer wählt die ID;
die jeweilige Komponente bestimmt das dafür registrierte Assetfeld. Gleichnamige
Entwürfe oder andere Versionsdateien werden nicht automatisch ausgewählt.

### Avatare

Quelle: `AVATAR_CATALOG` und `DEFAULT_AVATAR` in `app.py`.
Für das vollständige Profilfenster gilt `stage_asset`. Die zentrale
Porträtvariante verwendet einen Ausschnitt desselben ausgerüsteten Motivs;
siehe [PLAYER_PORTRAIT.md](PLAYER_PORTRAIT.md).

| ID | Figur | `stage_asset` – Profilbühne | Weiteres registriertes Bild / öffentliche Standardvariante |
|---|---|---|---|
| `a00` | Start-Avatar | [starter-neutral.svg](../static/avatars/starter-neutral.svg) | [starter-neutral-public.svg](../static/avatars/starter-neutral-public.svg) |
| `a01` | Kea | [a01-kea.webp](../static/avatars/stage/a01-kea.webp) | – |
| `a02` | Wasserschwein | [a02-wasserschwein.webp](../static/avatars/stage/a02-wasserschwein.webp) | [a02-wasserschwein.webp](../static/avatars/a02-wasserschwein.webp) |
| `a03` | Wanderfalke | [a03-wanderfalke.webp](../static/avatars/stage/a03-wanderfalke.webp) | [a03-wanderfalke.webp](../static/avatars/a03-wanderfalke.webp) |
| `a04` | Faultier | [a04-faultier.webp](../static/avatars/stage/a04-faultier.webp) | [a04-faultier.webp](../static/avatars/a04-faultier.webp) |
| `a05` | Waschbär | [a05-waschbaer.webp](../static/avatars/stage/a05-waschbaer.webp) | [a05-waschbaer.webp](../static/avatars/a05-waschbaer.webp) |
| `a06` | Oktopus | [a06-oktopus.webp](../static/avatars/stage/a06-oktopus.webp) | [a06-oktopus.webp](../static/avatars/a06-oktopus.webp) |
| `a07` | Ziege | [a07-ziege.webp](../static/avatars/stage/a07-ziege.webp) | [a07-ziege.webp](../static/avatars/a07-ziege.webp) |
| `a08` | Krähe | [a08-kraehe.webp](../static/avatars/stage/a08-kraehe.webp) | [a08-kraehe.webp](../static/avatars/a08-kraehe.webp) |
| `a09` | Fennek | [a09-fennek.webp](../static/avatars/stage/a09-fennek.webp) | [a09-fennek.webp](../static/avatars/a09-fennek.webp) |
| `a10` | Wombat | [a10-wombat.webp](../static/avatars/stage/a10-wombat.webp) | [a10-wombat.webp](../static/avatars/a10-wombat.webp) |
| `a11` | Gans | [a11-gans.webp](../static/avatars/stage/a11-gans.webp) | [a11-gans.webp](../static/avatars/a11-gans.webp) |
| `a12` | Fangschreckenkrebs | [a12-fangschreckenkrebs.webp](../static/avatars/stage/a12-fangschreckenkrebs.webp) | [a12-fangschreckenkrebs.webp](../static/avatars/a12-fangschreckenkrebs.webp) |
| `a13` | Axolotl | [a13-axolotl.webp](../static/avatars/stage/a13-axolotl.webp) | [a13-axolotl.webp](../static/avatars/a13-axolotl.webp) |
| `a14` | Somnus | [a14-somnus-cutout-v2.png](../static/avatars/stage/a14-somnus-cutout-v2.png) | [a14-somnus-cutout-v2.png](../static/avatars/a14-somnus-cutout-v2.png) |
| `a15` | Ember | [a15-ember-cutout-v2.png](../static/avatars/stage/a15-ember-cutout-v2.png) | [a15-ember-cutout-v2.png](../static/avatars/a15-ember-cutout-v2.png) |
| `a16` | Myrli | [a16-myrli-cutout-v2.png](../static/avatars/stage/a16-myrli-cutout-v2.png) | [a16-myrli-cutout-v2.png](../static/avatars/a16-myrli-cutout-v2.png) |
| `a17` | Luno | [a17-luno-cutout-v2.png](../static/avatars/stage/a17-luno-cutout-v2.png) | [a17-luno-cutout-v2.png](../static/avatars/a17-luno-cutout-v2.png) |
| `a18` | Nimbus | [a18-nimbus-cutout-v2.png](../static/avatars/stage/a18-nimbus-cutout-v2.png) | [a18-nimbus-cutout-v2.png](../static/avatars/a18-nimbus-cutout-v2.png) |

### Pulte und Plaketten

Quelle: `PLAQUE_CATALOG` und `DEFAULT_PLAQUE` in `app.py`.
`perfect_podium_asset` ist trotz seines historischen Namens das hohe Pult im
heutigen gemeinsamen Profilfenster. `podium_asset` und `desk_asset` verweisen
je Familie auf dieselbe ältere Pultdatei; es sind keine zwei zusätzlichen Skins.
Die kleine Plakette und das hohe Pult gehören zur gleichen ausgerüsteten ID.

| ID | Familie | Hohe Profilvariante (`perfect_podium_asset`) | Ältere Pult-/Artikelvariante (`podium_asset` / `desk_asset`) | Hängeplakette (`asset`) |
|---|---|---|---|---|
| `p00` | Startpult | [p00-startpult-tall-v2.png](../static/podiums/p00-startpult-tall-v2.png) | [p00-startpult-v1.png](../static/podiums/p00-startpult-v1.png) | – |
| `p01` | Tavernenschild | [p01-tavernenschild-tall-v2.png](../static/podiums/p01-tavernenschild-tall-v2.png) | [p01-tavernenschild-v1.png](../static/podiums/p01-tavernenschild-v1.png) | [p01.webp](../static/plaques/p01.webp) |
| `p02` | Schiefer | [p02-schiefer-tall-v2.png](../static/podiums/p02-schiefer-tall-v2.png) | [p02-schiefer-v1.png](../static/podiums/p02-schiefer-v1.png) | [p02.webp](../static/plaques/p02.webp) |
| `p03` | Gebürsteter Stahl | [p03-arena-console-tall-v3.png](../static/podiums/p03-arena-console-tall-v3.png) | [p03-arena-console-v2.png](../static/podiums/p03-arena-console-v2.png) | [p03.webp](../static/plaques/p03.webp) |
| `p04` | Gefalteter Stahl | [p04-gefalteter-stahl-tall-v2.png](../static/podiums/p04-gefalteter-stahl-tall-v2.png) | [p04-gefalteter-stahl-v1.png](../static/podiums/p04-gefalteter-stahl-v1.png) | [p04.webp](../static/plaques/p04.webp) |
| `p05` | Neonglas | [p05-neonglas-tall-v2.png](../static/podiums/p05-neonglas-tall-v2.png) | [p05-neonglas-v1.png](../static/podiums/p05-neonglas-v1.png) | [p05.webp](../static/plaques/p05.webp) |
| `p06` | Theatersamt | [p06-theatersamt-tall-v2.png](../static/podiums/p06-theatersamt-tall-v2.png) | [p06-theatersamt-v1.png](../static/podiums/p06-theatersamt-v1.png) | [p06.webp](../static/plaques/p06.webp) |
| `p07` | Arcade-Acryl | [p07-arcade-acryl-tall-v2.png](../static/podiums/p07-arcade-acryl-tall-v2.png) | [p07-arcade-acryl-v1.png](../static/podiums/p07-arcade-acryl-v1.png) | [p07.webp](../static/plaques/p07.webp) |
| `p08` | Emaille-Schild | [p08-emaille-tall-v2.png](../static/podiums/p08-emaille-tall-v2.png) | [p08-emaille-v1.png](../static/podiums/p08-emaille-v1.png) | [p08.webp](../static/plaques/p08.webp) |
| `p09` | Kupferpatina | [p09-kupferpatina-tall-v2.png](../static/podiums/p09-kupferpatina-tall-v2.png) | [p09-kupferpatina-v1.png](../static/podiums/p09-kupferpatina-v1.png) | [p09.webp](../static/plaques/p09.webp) |
| `p10` | Reiseleder | [p10-reiseleder-tall-v2.png](../static/podiums/p10-reiseleder-tall-v2.png) | [p10-reiseleder-v1.png](../static/podiums/p10-reiseleder-v1.png) | [p10.webp](../static/plaques/p10.webp) |
| `p11` | Kristalleis | [p11-kristalleis-tall-v2.png](../static/podiums/p11-kristalleis-tall-v2.png) | [p11-kristalleis-v1.png](../static/podiums/p11-kristalleis-v1.png) | [p11.webp](../static/plaques/p11.webp) |
| `p12` | Wurzelholz | [p12-wurzelholz-tall-v2.png](../static/podiums/p12-wurzelholz-tall-v2.png) | [p12-wurzelholz-v1.png](../static/podiums/p12-wurzelholz-v1.png) | [p12.webp](../static/plaques/p12.webp) |
| `p13` | Spielhallen-Beton | [p13-baustellenmeister-tall-v2.png](../static/podiums/p13-baustellenmeister-tall-v2.png) | [p13-baustellenmeister-v1.png](../static/podiums/p13-baustellenmeister-v1.png) | [p13.webp](../static/plaques/p13.webp) |

Das Startpult hat keine eigene Plakettengrafik; seine Darstellung wird in der
gemeinsamen Komponente behandelt. Keine neue Plakettendatei dafür erzeugen.

### Persönliche Hintergründe

Quelle: `BACKGROUND_CATALOG` und `DEFAULT_BACKGROUND` in `app.py`.
Diese Auswahl gilt für die persönlichen Profilfenster und den dafür
vorgesehenen guesstimate-Bereich, nicht automatisch für einen Spielraum.

| ID | Name | Registrierte Datei |
|---|---|---|
| `b00` | Neon-Arena | [arena-stage-background-v1.png](../static/arena-stage-background-v1.png) |
| `b01` | Arena-Rundblick | [arena-stage-background-v2.png](../static/arena-stage-background-v2.png) |
| `b02` | Clubzimmer | [stormseeds-perfect-clubroom-v1.png](../static/stormseeds-perfect-clubroom-v1.png) |
| `b03` | Wissensatelier | [background-wissensatelier-v1.png](../static/background-wissensatelier-v1.png) |
| `b04` | Neon-Garten | [background-neon-garten-v1.png](../static/background-neon-garten-v1.png) |
| `b05` | Bergsee | [background-bergsee-v1.png](../static/background-bergsee-v1.png) |
| `b06` | Quiz-Kosmos | [background-quiz-kosmos-v1.png](../static/background-quiz-kosmos-v1.png) |
| `b07` | Gameshow-Arena | [background-gameshow-arena-v1.png](../static/background-gameshow-arena-v1.png) |
| `b08` | Mediterraner Hof | [background-mediterraner-hof-v1.png](../static/background-mediterraner-hof-v1.png) |
| `b09` | Papierlandschaft | [background-papierlandschaft-v1.png](../static/background-papierlandschaft-v1.png) |
| `b10` | Wolkenpavillon | [background-wolkenpavillon-v1.png](../static/background-wolkenpavillon-v1.png) |

### Weitere vorhandene Avatar-/Pultdateien

Die folgenden Dateien sind nicht in den oben erfassten Assetfeldern
registriert. Das belegt keine vollständige Nichtverwendung: direkte
Vorlagenverweise und frühere Entwürfe können daneben bestehen.
Sie werden weder gelöscht noch als neue Standardvariante festgelegt.

| Datei | Einordnung |
|---|---|
| [static/avatars/a01-kea.webp](../static/avatars/a01-kea.webp) | Weiterer Bestand; Verwendungsprüfung vor Ersetzung oder Übernahme |
| [static/avatars/a14-somnus-background-v1.png](../static/avatars/a14-somnus-background-v1.png) | Weiterer Bestand; Verwendungsprüfung vor Ersetzung oder Übernahme |
| [static/avatars/a14-somnus-legacy-pre-normalization-v1.png](../static/avatars/a14-somnus-legacy-pre-normalization-v1.png) | Weiterer Bestand; Verwendungsprüfung vor Ersetzung oder Übernahme |
| [static/avatars/a14-somnus.png](../static/avatars/a14-somnus.png) | Weiterer Bestand; Verwendungsprüfung vor Ersetzung oder Übernahme |
| [static/avatars/a15-ember-background-v1.png](../static/avatars/a15-ember-background-v1.png) | Weiterer Bestand; Verwendungsprüfung vor Ersetzung oder Übernahme |
| [static/avatars/a15-ember-legacy-pre-normalization-v1.png](../static/avatars/a15-ember-legacy-pre-normalization-v1.png) | Weiterer Bestand; Verwendungsprüfung vor Ersetzung oder Übernahme |
| [static/avatars/a15-ember.png](../static/avatars/a15-ember.png) | Weiterer Bestand; Verwendungsprüfung vor Ersetzung oder Übernahme |
| [static/avatars/a16-myrli-background-v1.png](../static/avatars/a16-myrli-background-v1.png) | Weiterer Bestand; Verwendungsprüfung vor Ersetzung oder Übernahme |
| [static/avatars/a16-myrli-legacy-pre-normalization-v1.png](../static/avatars/a16-myrli-legacy-pre-normalization-v1.png) | Weiterer Bestand; Verwendungsprüfung vor Ersetzung oder Übernahme |
| [static/avatars/a16-myrli.png](../static/avatars/a16-myrli.png) | Weiterer Bestand; Verwendungsprüfung vor Ersetzung oder Übernahme |
| [static/avatars/a17-luno-background-v1.png](../static/avatars/a17-luno-background-v1.png) | Weiterer Bestand; Verwendungsprüfung vor Ersetzung oder Übernahme |
| [static/avatars/a17-luno-legacy-pre-normalization-v1.png](../static/avatars/a17-luno-legacy-pre-normalization-v1.png) | Weiterer Bestand; Verwendungsprüfung vor Ersetzung oder Übernahme |
| [static/avatars/a17-luno.png](../static/avatars/a17-luno.png) | Weiterer Bestand; Verwendungsprüfung vor Ersetzung oder Übernahme |
| [static/avatars/a18-nimbus-background-v1.png](../static/avatars/a18-nimbus-background-v1.png) | Weiterer Bestand; Verwendungsprüfung vor Ersetzung oder Übernahme |
| [static/avatars/a18-nimbus-legacy-pre-normalization-v1.png](../static/avatars/a18-nimbus-legacy-pre-normalization-v1.png) | Weiterer Bestand; Verwendungsprüfung vor Ersetzung oder Übernahme |
| [static/avatars/a18-nimbus.png](../static/avatars/a18-nimbus.png) | Weiterer Bestand; Verwendungsprüfung vor Ersetzung oder Übernahme |
| [static/avatars/stage/a01-kea-pre-normalization-v1.webp](../static/avatars/stage/a01-kea-pre-normalization-v1.webp) | Weiterer Bestand; Verwendungsprüfung vor Ersetzung oder Übernahme |
| [static/avatars/stage/a02-wasserschwein-pre-normalization-v1.webp](../static/avatars/stage/a02-wasserschwein-pre-normalization-v1.webp) | Weiterer Bestand; Verwendungsprüfung vor Ersetzung oder Übernahme |
| [static/avatars/stage/a03-wanderfalke-pre-normalization-v1.webp](../static/avatars/stage/a03-wanderfalke-pre-normalization-v1.webp) | Weiterer Bestand; Verwendungsprüfung vor Ersetzung oder Übernahme |
| [static/avatars/stage/a04-faultier-pre-normalization-v1.webp](../static/avatars/stage/a04-faultier-pre-normalization-v1.webp) | Weiterer Bestand; Verwendungsprüfung vor Ersetzung oder Übernahme |
| [static/avatars/stage/a05-waschbaer-pre-normalization-v1.webp](../static/avatars/stage/a05-waschbaer-pre-normalization-v1.webp) | Weiterer Bestand; Verwendungsprüfung vor Ersetzung oder Übernahme |
| [static/avatars/stage/a06-oktopus-pre-normalization-v1.webp](../static/avatars/stage/a06-oktopus-pre-normalization-v1.webp) | Weiterer Bestand; Verwendungsprüfung vor Ersetzung oder Übernahme |
| [static/avatars/stage/a07-ziege-pre-normalization-v1.webp](../static/avatars/stage/a07-ziege-pre-normalization-v1.webp) | Weiterer Bestand; Verwendungsprüfung vor Ersetzung oder Übernahme |
| [static/avatars/stage/a08-kraehe-pre-normalization-v1.webp](../static/avatars/stage/a08-kraehe-pre-normalization-v1.webp) | Weiterer Bestand; Verwendungsprüfung vor Ersetzung oder Übernahme |
| [static/avatars/stage/a09-fennek-pre-normalization-v1.webp](../static/avatars/stage/a09-fennek-pre-normalization-v1.webp) | Weiterer Bestand; Verwendungsprüfung vor Ersetzung oder Übernahme |
| [static/avatars/stage/a10-wombat-pre-normalization-v1.webp](../static/avatars/stage/a10-wombat-pre-normalization-v1.webp) | Weiterer Bestand; Verwendungsprüfung vor Ersetzung oder Übernahme |
| [static/avatars/stage/a11-gans-pre-normalization-v1.webp](../static/avatars/stage/a11-gans-pre-normalization-v1.webp) | Weiterer Bestand; Verwendungsprüfung vor Ersetzung oder Übernahme |
| [static/avatars/stage/a12-fangschreckenkrebs-pre-normalization-v1.webp](../static/avatars/stage/a12-fangschreckenkrebs-pre-normalization-v1.webp) | Weiterer Bestand; Verwendungsprüfung vor Ersetzung oder Übernahme |
| [static/avatars/stage/a13-axolotl-pre-normalization-v1.webp](../static/avatars/stage/a13-axolotl-pre-normalization-v1.webp) | Weiterer Bestand; Verwendungsprüfung vor Ersetzung oder Übernahme |
| [static/avatars/stage/a14-somnus-background-v1.png](../static/avatars/stage/a14-somnus-background-v1.png) | Weiterer Bestand; Verwendungsprüfung vor Ersetzung oder Übernahme |
| [static/avatars/stage/a14-somnus-cutout-v2-pre-normalization-v1.png](../static/avatars/stage/a14-somnus-cutout-v2-pre-normalization-v1.png) | Weiterer Bestand; Verwendungsprüfung vor Ersetzung oder Übernahme |
| [static/avatars/stage/a14-somnus-legacy-pre-normalization-v1.png](../static/avatars/stage/a14-somnus-legacy-pre-normalization-v1.png) | Weiterer Bestand; Verwendungsprüfung vor Ersetzung oder Übernahme |
| [static/avatars/stage/a14-somnus.png](../static/avatars/stage/a14-somnus.png) | Weiterer Bestand; Verwendungsprüfung vor Ersetzung oder Übernahme |
| [static/avatars/stage/a15-ember-background-v1.png](../static/avatars/stage/a15-ember-background-v1.png) | Weiterer Bestand; Verwendungsprüfung vor Ersetzung oder Übernahme |
| [static/avatars/stage/a15-ember-cutout-v2-pre-normalization-v1.png](../static/avatars/stage/a15-ember-cutout-v2-pre-normalization-v1.png) | Weiterer Bestand; Verwendungsprüfung vor Ersetzung oder Übernahme |
| [static/avatars/stage/a15-ember-legacy-pre-normalization-v1.png](../static/avatars/stage/a15-ember-legacy-pre-normalization-v1.png) | Weiterer Bestand; Verwendungsprüfung vor Ersetzung oder Übernahme |
| [static/avatars/stage/a15-ember.png](../static/avatars/stage/a15-ember.png) | Weiterer Bestand; Verwendungsprüfung vor Ersetzung oder Übernahme |
| [static/avatars/stage/a16-myrli-background-v1.png](../static/avatars/stage/a16-myrli-background-v1.png) | Weiterer Bestand; Verwendungsprüfung vor Ersetzung oder Übernahme |
| [static/avatars/stage/a16-myrli-cutout-v2-pre-normalization-v1.png](../static/avatars/stage/a16-myrli-cutout-v2-pre-normalization-v1.png) | Weiterer Bestand; Verwendungsprüfung vor Ersetzung oder Übernahme |
| [static/avatars/stage/a16-myrli-legacy-pre-normalization-v1.png](../static/avatars/stage/a16-myrli-legacy-pre-normalization-v1.png) | Weiterer Bestand; Verwendungsprüfung vor Ersetzung oder Übernahme |
| [static/avatars/stage/a16-myrli.png](../static/avatars/stage/a16-myrli.png) | Weiterer Bestand; Verwendungsprüfung vor Ersetzung oder Übernahme |
| [static/avatars/stage/a17-luno-background-v1.png](../static/avatars/stage/a17-luno-background-v1.png) | Weiterer Bestand; Verwendungsprüfung vor Ersetzung oder Übernahme |
| [static/avatars/stage/a17-luno-cutout-v2-pre-normalization-v1.png](../static/avatars/stage/a17-luno-cutout-v2-pre-normalization-v1.png) | Weiterer Bestand; Verwendungsprüfung vor Ersetzung oder Übernahme |
| [static/avatars/stage/a17-luno-legacy-pre-normalization-v1.png](../static/avatars/stage/a17-luno-legacy-pre-normalization-v1.png) | Weiterer Bestand; Verwendungsprüfung vor Ersetzung oder Übernahme |
| [static/avatars/stage/a17-luno.png](../static/avatars/stage/a17-luno.png) | Weiterer Bestand; Verwendungsprüfung vor Ersetzung oder Übernahme |
| [static/avatars/stage/a18-nimbus-background-v1.png](../static/avatars/stage/a18-nimbus-background-v1.png) | Weiterer Bestand; Verwendungsprüfung vor Ersetzung oder Übernahme |
| [static/avatars/stage/a18-nimbus-cutout-v2-pre-normalization-v1.png](../static/avatars/stage/a18-nimbus-cutout-v2-pre-normalization-v1.png) | Weiterer Bestand; Verwendungsprüfung vor Ersetzung oder Übernahme |
| [static/avatars/stage/a18-nimbus-legacy-pre-normalization-v1.png](../static/avatars/stage/a18-nimbus-legacy-pre-normalization-v1.png) | Weiterer Bestand; Verwendungsprüfung vor Ersetzung oder Übernahme |
| [static/avatars/stage/a18-nimbus.png](../static/avatars/stage/a18-nimbus.png) | Weiterer Bestand; Verwendungsprüfung vor Ersetzung oder Übernahme |
| [static/podiums/arena-side-desk-blue-v1.png](../static/podiums/arena-side-desk-blue-v1.png) | Weiterer Bestand; Verwendungsprüfung vor Ersetzung oder Übernahme |
| [static/podiums/arena-side-desk-red-v1.png](../static/podiums/arena-side-desk-red-v1.png) | Weiterer Bestand; Verwendungsprüfung vor Ersetzung oder Übernahme |
| [static/podiums/p00-startpult-tall-v2-pre-normalization-v1.png](../static/podiums/p00-startpult-tall-v2-pre-normalization-v1.png) | Weiterer Bestand; Verwendungsprüfung vor Ersetzung oder Übernahme |
| [static/podiums/p01-tavernenschild-tall-v2-pre-normalization-v1.png](../static/podiums/p01-tavernenschild-tall-v2-pre-normalization-v1.png) | Weiterer Bestand; Verwendungsprüfung vor Ersetzung oder Übernahme |
| [static/podiums/p02-schiefer-tall-v2-pre-normalization-v1.png](../static/podiums/p02-schiefer-tall-v2-pre-normalization-v1.png) | Weiterer Bestand; Verwendungsprüfung vor Ersetzung oder Übernahme |
| [static/podiums/p03-arena-console-tall-v3-pre-normalization-v1.png](../static/podiums/p03-arena-console-tall-v3-pre-normalization-v1.png) | Weiterer Bestand; Verwendungsprüfung vor Ersetzung oder Übernahme |
| [static/podiums/p03-brushed-steel.png](../static/podiums/p03-brushed-steel.png) | Weiterer Bestand; Verwendungsprüfung vor Ersetzung oder Übernahme |
| [static/podiums/p04-gefalteter-stahl-tall-v2-pre-normalization-v1.png](../static/podiums/p04-gefalteter-stahl-tall-v2-pre-normalization-v1.png) | Weiterer Bestand; Verwendungsprüfung vor Ersetzung oder Übernahme |
| [static/podiums/p05-neonglas-tall-v2-pre-normalization-v1.png](../static/podiums/p05-neonglas-tall-v2-pre-normalization-v1.png) | Weiterer Bestand; Verwendungsprüfung vor Ersetzung oder Übernahme |
| [static/podiums/p06-theatersamt-tall-v2-pre-normalization-v1.png](../static/podiums/p06-theatersamt-tall-v2-pre-normalization-v1.png) | Weiterer Bestand; Verwendungsprüfung vor Ersetzung oder Übernahme |
| [static/podiums/p07-arcade-acryl-tall-v2-pre-normalization-v1.png](../static/podiums/p07-arcade-acryl-tall-v2-pre-normalization-v1.png) | Weiterer Bestand; Verwendungsprüfung vor Ersetzung oder Übernahme |
| [static/podiums/p08-emaille-tall-v2-pre-normalization-v1.png](../static/podiums/p08-emaille-tall-v2-pre-normalization-v1.png) | Weiterer Bestand; Verwendungsprüfung vor Ersetzung oder Übernahme |
| [static/podiums/p09-kupferpatina-tall-v2-pre-normalization-v1.png](../static/podiums/p09-kupferpatina-tall-v2-pre-normalization-v1.png) | Weiterer Bestand; Verwendungsprüfung vor Ersetzung oder Übernahme |
| [static/podiums/p10-reiseleder-tall-v2-pre-normalization-v1.png](../static/podiums/p10-reiseleder-tall-v2-pre-normalization-v1.png) | Weiterer Bestand; Verwendungsprüfung vor Ersetzung oder Übernahme |
| [static/podiums/p11-kristalleis-tall-v2-pre-normalization-v1.png](../static/podiums/p11-kristalleis-tall-v2-pre-normalization-v1.png) | Weiterer Bestand; Verwendungsprüfung vor Ersetzung oder Übernahme |
| [static/podiums/p12-wurzelholz-tall-v2-pre-normalization-v1.png](../static/podiums/p12-wurzelholz-tall-v2-pre-normalization-v1.png) | Weiterer Bestand; Verwendungsprüfung vor Ersetzung oder Übernahme |
| [static/podiums/p13-baustellenmeister-tall-v2-pre-normalization-v1.png](../static/podiums/p13-baustellenmeister-tall-v2-pre-normalization-v1.png) | Weiterer Bestand; Verwendungsprüfung vor Ersetzung oder Übernahme |

## 2. Spielmotive, Räume und Bedienelemente

Die Rollen beschreiben die aktuellen Vorlagen und Styles. Diese Tabelle
führt keine neue Grafik ein und erklärt keine unreferenzierte Datei für
aktuell sichtbar.

| Datei | Rolle | Einsatz im Bestand |
|---|---|---|
| [carousel-daily-quiz-v1.png](../static/carousel-daily-quiz-v1.png) | guesstimate-Motiv | Startseiten-Präsentation |
| [carousel-party-classic-v1.png](../static/carousel-party-classic-v1.png) | guesstimate party-Motiv | Startseiten-Präsentation |
| [carousel-stormseeds-perfect-v1.png](../static/carousel-stormseeds-perfect-v1.png) | perfect-Motiv | Startseite und Brettspiel-Kachel |
| [carousel-playtable-v1.png](../static/carousel-playtable-v1.png) | Sammlungsraum | games collection, brettspiele und Sammlungspräsentation |
| [tabletop-card-table-tile-v1.png](../static/tabletop-card-table-tile-v1.png) | Karten-Kachel | Sammlung und Kartengruppe |
| [tabletop-dice-table-tile-v1.png](../static/tabletop-dice-table-tile-v1.png) | Würfel-Kachel | Sammlung; wiederverwendet bei Würfelspielen |
| [tabletop-kniffel-tile-v1.png](../static/tabletop-kniffel-tile-v1.png) | kniffel-Kachel | Würfelgruppe |
| [tabletop-risk-tile-v1.png](../static/tabletop-risk-tile-v1.png) | conquest-Kachel | Brettspielgruppe |
| [card-tables-background-v1.png](../static/card-tables-background-v1.png) | Kartenraum | Kartenübersicht und Standard-Kartenlobby |
| [card-table-felt-v1.png](../static/card-table-felt-v1.png) | Kartenfilz | Laufender Kartentisch |
| [card-player-board-poker-v2.png](../static/card-player-board-poker-v2.png) | Kartenablage / Spielerkonsole | Laufender Kartentisch; kein persönliches Profilpult |
| [guesstimate-card-back-v1.png](../static/guesstimate-card-back-v1.png) | Kartenrücken | Freie Standardkarten |
| [dice-table-background-v2.png](../static/dice-table-background-v2.png) | Würfelraum | Würfelübersichten, -lobbys und laufende Würfelspiele |
| [maexchen-logo-v1.svg](../static/maexchen-logo-v1.svg) | mäxchen-Logo | Würfelkonsole |
| [stormseeds-perfect-clubroom-table-v2.png](../static/stormseeds-perfect-clubroom-table-v2.png) | perfect-Raum mit Tisch | Laufender perfect-Raum und dessen Lobby |
| [stormseeds-perfect-settings-paper-v2.png](../static/stormseeds-perfect-settings-paper-v2.png) | Einstellungszettel | perfect; unveränderte Position beibehalten |
| [stormseeds-perfect-start-buzzer-v2.png](../static/stormseeds-perfect-start-buzzer-v2.png) | Start-/Bereit-Buzzer | perfect; unveränderte Position beibehalten |
| [conquest-lobby-background-v1.png](../static/conquest-lobby-background-v1.png) | conquest-Raum | conquest-Übersicht und Lobby |
| [welt-conquest-farbkarte-v2.png](../static/conquest/boards/welt-conquest-farbkarte-v2.png) | Aktuelles conquest-Kartenmotiv | Statische Kopie des aktiven Tischmotivs karte.png; kein zusätzlicher Vorschau-Block mehr in der Übersicht |
| [favicon.svg](../static/favicon.svg) | Projektzeichen | Browserkennzeichnung |

## 3. Komponenten und Werkzeuge

| Quelle | Aufgabe | Status |
|---|---|---|
| [player_portrait.py](../player_portrait.py), [static/player-portrait.js](../static/player-portrait.js), [static/player-portrait.css](../static/player-portrait.css) | Gemeinsame kompakte Anzeige aus aktueller Profilausrüstung | Lokal bei Conquest angeschlossen; weitere Einsatzorte offen |
| [templates/_lobby_overview.html](../templates/_lobby_overview.html) | Gemeinsame Übersicht mit Kopf, Zeilen und Aktionen | Gemeinsamer Baustein |
| [static/lobby-overview.css](../static/lobby-overview.css) | Eine gemeinsame Gestaltung der Übersichten | Gemeinsamer Baustein |
| [static/lobby-overview.js](../static/lobby-overview.js) | Gemeinsame Aktualisierung und Wiederholung nach Fehlern | Gemeinsamer Baustein |
| [lobby_overview.py](../lobby_overview.py) | Lesender Anzeigeadapter und Signatur der sichtbaren Angaben | Gemeinsamer Baustein |
| [templates/_profile_window.html](../templates/_profile_window.html) | Vollständiges Profilfenster und Inhaltsparameter | Gemeinsamer Baustein |
| [static/profile-window.css](../static/profile-window.css) | Eine Szenenkomposition und Feldkoordinaten aller 14 Pulte | Gemeinsamer Baustein |
| [static/profile-stage-v1.js](../static/profile-stage-v1.js) | Automatische Pultbeschriftung und Aktualisierung | Gemeinsamer Baustein |
| [templates/_player_identity.html](../templates/_player_identity.html) | Ranking, ältere Ergebnis-/Pultdarstellungen und Artikelvorschau | Ältere Darstellungen; nicht pauschal unbenutzt |
| [templates/_lobby_room.html](../templates/_lobby_room.html) | Standardlobby, Zusammenfassung und Startknopf | Gemeinsamer Baustein |
| [static/lobby.css](../static/lobby.css) | Standard-Lobbygestaltung | Gemeinsamer Baustein |
| [static/lobby.js](../static/lobby.js) | Statusaktualisierung, Speichern und Startkoordination | Gemeinsamer Baustein |
| [lobby_view.py](../lobby_view.py) | Aktuelle Profilausrüstung für Lobbyanzeigen lesen | Gemeinsamer Baustein |
| [templates/_game_flyers.html](../templates/_game_flyers.html) | perfect- und conquest-Präsentation | Vorhandene Kachelfamilie |
| [templates/tabletop_family.html](../templates/tabletop_family.html) | Karten-, Würfel- und Brettspielgruppen | Gemeinsame Gruppenvorlage |
| [templates/tabletop_connection.html](../templates/tabletop_connection.html) | games collection | Sammlungsansicht |
| [templates/_leaderboard.html](../templates/_leaderboard.html) | Ranglisten und Ranking-Identitäten | Gemeinsamer Baustein mit älterer Identitätsvariante |
| [templates/_icons.html](../templates/_icons.html) | Fragearten-Symbole als gemeinsame SVG-Makros | Gemeinsamer Baustein |
| [static/ui-conventions.css](../static/ui-conventions.css) | Aktionsgrün und Kleinschreibung | Gemeinsame Grundlage |
| [static/typography-v1.css](../static/typography-v1.css) | Lokale Schriftfamilien und gemeinsame Typografie | Gemeinsame Grundlage |
| [static/rules.js](../static/rules.js) | Regeldialog über vorhandene Auslöser bedienen | Gemeinsamer Baustein |
| [static/card-table.js](../static/card-table.js) | Kartenbedienung, Austeilen, Stapel, Gebote und Notizen | Im Kartenspiel gebunden |
| [static/dice-table.js](../static/dice-table.js) | Würfeltechnik, Kniffelblock, mäxchen-Anzeigen | Im Würfelspiel gebunden |
| [offline-preview/conquest-2-5d-v1/table-surface.js](../offline-preview/conquest-2-5d-v1/table-surface.js) | Gemeinsame tatsächliche conquest-Tischoberfläche | Im Spiel und dessen isolierter Vorschau gemeinsam benutzt |
| [offline-preview/conquest-2-5d-v1/scene.js](../offline-preview/conquest-2-5d-v1/scene.js) | Räumlicher Holztisch, Materialien und Raum | Im conquest-Spiel gebunden |
| [offline-preview/conquest-2-5d-v1/camera.js](../offline-preview/conquest-2-5d-v1/camera.js) | Blickwinkel und Einpassen des Bretts | Im conquest-Spiel gebunden |
| [offline-preview/conquest-2-5d-v1/territories.js](../offline-preview/conquest-2-5d-v1/territories.js) | Länder- und Truppenmarken, Auswahl und Nachbarschaft | Im conquest-Spiel gebunden |
| [offline-preview/conquest-2-5d-v1/cards.js](../offline-preview/conquest-2-5d-v1/cards.js) | Gemeinsame Länderkarten, Gewinnkarte und Inventar mit Vektorsymbolen | Im conquest-Spiel gebunden |
| [offline-preview/conquest-2-5d-v1/remote-turn.js](../offline-preview/conquest-2-5d-v1/remote-turn.js) | Anbindung des Tischs an gespeicherten Spielzustand | Spieladapter; keine allgemeine Komponentenlogik |
| [conquest_cards.py](../conquest_cards.py) | Kartensatz und serverseitiger Tausch | Spielregelmodul; keine Grafikbibliothek |

`spieler.portraet` und `zugang.liste` aus [BAUKASTEN.md](BAUKASTEN.md) sind oben
als gemeinsame lokale Implementierungen erfasst. Die bisherigen allgemeinen
Buttons und Spielanzeigen bleiben gestalterisch offen. Die ältere Party-
Ergebnisdarstellung wird vor einer Weiterverwendung eigenständig neu entworfen;
siehe [GESTALTUNGSPLAN.md](GESTALTUNGSPLAN.md).

## 4. Modelle, Bibliotheken, Schriften und Klänge

| Bestand | Vorhandene Quelle | Wiederverwendung / Nachweis |
|---|---|---|
| dddice 0.21.8 | [dddice-0.21.8.js](../static/vendor/dddice-0.21.8.js) | Lokal eingebundene Würfelbibliothek; [dddice-0.21.8.LICENSE.txt](../static/vendor/dddice-0.21.8.LICENSE.txt) und [dddice-0.21.8.THIRD-PARTY-NOTICES.txt](../static/vendor/dddice-0.21.8.THIRD-PARTY-NOTICES.txt) vorhanden |
| Würfel-Theme Outgunned Reimagined 1.0.6 | [theme.json](../static/vendor/dddice-outgunned/theme.json) | 24 lokale Dateien: 2 FBX-Modelle, 3 PNG, 13 WebP, 5 MP3 und die JSON-Datei. Ein gesonderter lokaler Lizenztext für alle Theme-Dateien wurde in diesem Ordner nicht gefunden. |
| W6-Modell | [d6.fbx](../static/vendor/dddice-outgunned/d6.fbx) | Modell des vorhandenen Theme-Pakets; im Würfelspiel verwendet |
| W2-/Münzmodell | [d2.fbx](../static/vendor/dddice-outgunned/d2.fbx) | Im Paket vorhanden; keine damit neu eingeführte Spielart |
| Three.js | [three.module.js](../offline-preview/conquest-2-5d-v1/vendor/three/three.module.js) und [three.core.js](../offline-preview/conquest-2-5d-v1/vendor/three/three.core.js) | Lokaler Bestand der conquest-Tischszene; [LICENSE](../offline-preview/conquest-2-5d-v1/vendor/three/LICENSE) vorhanden |
| Räumlicher Spieltisch | [scene.js](../offline-preview/conquest-2-5d-v1/scene.js) | Tischkörper, Holztextur, Tischbeine und Ausstattung entstehen im Code; kein separat registriertes universelles GLB-/OBJ-Tischmodell |
| Inter | [Inter-Variable.ttf](../static/fonts/Inter-Variable.ttf) | Gemeinsame Bedien- und Leseschrift. [OFL.txt](../static/fonts/OFL.txt) nennt Inter. |
| Fredoka | [Fredoka-Variable.ttf](../static/fonts/Fredoka-Variable.ttf) | Gemeinsame markante Überschriftenschrift. Ein gesonderter Fredoka-Nachweis ist in diesem Schriftordner nicht vorhanden. |

### Dateien des vorhandenen Würfel-Themes

Die Klänge sind Teil des importierten Würfelpakets. Daraus folgt keine
neue globale Klanggestaltung und keine Pflicht, Ton einzuschalten.

| Datei | Typ |
|---|---|
| [09b5fe57f2a989d030759d608b061f44.webp](../static/vendor/dddice-outgunned/09b5fe57f2a989d030759d608b061f44.webp) | `.webp` |
| [4c57e71c50b60ffbce06cc7ff9e14862.webp](../static/vendor/dddice-outgunned/4c57e71c50b60ffbce06cc7ff9e14862.webp) | `.webp` |
| [60a8a1829998de57a04b75c4613d9ce5.webp](../static/vendor/dddice-outgunned/60a8a1829998de57a04b75c4613d9ce5.webp) | `.webp` |
| [65d8ad5d-ed69-4c48-8ac6-8ff0a1636979-027e092a764b0ecf1522cd5cdb27aa2e.png](../static/vendor/dddice-outgunned/65d8ad5d-ed69-4c48-8ac6-8ff0a1636979-027e092a764b0ecf1522cd5cdb27aa2e.png) | `.png` |
| [6c01e8b8239b9c2c2213eab9dcd688e0.webp](../static/vendor/dddice-outgunned/6c01e8b8239b9c2c2213eab9dcd688e0.webp) | `.webp` |
| [7a4b2ee2c8f3f1256fb7f1c19981394e.mp3](../static/vendor/dddice-outgunned/7a4b2ee2c8f3f1256fb7f1c19981394e.mp3) | `.mp3` |
| [7b184bd9eb022a0a0a34654b183db07e.mp3](../static/vendor/dddice-outgunned/7b184bd9eb022a0a0a34654b183db07e.mp3) | `.mp3` |
| [843db96bf74689740254d9f8e0a2c8e2.webp](../static/vendor/dddice-outgunned/843db96bf74689740254d9f8e0a2c8e2.webp) | `.webp` |
| [9a663b8b6b9d5d0ff3041a0e2fa6f724.mp3](../static/vendor/dddice-outgunned/9a663b8b6b9d5d0ff3041a0e2fa6f724.mp3) | `.mp3` |
| [9a92e2cf59d1d2c176855d18035128ab.webp](../static/vendor/dddice-outgunned/9a92e2cf59d1d2c176855d18035128ab.webp) | `.webp` |
| [a1629110aea24f26cb32f8c240f83e6a.mp3](../static/vendor/dddice-outgunned/a1629110aea24f26cb32f8c240f83e6a.mp3) | `.mp3` |
| [aae4286a8398066c891459aa818dc8ca.webp](../static/vendor/dddice-outgunned/aae4286a8398066c891459aa818dc8ca.webp) | `.webp` |
| [ac9670cb951371b5a8bf06f9aacaeb36.webp](../static/vendor/dddice-outgunned/ac9670cb951371b5a8bf06f9aacaeb36.webp) | `.webp` |
| [be8fe5f417e657ec8000d69fe3781bcd.mp3](../static/vendor/dddice-outgunned/be8fe5f417e657ec8000d69fe3781bcd.mp3) | `.mp3` |
| [d2.fbx](../static/vendor/dddice-outgunned/d2.fbx) | `.fbx` |
| [d3f0b12f-ad5e-47e1-959f-43441319d82c-a60d582756ddb9944a9d48c7ba44e178.png](../static/vendor/dddice-outgunned/d3f0b12f-ad5e-47e1-959f-43441319d82c-a60d582756ddb9944a9d48c7ba44e178.png) | `.png` |
| [d6-881c5673416865ff9078932c445ea29b.png](../static/vendor/dddice-outgunned/d6-881c5673416865ff9078932c445ea29b.png) | `.png` |
| [d6.fbx](../static/vendor/dddice-outgunned/d6.fbx) | `.fbx` |
| [d740ee48960cf2701b8874b6f9ccd0b2.webp](../static/vendor/dddice-outgunned/d740ee48960cf2701b8874b6f9ccd0b2.webp) | `.webp` |
| [dc5b3c007962582688ee63058fb1c81e.webp](../static/vendor/dddice-outgunned/dc5b3c007962582688ee63058fb1c81e.webp) | `.webp` |
| [f02eaab726e83f6361ef9344d0b80188.webp](../static/vendor/dddice-outgunned/f02eaab726e83f6361ef9344d0b80188.webp) | `.webp` |
| [ffbfe7bdfdc9eaa66d1e475b072e59dd.webp](../static/vendor/dddice-outgunned/ffbfe7bdfdc9eaa66d1e475b072e59dd.webp) | `.webp` |
| [preview-18a5f27c0452565fdca077d4ec5e715b.webp](../static/vendor/dddice-outgunned/preview-18a5f27c0452565fdca077d4ec5e715b.webp) | `.webp` |
| [theme.json](../static/vendor/dddice-outgunned/theme.json) | `.json` |

## 5. conquest-Brett- und Kartenbestand

Die normale Anwendung lädt den aktuellen räumlichen Tisch über
`templates/conquest_table.html` und den Dateibestand unter
`offline-preview/conquest-2-5d-v1/`. Der Ordnername bedeutet hier nicht,
dass die Dateien ausschließlich unverbundene Entwürfe wären.

Die aktive Karte und die weiteren Raumdateien sind in
[manifest.json](../offline-preview/conquest-2-5d-v1/assets/manifest.json) verzeichnet.
Die `active`-Angabe unten wird daraus übernommen; sie ist keine neue
Browserprüfung. Die Manifest-Datei deckt nur diesen Tischbestand ab.

| Datei | `active` laut Manifest |
|---|---|
| [karte.png](../offline-preview/conquest-2-5d-v1/assets/karte.png) | True |
| [raum-ohne-tisch.png](../offline-preview/conquest-2-5d-v1/assets/raum-ohne-tisch.png) | False |
| [teppich.png](../offline-preview/conquest-2-5d-v1/assets/teppich.png) | True |
| [raum-wand-v2.png](../offline-preview/conquest-2-5d-v1/assets/raum-wand-v2.png) | True |
| [moebel-v2.png](../offline-preview/conquest-2-5d-v1/assets/moebel-v2.png) | True |

Die beiden oben genannten Dateien des aktuellen Kartenmotivs sind bei dieser
Erfassung per SHA-256 identisch. Es wird hier keine davon ersetzt.

### Weitere vorhandene Bretter und Deckbögen

Die drei früheren Stile klassisch/taktisch/farbenfroh und die zusätzlichen
Brettentwürfe bleiben erfasst. Ihre Existenz ist kein Beleg, dass der
aktuelle räumliche Spieltisch alle Stile umschaltet. Die tatsächlichen
Länderkarten im aktuellen Inventar werden von der gemeinsamen
`cards.js`-Komponente mit eigenen Vektorsymbolen aufgebaut.

| Datei | Einordnung |
|---|---|
| [static/conquest/boards/welt-conquest-farbkarte-v2.png](../static/conquest/boards/welt-conquest-farbkarte-v2.png) | Aktuelles Kartenmotiv / siehe oben |
| [static/conquest/boards/welt-conquest-skizze-v1.png](../static/conquest/boards/welt-conquest-skizze-v1.png) | Weiterer Brett-/Deckbestand; kein automatischer neuer Standard |
| [static/conquest/boards/welt-conquest-v1.png](../static/conquest/boards/welt-conquest-v1.png) | Weiterer Brett-/Deckbestand; kein automatischer neuer Standard |
| [static/conquest/boards/welt-conquest-v2.png](../static/conquest/boards/welt-conquest-v2.png) | Weiterer Brett-/Deckbestand; kein automatischer neuer Standard |
| [static/conquest/boards/welt-conquest-v3.png](../static/conquest/boards/welt-conquest-v3.png) | Weiterer Brett-/Deckbestand; kein automatischer neuer Standard |
| [static/conquest/boards/welt-conquest-v4.png](../static/conquest/boards/welt-conquest-v4.png) | Weiterer Brett-/Deckbestand; kein automatischer neuer Standard |
| [static/conquest/boards/welt-farbenfroh.webp](../static/conquest/boards/welt-farbenfroh.webp) | Weiterer Brett-/Deckbestand; kein automatischer neuer Standard |
| [static/conquest/boards/welt-klassisch.webp](../static/conquest/boards/welt-klassisch.webp) | Weiterer Brett-/Deckbestand; kein automatischer neuer Standard |
| [static/conquest/boards/welt-konturen-original-v1.png](../static/conquest/boards/welt-konturen-original-v1.png) | Weiterer Brett-/Deckbestand; kein automatischer neuer Standard |
| [static/conquest/boards/welt-taktisch.webp](../static/conquest/boards/welt-taktisch.webp) | Weiterer Brett-/Deckbestand; kein automatischer neuer Standard |
| [static/conquest/decks/laender-farbenfroh/back.webp](../static/conquest/decks/laender-farbenfroh/back.webp) | Weiterer Brett-/Deckbestand; kein automatischer neuer Standard |
| [static/conquest/decks/laender-farbenfroh/sheet-1.webp](../static/conquest/decks/laender-farbenfroh/sheet-1.webp) | Weiterer Brett-/Deckbestand; kein automatischer neuer Standard |
| [static/conquest/decks/laender-klassisch/back.webp](../static/conquest/decks/laender-klassisch/back.webp) | Weiterer Brett-/Deckbestand; kein automatischer neuer Standard |
| [static/conquest/decks/laender-klassisch/sheet-1.webp](../static/conquest/decks/laender-klassisch/sheet-1.webp) | Weiterer Brett-/Deckbestand; kein automatischer neuer Standard |
| [static/conquest/decks/laender-taktisch/back.webp](../static/conquest/decks/laender-taktisch/back.webp) | Weiterer Brett-/Deckbestand; kein automatischer neuer Standard |
| [static/conquest/decks/laender-taktisch/sheet-1.webp](../static/conquest/decks/laender-taktisch/sheet-1.webp) | Weiterer Brett-/Deckbestand; kein automatischer neuer Standard |
| [static/conquest/decks/missionen-farbenfroh/back.webp](../static/conquest/decks/missionen-farbenfroh/back.webp) | Weiterer Brett-/Deckbestand; kein automatischer neuer Standard |
| [static/conquest/decks/missionen-farbenfroh/sheet-1.webp](../static/conquest/decks/missionen-farbenfroh/sheet-1.webp) | Weiterer Brett-/Deckbestand; kein automatischer neuer Standard |
| [static/conquest/decks/missionen-klassisch/back.webp](../static/conquest/decks/missionen-klassisch/back.webp) | Weiterer Brett-/Deckbestand; kein automatischer neuer Standard |
| [static/conquest/decks/missionen-klassisch/sheet-1.webp](../static/conquest/decks/missionen-klassisch/sheet-1.webp) | Weiterer Brett-/Deckbestand; kein automatischer neuer Standard |
| [static/conquest/decks/missionen-taktisch/back.webp](../static/conquest/decks/missionen-taktisch/back.webp) | Weiterer Brett-/Deckbestand; kein automatischer neuer Standard |
| [static/conquest/decks/missionen-taktisch/sheet-1.webp](../static/conquest/decks/missionen-taktisch/sheet-1.webp) | Weiterer Brett-/Deckbestand; kein automatischer neuer Standard |

Das aktuelle Weltmodell liegt in [world.json](../static/conquest/world.json).
Die Spielregeln bleiben in [CONQUEST_RULESET.md](../CONQUEST_RULESET.md) beschrieben und
werden durch diese Bestandserfassung nicht verändert.

## 6. Quellen, Gültigkeit und weitere Pflege

- Maßgeblich für die Profilauswahl sind die aktuellen Katalogeinträge in
  [app.py](../app.py); für die Darstellung die tatsächlich verwendeten Komponenten.
- Ältere `static/conquest-table.js`-/CSS-Bestände und historische Renderings
  sind nicht allein wegen ihres Namens die Quelle der aktuellen Tischansicht.
- Für Projektgrafiken liefert das Projektlog Entstehungskontext. Eine
  vollständige Quellen-/Lizenzakte je Einzelbild ist damit nicht belegt.
  Der Katalog erfindet keine Freigaben für ungeklärte Dateien.
- `pets_runs/`, Laufzeitsicherungen, Testdaten und verworfene Renderordner
  sind keine automatisch freigegebenen Avatar-/Modellpakete für neue Spiele.
- Es wurden keine neuen Assets recherchiert, heruntergeladen, erzeugt,
  umbenannt oder in einen anderen Ordner kopiert. Vorhandene Lizenzen bleiben
  bei ihren Dateien. Eine spätere Paketbildung ist ein eigener Arbeitsschritt.
- Bei einer neuen Registrierung diese Tabellen und die Einsatzmatrix in
  `BAUKASTEN.md` gemeinsam nachführen. Die Zuordnung in dieser Dokumentation
  ist nicht als zweite vom Spiel gelesene Ausrüstungsliste zu verwenden.

## 7. Werkstatt und tatsächlicher Spielebestand vom 26.10.2026

Die aktuelle Quellaufnahme umfasst Daily Quiz, Party, Perfect, Playtable,
Würfeltisch, Kniffel, Mäxchen und Conquest sowie Startseite, Profil und Sammlung.
[WERKSTATT_BESTAND.json](WERKSTATT_BESTAND.json) enthält 19 Elementfamilien mit
konkreten Quellbelegen, Zeilennummern und Prüfsummen sowie die gefundenen
Bedienelemente und Stildefinitionen. Der Bericht lässt sich mit
`python deploy/inventory_workshop_elements.py` aus dem aktuellen lokalen
Dateibestand erneuern; Anwendung und Datenbanken werden dabei nicht geöffnet.

Quellvorkommen zählen keine tatsächlichen Bildschirmexemplare: Schleifen,
Spielzustände und ältere Einbindungen beeinflussen, was zu sehen ist. Die
Kaskade von CSS-Regeln ist erst am jeweiligen Einsatzort sichtbar zu prüfen.
Der Bericht erzeugt keine persönlichen Entwürfe und erklärt vorhandenen Code
nicht automatisch zum gemeinsamen Standard.

| Familie | Aktueller Befund | Nächster Zusammenhang mit der Werkstatt |
|---|---|---|
| Buttons | 144 Quellverwendungen als 85 Modelle aufgenommen; alle registrierten Buttons im gemeinsamen Kontureditor öffnbar. | Gemeinsame Prüfung und Anpassung sinnvoller Editoroptionen für später vorgemerkt. Zunächst die übrigen Elemente aufnehmen und anpassen; Beschriftung, Aktion und Zustände erhalten. |
| Fenster | 84 konkrete Verwendungen in 30 Modellen aufgenommen: Regeldialoge, Entscheidungen, Inventare und Aktionsflächen aller Spiele sowie Profil und Shop. | In der Bibliothek filtern, Varianten ansehen und genau zu Projekten zuordnen. Quellen und Gruppierung in [FENSTER_BESTAND.md](FENSTER_BESTAND.md). Fenstereditor und gemeinsame Optionsprüfung bleiben offen. |
| Eingaben | 58 Einsatzvarianten in 27 Modellen; alle 45 nativen bzw. rollenbasierten Quellkontrollen zugeordnet. Text/Zahlen, Auswahl, Schalter, Regler sowie Zuordnen und Sortieren vorhanden. | In Bibliothek → Eingaben ansehen, nach Spiel/Eingabeart filtern und konkrete Varianten Projekten zuordnen. Quellen in [EINGABEN_BESTAND.md](EINGABEN_BESTAND.md). Eingabeeditor und Optionsprüfung bleiben offen. |
| Anzeigen | 210 Einsatzvarianten in 63 Modellen: Punkte, Zeitwerte, Fortschritt, Status, Zähler und Ergebnisse aller acht Spiele sowie Profil/Shop. | In Bibliothek → Anzeigen nach Spiel und Anzeigeart filtern, konkrete Varianten ansehen und Projekten zuordnen. Quellen in [ANZEIGEN_BESTAND.md](ANZEIGEN_BESTAND.md). Zeitwerte sind feste Beispiele; Editor und Optionsprüfung bleiben offen. |
| Spieleranzeigen und Pulte | 146 Varianten in 13 Modellen aus allen acht Spielen sowie Profil/Shop. Profilfenster, Lobbyplätze, Porträts, Ranglisten und Namenspulte; 14 Pultfamilien und vorhandene Ausschnitte aller 19 Avatare. | Bibliothek → Spieleranzeigen & Pulte nach Spiel und Baustein filtern und konkrete Varianten Projekten zuordnen. Quellen in [SPIELER_BESTAND.md](SPIELER_BESTAND.md). Editoroptionen bleiben offen. |
| Lobbys und Übersichten | 134 Quellvarianten in sieben Modellen aus allen sieben Mehrspielerspielen. Gemeinsamer Standardraum und Übersicht; Perfect mit vorhandener eigener Anordnung. | Bibliothek → Lobbys & Übersichten nach Spiel/Lobbyart filtern und konkrete Varianten Projekten zuordnen. Bestand: [LOBBYS_BESTAND.md](LOBBYS_BESTAND.md). Bisheriger allgemeiner Entwurf bleibt erhalten; Editoroptionen später. |
| Bretter und Spielflächen | Parametrischer Brettgenerator, Conquest-Tisch, Kartenfilz und Würfelfläche vorhanden. | Unterschiedliche Aufgaben und Gestaltungsmöglichkeiten je Variante erfassen. |
| Figuren und Spielsteine | Werkstattfiguren und Conquest-Truppenmarken vorhanden. | Spielgebundene Marken und frei gestaltete Figuren unterscheidbar zuordnen. |
| Würfel | Werkstattmodelle, dddice und Conquest-Würfelsymbole vorhanden. | Geometrie, Material, Anzeige und tatsächliche Bewegung im Gespräch klären. |
| Karten | Werkstattkarte, allgemeiner Kartentisch und gemeinsame Conquest-Länderkarte vorhanden. | Kartengestaltung und spielabhängige Inhalte getrennt zuordnen. |
| Hintergründe, Titelbilder, Flyer | Fertige Bilddateien; außerdem zusammengesetzte Spielpräsentationen. | Import, Ansehen, Auswahl und Projektzuordnung. Keine Editoranzeige für diese drei Bildarten. |
| Icons und Avatare | Bildeditor für Ausschnitte; registrierte Avatarbilder und SVG-Makros vorhanden. | Umfang des jeweiligen Editors später gemeinsam prüfen; Profilausrüstung bleibt maßgeblich. |
| Geräusche und Musik | Button-Audiokatalog, Würfelpaket und weitere spielgebundene Klänge vorhanden. | Hörbare Bestände mit Herkunft und Verwendungszweck erfassen; neue Klänge erst bedarfsbezogen recherchieren. |
| Schriften, Materialien und Stile | Lokale Schriftfamilien, Buttonmaterialien und räumliche Materialien vorhanden. | Auswahl verbessern und gemeinsame Quellen bewahren. |
| Kamera, Licht und Bewegung | Conquest-Kamera und begrenzte Werkstattbewegung vorhanden. | Projektentscheidungen und Objekteigenschaften; keine fertige allgemeine Physik behaupten. |

Die aktuelle Conquest-Spielansicht lädt `table-surface.js` über `scene.js`.
`static/conquest-table.js` bleibt als ältere Quelle erhalten und belegt allein
kein aktuell verwendetes Inventarfenster. Die Einbindung des Werkstatt-Renderers
erfolgt über die Aliaszuordnung in `conquest.py`, nicht durch unabhängige Kopien.

Aktuelle Reihenfolge nach Nutzerentscheidung vom 26.10.2026: Nach der
vervollständigten Buttonaufnahme haben Aufnahme und Anpassung der übrigen
Elemente Vorrang. Dafür sollen zunächst zusammenhängende Aufgaben mit längeren
Prompts bearbeitet werden. Die gemeinsame Prüfung und Anpassung sinnvoller
Buttonoptionen ist ausdrücklich für später vorgemerkt und keine Voraussetzung
für die nächsten Elementarten. Dies ersetzt die frühere Reihenfolge, in der
die Buttonprüfung vor weiteren Elementeditoren stand. Ein vollständiger
Button-Einsatzweg und die Projektvorschau bleiben zurückgestellt. Bei der
späteren Optionsprüfung jeweils einen kleinen Bereich mit tatsächlichen
Beispielen behandeln; die Aufnahme eines Buttons gilt nicht als inhaltliche
Abnahme seiner Editoroptionen.

Für die Materialauswahl hat der Nutzer präzisiert: Erweiterungen sollen den
tatsächlichen Spielebestand abbilden können. Daraus wurden zunächst Farbflächen,
zweifarbige Verläufe und durchscheinende Flächen in der gemeinsamen Button-
Werkstatt ergänzt. Zweite Farbe und Flächendeckkraft sind bedarfsabhängige
Einstellungen; die drei bisherigen Materialien bleiben erhalten. Drei passende
Startvorlagen machen die Flächen ausprobierbar. Die Zuordnung der benötigten
Flächen zu ihren Quellen steht unter `button_surface_coverage` im JSON-Bericht.

Bildknöpfe wie der Perfect-Buzzer bleiben als vorhandenes Motiv erfasst. Ihre
Aufnahme als Button mit gespeicherter Verwendung ist noch offen. Ebenso sind
die konkrete Kontur, Schrift, Rahmen, Druckbewegung und die Einbindung jedes
bestehenden Buttons weiter zu prüfen; eine passende Flächenart allein macht
noch keine vollständige Übernahme des Originals.

### Sichtbare Aufnahme in die Werkstattbibliothek

Die Bestandsaufnahme mit 19 Familien und die nun 15 Elementbereiche im Menü sind
getrennt ausgewiesen; die vier weiteren Familien stehen im aufklappbaren
Bestandsbereich. Die gemeinsame Werkstatt bleibt auf 8776. Der Desktop-Starter
öffnet sie direkt statt der älteren Übersicht.

106 Buttons sind nun aus tatsächlich verbundenen Quellen in Bibliothek → Buttons
aufgenommen: 99 aus Spielvorlagen und sieben gemeinsam gerenderte Conquest-Aktionen.
Die Auswahl „Im Spiel verwendet“ und der Spielfilter machen insbesondere die
Guesstimate-Startseiten-, Frage- und Ergebnisbuttons auffindbar. Die Vorschau liest
die vorhandenen Vorlagen und Styles; sie führt keine Spielaktionen aus. Beispielwerte
stehen stellvertretend für zustandsabhängige Beschriftungen. Projektmappen halten
die Quelldaten und Prüfsummen ihrer gewählten Originale fest.

Die sieben bereits gemeinsam gerenderten Conquest-Aktionen lassen sich als eigene
Entwürfe bearbeiten. Bei anderen Originalen zeigt die Ansicht die noch ausstehende
Editoranbindung ausdrücklich an. Weitere dynamische Kontrollen und die vollständige
Bearbeitbarkeit aller Originale sind damit nicht erledigt.


### Vervollständigte lokale Buttonaufnahme (26.10.2026)

Die aktuelle Aufnahme steht in [BUTTON_BESTAND.md](BUTTON_BESTAND.md) und
[BUTTON_BESTAND.json](BUTTON_BESTAND.json). Sie ersetzt die obige Zwischenangabe
106/99 und die dort noch offene gemeinsame Editoranbindung: 144 Quellverwendungen
als 85 Modelle, alle registrierten Buttons im gemeinsamen Kontureditor öffnbar.
Auch gemeinsame Lobbyübersichten, Navigationsknöpfe, Conquest-Nebenaktionen und
dynamische Würfel-/Kniffel-/Kartenbadge-Buttons sind zugeordnet. Die jeweiligen
Spiele finden gemeinsame Quellen über denselben Bibliothekseintrag.

Karten- und Truppen-Klickflächen bleiben ihren Spielelementen zugeordnet. Der
Bestandsbericht grenzt diese, nur für die Offline-Demo verwendete Kontrollen und
alte, nicht eingebundene Quellen ausdrücklich ab. Die Quellenprüfung ersetzt
keinen vollständigen Durchlauf sämtlicher tatsächlicher Spielzustände. Originale
und Spielaktionen bleiben unverändert; weitere optische Angleichungen sind offen.

### Raumkulissen und Abschlussabgleich (27.10.2026)

Neun ganze Raumvarianten in zwei Grundmodellen (2D/3D) unter Hintergründe ergänzt;
die 15 bisherigen Bildmotive und Kennungen bleiben erhalten. Conquests Wand,
Möbel und Teppich als eine Komposition aus der ursprünglichen Raumfabrik. Eigene
Kulissen für Playtable und Perfect, gemeinsame Würfelkulissen und Profilbühne.

Abschlussabgleich aller acht aktuellen Spiele ohne offene Elementzuordnungen im
dokumentierten Umfang. Dabei fünf vollständige Quizfenstermodelle mit 30 festen
Beispielen ergänzt; Fragen weiterhin nur Datenquellen. Insgesamt 35 Fenster-
modelle / 114 Quellbeispiele. Keine Spiel-, Fragenbank- oder Entwurfsänderung.
Material-/Darstellungseigenschaften und Editoroptionen bleiben spätere Arbeiten.
Belege und Grenzen: [WERKSTATT_ABSCHLUSSPRUEFUNG.md](WERKSTATT_ABSCHLUSSPRUEFUNG.md).

### Gemeinsame Material-/Ansichtsauswahl (27.10.2026)

Neun Materialfamilien mit Originalbeispielen und drei Darstellungsbeispielen als
Projekteigenschaften aufbereitet. 17 Elementbereiche bleiben unverändert; keine
Materialeinträge als zusätzliche Spielobjekte. Materialwünsche lassen sich ohne
Änderung der gewählten Originalelemente speichern und mit eingefrorener Herkunft
übergeben. Passende feste Schriftstile verknüpft; keine allgemeine Effektmatrix.
Alte Mappen und persönliche Entwürfe erhalten; Editoroptionen bleiben offen.
Siehe [MATERIAL_DARSTELLUNG.md](MATERIAL_DARSTELLUNG.md).

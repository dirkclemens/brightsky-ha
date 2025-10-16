# BrightSky Weather Integration für Home Assistant

Diese Integration nutzt die kostenlose [BrightSky API](https://brightsky.dev/), um Wetterdaten vom Deutschen Wetterdienst (DWD) in Home Assistant bereitzustellen.

## Features

- Aktuelle Wetterdaten und Vorhersagen ohne API-Key
- Tages- und Stundenvorhersagen
- Wetter-Entität mit detaillierten Attributen
- Sensor-Entitäten für alle verfügbaren Wetterdaten
- Optimiert für deutsche Wetterbedingungen und Einheiten

## Installation

### HACS (empfohlen)

1. Fügen Sie dieses Repository als Custom Repository in HACS hinzu:
   - Gehen Sie zu HACS > Integration > Drei-Punkte-Menü > Benutzerdefiniertes Repository
   - Fügen Sie folgende URL ein: `https://github.com/dirkclemens/brightsky-ha`
   - Wählen Sie Kategorie: Integration

2. Suchen Sie nach "BrightSky Weather" und installieren Sie es

3. Starten Sie Home Assistant neu

### Manuelle Installation

1. Laden Sie das neueste Release herunter
2. Entpacken Sie den Inhalt in den Ordner `custom_components/brightsky` in Ihrem Home Assistant Konfigurationsverzeichnis
3. Starten Sie Home Assistant neu

## Konfiguration

1. Gehen Sie zu Einstellungen > Geräte & Dienste > Integrationen
2. Klicken Sie auf "+ Integration hinzufügen"
3. Suchen Sie nach "BrightSky Weather"
4. Folgen Sie den Anweisungen im Konfigurationsassistenten

## Hinweise zur Verwendung

- BrightSky liefert primär **deutsche Wetterdaten** vom DWD
- Im Gegensatz zu vielen anderen Wetter-APIs benötigt BrightSky **keinen API-Key**
- Die Daten werden vom DWD in der Regel stündlich aktualisiert
- Ein Scan-Intervall von 900 Sekunden (15 Minuten) ist ausreichend

## Verfügbare Daten

- Temperatur
- Gefühlte Temperatur
- Luftfeuchtigkeit
- Luftdruck
- Taupunkt
- Windgeschwindigkeit und -richtung
- Niederschlag
- Bewölkungsgrad
- Sichtweite
- Wetterbedingung

## Fehlerbehebung

Wenn Probleme auftreten:

1. Überprüfen Sie die Home Assistant Logs auf Fehler im Zusammenhang mit `brightsky`
2. Stellen Sie sicher, dass der angegebene Standort in Deutschland liegt für beste Ergebnisse
3. Prüfen Sie die Verbindung zur BrightSky API unter https://api.brightsky.dev/status

## Lizenz

Diese Integration steht unter der [Creative Commons BY 4.0 (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/) Lizenz.

Siehe auch 
* https://brightsky.dev/
* https://www.dwd.de/EN/service/legal_notice/legal_notice.html

## Danksagung

- [BrightSky](https://brightsky.dev/) für die großartige, kostenlose API
- [Deutscher Wetterdienst (DWD)](https://www.dwd.de/) für die Bereitstellung der Open-Data-Wetterdaten

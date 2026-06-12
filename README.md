# TableDiffGenerator

TableDiffGenerator vergleicht bis zu vier HTML-Dateien, die Key/Value-Tabellen enthalten, und erzeugt daraus einen HTML-Vergleichsreport.

Das Tool ist fuer exportierte Tabellenberichte gedacht, bei denen relevante Tabellen an einer gemeinsamen Ueberschrift erkannt werden. Standardmaessig sucht es nach Tabellenueberschriften mit `Codeplug\\`.

## Funktionen

- Vergleich von 1 bis 4 HTML-Dateien
- automatische Erkennung relevanter Tabellen per Suchbegriff
- gemeinsame Darstellung gleicher Tabellen nebeneinander
- farbliche Markierung:
  - hellgruen fuer gleiche Werte
  - orange fuer abweichende Werte
  - rot fuer fehlende Tabellen oder Keys
- einklappbare Tabellen im Report
- Inhaltsverzeichnis mit Suchfunktion
- Schaltflaechen zum Auf- und Zuklappen aller Tabellen
- Navigation zurueck zum Dateianfang pro Tabelle
- einfache GUI fuer Linux und Windows
- keine externen Python-Abhaengigkeiten

## Nutzung

Ohne Kommandozeilenargumente startet die GUI:

```bash
python3 compare_codeplug_html.py
```

In der GUI koennen bis zu vier HTML-Dateien ausgewaehlt werden. Der Tabellen-Suchbegriff ist mit `Codeplug\\` vorbelegt und kann angepasst werden. Nach dem Start des Vergleichs wird der Report erzeugt und, wenn moeglich, ueber die Betriebssystemfunktionen im Standardbrowser geoeffnet.

Die Kommandozeile bleibt weiterhin nutzbar:

```bash
python3 compare_codeplug_html.py file1.html file2.html -o vergleich.html
```

Bis zu vier Dateien sind moeglich:

```bash
python3 compare_codeplug_html.py file1.html file2.html file3.html file4.html -o vergleich.html
```

Der Tabellen-Suchbegriff ist variabel. Standard ist `Codeplug\\`.

```bash
python3 compare_codeplug_html.py file1.html file2.html --table-marker "Codeplug\\" -o vergleich.html
```

Kurzform:

```bash
python3 compare_codeplug_html.py file1.html file2.html -m "Codeplug\\" -o vergleich.html
```

## Hinweise

Die Eingabe-HTML-Dateien und erzeugten Reports werden nicht versioniert. Die `.gitignore` schliesst `*.html` und `*.htm` aus.

## Lizenz

Dieses Projekt steht unter der CC0-1.0-Lizenz. Details stehen in `LICENSE`.

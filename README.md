# Eurex GC Auswertung

Kleine Python-CLI zur Auswertung von Eurex GC Pooling Basket-Dateien.

## Funktionen

- Einlesen vorhandener Eurex-CSV-Dateien
- automatische Basket-Erkennung
- Aufbereitung von ISIN, Bezeichnung, Haircut und Settlement Location
- Filterung einzelner Baskets
- Ausgabe als Terminaltabelle
- Export als CSV

## Start

```bash
python gc_collateral_auswertung.py
```

Optional kann ein bestimmter Basket ausgewählt werden:

```bash
python gc_collateral_auswertung.py --basket eu
```

## Daten

Die Anwendung liest die CSV-Dateien aus:

```text
Eurex Dateien/
```

Die Originaldateien werden nicht verändert.

## Output

Der aufbereitete Gesamtexport wird im Ordner `output/` gespeichert.

#!/usr/bin/env python3
"""CLI für die Auswertung vorhandener Eurex-Basket-Dateien."""
import argparse
import csv
import sys
from pathlib import Path
from src.loaders import discover_files, load_file
from src.processing import process_file
from src.reporting import export_csv, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--basket', help='Basketname aus den Metadaten (Groß-/Kleinschreibung egal)')
    parser.add_argument('--file', help='CSV-Dateiname innerhalb von Eurex Dateien')
    parser.add_argument('--haircut-unit', choices=['auto', 'percent', 'fraction'], default='auto',
                        help='Einheit unmarkierter Haircuts; auto nutzt die Spaltenüberschrift')
    parser.add_argument('--limit', type=int, default=20, help='Angezeigte Datensätze, 0 = alle (Standard: 20)')
    args = parser.parse_args()
    if args.limit < 0:
        parser.error('--limit muss mindestens 0 sein.')
    base = Path(__file__).resolve().parent
    try:
        files = discover_files(base / 'Eurex Dateien')
        if args.file:
            files = [p for p in files if p.name == args.file]
            if not files:
                raise ValueError('Ausgewählte Datei nicht im Datenordner gefunden.')
        records = []
        for path in files:
            loaded = load_file(path)
            rows, warnings = process_file(path, loaded, args.haircut_unit)
            if args.basket:
                rows = [r for r in rows if r['Basket'].casefold() == args.basket.casefold()]
                if not rows:
                    continue
            print(f'Eingelesen: {path.name} ({len(rows)} Datensätze)')
            for warning in warnings:
                print(f'Hinweis: {warning}', file=sys.stderr)
            records.extend(rows)
        if not records:
            raise ValueError('Keine Datensätze für die Auswahl gefunden.')
        destination = base / 'output' / 'eurex_gc_auswertung.csv'
        export_csv(records, destination)
        report(records, args.limit)
        print(f'Export: {destination.relative_to(base)} ({len(records)} Datensätze)')
        return 0
    except (ValueError, OSError, csv.Error) as exc:
        print(f'Fehler: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())

"""Terminalansicht und UTF-8-CSV-Export."""
import csv
from collections import Counter

FIELDS = ['ISIN', 'Description', 'Basket', 'Haircut', 'Settlement_Location', 'Source_File', 'As_Of_Date']


def export_csv(records, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(records)


def report(records, limit):
    print('Eurex GC Auswertung')
    for basket, count in sorted(Counter(r['Basket'] for r in records).items()):
        unique = len({r['ISIN'] for r in records if r['Basket'] == basket})
        print(f'Basket: {basket} | Datensätze: {count} | Wertpapiere (ISIN): {unique}')
    shown = records if limit == 0 else records[:limit]
    columns = FIELDS[:5]
    try:
        from rich.console import Console
        from rich.table import Table
    except ImportError:
        print('\t'.join(columns))
        for row in shown:
            print('\t'.join(row[c] for c in columns))
    else:
        table = Table(show_lines=False)
        for column in columns:
            table.add_column(column)
        for row in shown:
            table.add_row(*(row[c] for c in columns))
        Console().print(table)
    if len(shown) < len(records):
        print(f'Anzeige: {len(shown)} von {len(records)} Datensätzen; --limit 0 zeigt alle. Export enthält alle ausgewählten Daten.')

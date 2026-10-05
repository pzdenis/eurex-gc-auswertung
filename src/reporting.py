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
        print(f'Basket: {basket} | Datensätze: {count}')
    shown = records if limit == 0 else records[:limit]
    columns = FIELDS[:5]
    try:
        from rich import box
        from rich.console import Console
        from rich.table import Table
    except ImportError:
        print('\t'.join(columns))
        for row in shown:
            print('\t'.join(row[c] for c in columns))
    else:
        console = Console()
        basket_width = max(6, max(len(r['Basket']) for r in shown))
        haircut_width = max(7, max(len(r['Haircut']) for r in shown))
        description_width = min(30, max(1, console.width -
                                       (12 + basket_width + haircut_width + 19 + 16)))
        table = Table(box=box.HEAVY_HEAD, show_lines=False,
                      header_style='bold', safe_box=False, padding=(0, 1))
        table.add_column('ISIN', min_width=12, no_wrap=True)
        table.add_column('Description', width=description_width, no_wrap=True,
                         overflow='ellipsis')
        table.add_column('Basket', min_width=basket_width,
                         no_wrap=True)
        table.add_column('Haircut', min_width=haircut_width,
                         justify='right', no_wrap=True)
        table.add_column('Settlement Location', min_width=19, no_wrap=True)
        for row in shown:
            table.add_row(*(row[c] for c in columns))
        console.print(table, markup=False, highlight=False)
    if len(shown) < len(records):
        print(f'Anzeige: {len(shown)} von {len(records)} Datensätzen; --limit 0 zeigt alle. Export enthält alle ausgewählten Daten.')

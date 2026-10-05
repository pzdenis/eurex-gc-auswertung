"""CSV-Erkennung einschließlich Eurex-Metadaten vor dem Tabellenkopf."""
import csv
import re
from pathlib import Path


def column_key(value):
    return re.sub(r'[^a-z0-9%]', '', value.lower())


def load_file(path):
    raw = path.read_bytes()
    for encoding in ('utf-8-sig', 'cp1252'):
        try:
            text = raw.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        raise ValueError(f'{path.name}: Zeichenkodierung nicht lesbar.')
    for delimiter in (',', ';', '\t', '|'):
        try:
            rows = list(csv.reader(text.splitlines(), delimiter=delimiter, strict=True))
        except csv.Error:
            continue
        header_index = next((i for i, row in enumerate(rows)
                             if any(column_key(c) == 'isin' for c in row)), None)
        if header_index is not None:
            break
    else:
        raise ValueError(f'{path.name}: Keine Tabellenüberschrift mit ISIN gefunden.')
    headers = [c.strip() for c in rows[header_index]]
    if len(set(map(column_key, headers))) != len(headers):
        raise ValueError(f'{path.name}: Doppelte Spaltennamen.')
    metadata = '\n'.join(' '.join(row) for row in rows[:header_index])
    match = re.search(r'GC\s+Pooling[^\w]*\s*(.*?)\s+Basket', metadata, re.I)
    basket = match.group(1).strip() if match else re.sub(
        r'^euro_gc_pooling_?|_basket$', '', path.stem, flags=re.I).replace('_', ' ').strip()
    basket = basket or path.stem
    date = re.search(r'\b\d{2}\.\d{2}\.\d{4}\b', metadata)
    records = []
    for line, row in enumerate(rows[header_index + 1:], header_index + 2):
        if not any(c.strip() for c in row):
            continue
        if len(row) != len(headers):
            raise ValueError(f'{path.name}, Zeile {line}: {len(row)} statt {len(headers)} Felder.')
        records.append((line, dict(zip(headers, (c.strip() for c in row)))))
    return headers, records, basket, date.group(0) if date else ''


def discover_files(directory):
    if not directory.is_dir():
        raise ValueError(f'Datenordner fehlt: {directory}')
    files = sorted(p for p in directory.iterdir() if p.is_file() and p.suffix.lower() == '.csv')
    if not files:
        raise ValueError(f'Keine CSV-Dateien in {directory}.')
    return files

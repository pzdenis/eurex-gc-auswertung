"""Normalisierung; Haircuts intern in Prozentpunkten, ohne Positionsdaten."""
from decimal import Decimal, InvalidOperation
from .loaders import column_key

ALIASES = {
    'ISIN': {'isin'},
    'Description': {'briefdescription', 'description', 'wertpapierbezeichnung'},
    'Haircut': {'haircut%', 'haircut', 'haircutpercent', 'haircutpercentage'},
    'Settlement_Location': {'settlementlocation'},
    'Basket': {'basket'},
}
MISSING = {'', 'na', 'n/a', 'null', 'nan', '-'}


def parse_haircut(value, unit):
    if value.lower() in MISSING:
        return ''
    explicit_percent = value.endswith('%')
    number = value.removesuffix('%').strip().replace(',', '.')
    try:
        haircut = Decimal(number)
    except InvalidOperation as exc:
        raise ValueError(f'Ungültiger Haircut: {value!r}') from exc
    if not haircut.is_finite():
        raise ValueError(f'Ungültiger Haircut: {value!r}')
    if not explicit_percent:
        if unit == 'auto':
            raise ValueError('Haircut-Einheit uneindeutig; --haircut-unit percent oder fraction angeben.')
        if unit == 'fraction':
            haircut *= 100
    if not 0 <= haircut <= 100:
        raise ValueError(f'Haircut außerhalb 0–100 %: {value!r}')
    return f'{haircut:.2f} %' if haircut == haircut.quantize(Decimal('.01')) else f'{haircut:f} %'


def process_file(path, loaded, unit='auto'):
    headers, records, basket, date = loaded
    mapping = {}
    for target, aliases in ALIASES.items():
        matches = [h for h in headers if column_key(h) in aliases]
        if len(matches) > 1:
            raise ValueError(f'{path.name}: Mehrdeutige Spalten für {target}.')
        mapping[target] = matches[0] if matches else None
    if not mapping['ISIN']:
        raise ValueError(f'{path.name}: ISIN fehlt.')
    warnings = [f'{path.name}: Spalte {k} fehlt; Werte bleiben leer.'
                for k, v in mapping.items() if not v and k not in ('Basket', 'ISIN')]
    haircut_header = mapping['Haircut']
    effective_unit = unit
    if unit == 'auto' and haircut_header and ('%' in haircut_header or 'percent' in haircut_header.lower()):
        effective_unit = 'percent'
    output = []
    for line, record in records:
        row = {k: record.get(v, '') if v else '' for k, v in mapping.items()}
        if not row['ISIN']:
            raise ValueError(f'{path.name}, Zeile {line}: ISIN fehlt.')
        row['Basket'] = row['Basket'] or basket
        try:
            row['Haircut'] = parse_haircut(row['Haircut'], effective_unit)
        except ValueError as exc:
            raise ValueError(f'{path.name}, Zeile {line}: {exc}') from exc
        row.update(Source_File=path.name, As_Of_Date=date)
        output.append(row)
    return output, warnings

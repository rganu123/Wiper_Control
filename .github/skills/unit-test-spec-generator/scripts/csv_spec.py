import argparse
import csv
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path


COLUMNS = (
    'test_id', 'story_id', 'design_file', 'unit_id', 'requirement_ids',
    'design_refs', 'category', 'title', 'variant', 'preconditions', 'mocks',
    'inputs', 'steps', 'expected_result', 'status', 'notes',
)
CATEGORIES = {'Positive', 'Negative', 'Boundary'}
REFERENCE = r'(?:REQ-[FN]|ARC|IF|SAF|TC)-\d{3,}'
TEMPLATE = Path(__file__).resolve().parent.parent / 'assets' / 'unit-test-spec-template.csv'


def read_csv(path):
    with path.open(encoding='utf-8-sig', newline='') as stream:
        records = list(csv.reader(stream, strict=True))
    if not records or records[0] != list(COLUMNS):
        raise ValueError(f'{path}: header must exactly match the CSV contract')
    rows = []
    for record_number, record in enumerate(records[1:], 2):
        if len(record) != len(COLUMNS):
            raise ValueError(f'{path}: record {record_number} has {len(record)} fields')
        rows.append(dict(zip(COLUMNS, record)))
    return rows


def inside_root(root, supplied):
    resolved = (root / supplied).resolve()
    try:
        resolved.relative_to(root)
    except ValueError as error:
        raise ValueError('Paths must stay inside the workspace root') from error
    return resolved


def reference_list(value):
    return [entry.strip() for entry in value.split(';') if entry.strip()]


def validate_rows(rows, root, design):
    text = design.read_text(encoding='utf-8-sig')
    definitions = set(re.findall(r'^\|\s*(' + REFERENCE + r')\s*\|', text, re.MULTILINE))
    requirements = {entry for entry in definitions if entry.startswith('REQ-')}
    if not requirements:
        raise ValueError('Design has no requirement definitions in Markdown table first cells')
    if not rows:
        raise ValueError('Specification must contain cases or exclusion records')
    covered = set()
    identifiers = set()
    units = {}
    errors = []
    for record_number, row in enumerate(rows, 2):
        prefix = f'record {record_number}'
        if set(row) != set(COLUMNS) or any(not isinstance(value, str) for value in row.values()):
            errors.append(f'{prefix}: exact string-valued columns required')
            continue
        if any(not row[column].strip() for column in COLUMNS if column != 'notes'):
            errors.append(f'{prefix}: required field is empty')
        if not re.fullmatch(r'UT-\d{3,}', row['test_id']) or row['test_id'] in identifiers:
            errors.append(f'{prefix}: invalid or duplicate test_id')
        identifiers.add(row['test_id'])
        if row['story_id'] not in text:
            errors.append(f'{prefix}: story_id not found in design')
        try:
            if Path(row['design_file']).is_absolute() or '\\' in row['design_file']:
                raise ValueError('design_file must be relative with forward slashes')
            if inside_root(root, row['design_file']) != design:
                raise ValueError('design_file does not match selected design')
        except ValueError as error:
            errors.append(f'{prefix}: {error}')
        requirement_ids = reference_list(row['requirement_ids'])
        design_refs = reference_list(row['design_refs'])
        if not requirement_ids or not set(requirement_ids) <= requirements:
            errors.append(f'{prefix}: undefined requirement reference')
        covered.update(requirement_ids)
        if not design_refs or not set(design_refs) <= definitions:
            errors.append(f'{prefix}: undefined design reference')
        if row['category'] not in CATEGORIES:
            errors.append(f'{prefix}: invalid category')
        if row['status'] not in {'Ready', 'Blocked', 'NotApplicable'}:
            errors.append(f'{prefix}: invalid status')
        if row['variant'] not in {'S', 'M', 'L', 'All', 'N/A'}:
            errors.append(f'{prefix}: invalid variant')
        if row['unit_id'] == 'N/A':
            if row['status'] != 'NotApplicable':
                errors.append(f'{prefix}: excluded unit must be NotApplicable')
        elif not row['unit_id'].startswith('ARC-') or row['unit_id'] not in definitions:
            errors.append(f'{prefix}: unit_id must reference a defined architecture element')
        else:
            units.setdefault(row['unit_id'], set()).add(row['category'])
        try:
            mocks = json.loads(row['mocks'])
            if not isinstance(mocks, dict):
                raise ValueError('mocks must be a JSON object')
            if not mocks and not row['notes'].strip():
                errors.append(f'{prefix}: explain why no mocks are needed')
        except (ValueError, TypeError) as error:
            errors.append(f'{prefix}: invalid mocks JSON: {error}')
        if (row['status'] != 'Ready' or row['variant'] == 'All') and not row['notes'].strip():
            errors.append(f'{prefix}: notes required for status or variant justification')
        if row['status'] == 'Ready' and re.search(r'\bTBD\b', ' '.join(row.values())):
            errors.append(f'{prefix}: unresolved TBD cannot be Ready')
    missing = requirements - covered
    if missing:
        errors.append('Unaccounted requirements: ' + ', '.join(sorted(missing)))
    for unit_id, categories in units.items():
        if categories != CATEGORIES:
            errors.append(f'{unit_id}: missing categories {sorted(CATEGORIES - categories)}')
    if errors:
        raise ValueError('\n'.join(errors))


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


class CsvSpecTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.design = self.root / 'design.md'
        self.design.write_text('# US-032\n| REQ-F-001 | Rule |\n| ARC-001 | Unit |\n', encoding='utf-8')
        self.rows = []
        for index, category in enumerate(sorted(CATEGORIES), 1):
            row = dict.fromkeys(COLUMNS, 'fixture')
            row.update(test_id=f'UT-{index:03}', story_id='US-032', design_file='design.md',
                       unit_id='ARC-001', requirement_ids='REQ-F-001', design_refs='ARC-001',
                       category=category, variant='S', mocks='{"clock": "fake"}', status='Ready')
            self.rows.append(row)

    def test_round_trip(self):
        self.rows[0]['title'] = 'Quoted "value", comma\nand newline'
        self.rows[0]['notes'] = 'UTF-8: \u00b0C'
        target = self.root / 'spec.csv'
        write_csv(target, self.rows)
        self.assertEqual(read_csv(target), self.rows)
        validate_rows(read_csv(target), self.root, self.design)
        with self.assertRaises(FileExistsError):
            write_csv(target, self.rows)

    def test_rejections(self):
        mutations = (
            ('test_id', 'UT-002'), ('requirement_ids', 'REQ-F-999'),
            ('design_refs', 'IF-999'), ('unit_id', 'ARC-999'), ('mocks', '[]'),
            ('design_file', '../outside.md'), ('inputs', 'TBD'),
            ('category', 'Integration'), ('status', 'Passed'),
        )
        for column, value in mutations:
            with self.subTest(column=column):
                changed = [dict(row) for row in self.rows]
                changed[0][column] = value
                with self.assertRaises(ValueError):
                    validate_rows(changed, self.root, self.design)
        with self.assertRaises(ValueError):
            validate_rows(self.rows[:1], self.root, self.design)
        with self.assertRaises(ValueError):
            validate_rows([], self.root, self.design)

    def test_bad_csv(self):
        target = self.root / 'bad.csv'
        for content in ('wrong,header\n', ','.join(COLUMNS) + '\nshort,row\n',
                        ','.join(COLUMNS) + '\n"unclosed'):
            target.write_text(content, encoding='utf-8')
            with self.assertRaises((ValueError, csv.Error)):
                read_csv(target)

    def test_coverage_and_exclusions(self):
        self.design.write_text(self.design.read_text() + '| REQ-N-001 | Hardware |\n', encoding='utf-8')
        with self.assertRaises(ValueError):
            validate_rows(self.rows, self.root, self.design)
        excluded = dict(self.rows[0])
        excluded.update(test_id='UT-004', requirement_ids='REQ-N-001', unit_id='N/A',
                        status='NotApplicable', notes='Hardware timing is outside unit scope')
        validate_rows(self.rows + [excluded], self.root, self.design)


def main():
    parser = argparse.ArgumentParser(description='Generate and validate logical-unit CSV test specifications')
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('self-test')
    for command in ('generate', 'validate'):
        options = commands.add_parser(command)
        options.add_argument('--root', required=True, type=Path)
        options.add_argument('--design', required=True)
        if command == 'generate':
            options.add_argument('--rows', required=True, type=Path)
            options.add_argument('--output', required=True)
        else:
            options.add_argument('--csv', required=True)
    args = parser.parse_args()
    try:
        if read_csv(TEMPLATE):
            raise ValueError('CSV template must contain only the header')
        if args.command == 'self-test':
            result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(CsvSpecTests))
            return 0 if result.wasSuccessful() else 1
        root = args.root.resolve()
        design = inside_root(root, args.design)
        if args.command == 'generate':
            rows = json.loads(args.rows.read_text(encoding='utf-8-sig'))
            if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
                raise ValueError('Rows input must be a JSON array of objects')
            validate_rows(rows, root, design)
            output = inside_root(root, args.output)
            write_csv(output, rows)
        else:
            output = inside_root(root, args.csv)
        rows = read_csv(output)
        validate_rows(rows, root, design)
        print(f'PASS: {len(rows)} specification records; structure, references and coverage validated')
        return 0
    except (OSError, ValueError, csv.Error) as error:
        print(f'FAIL: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
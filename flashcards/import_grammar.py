import csv
from flashcards.models import Grammar

def run():
    csv_files = ['n5_grammar.csv', 'n4_grammar.csv', 'n3_grammar.csv', 'n2_grammar.csv']

    for csv_file in csv_files:
        with open(csv_file, newline='', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            for row in reader:
                level = row.get('level', '').strip()

                # header болон буруу level-г skip
                if level not in ['N5', 'N4', 'N3', 'N2']:
                    print(f"Skipping invalid level in {csv_file}: {level}")
                    continue

                # Хоосон баганад утга өгөх
                pattern = row.get('pattern', '').strip()
                meaning_jp = row.get('meaning_jp', '').strip()
                meaning_en = row.get('meaning_en', '').strip()
                example_jp = row.get('example_jp', '').strip()
                example_en = row.get('example_en', '').strip()
                structure = row.get('structure', '').strip()
                notes = row.get('notes', '').strip()

                Grammar.objects.create(
                    pattern=pattern,
                    meaning_jp=meaning_jp,
                    meaning_en=meaning_en,
                    example_jp=example_jp,
                    example_en=example_en,
                    structure=structure,
                    notes=notes,
                    level=level
                )

    print("All CSVs imported!")

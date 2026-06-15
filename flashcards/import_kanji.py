import csv
from flashcards.models import Kanji

def run(filename="n5_kanji.csv"):
    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)

        for row in reader:
            Kanji.objects.create(
                character=row[0].strip(),
                reading=row[1].strip(),
                meaning=row[2].strip(),
                level=row[3].strip()
            )

    print(f"{filename} import finished!")

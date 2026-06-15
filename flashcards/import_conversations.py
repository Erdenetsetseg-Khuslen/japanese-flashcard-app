import csv
from flashcards.models import Conversation

def run():
    with open('daily_conversations.csv', newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        print(reader.fieldnames)
        for row in reader:
            Conversation.objects.create(
                category=row['category'],
                japanese=row['japanese'],
                hiragana=row['hiragana'],
                meaning=row['meaning']
            )

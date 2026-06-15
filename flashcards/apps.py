from django.apps import AppConfig


class FlashcardsConfig(AppConfig):
    name = 'flashcards'

    def ready(self):
        import flashcards.signals
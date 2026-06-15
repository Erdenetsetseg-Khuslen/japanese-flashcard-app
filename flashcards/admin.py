from django.contrib import admin
from .models import Kanji, UserKanji, Grammar
from .models import Conversation



@admin.register(Kanji)
class KanjiAdmin(admin.ModelAdmin):
    list_display = ('character', 'meaning', 'level')  # kanji биш!


@admin.register(UserKanji)
class UserKanjiAdmin(admin.ModelAdmin):
    list_display = ('user', 'kanji', 'status')  # known биш!


@admin.register(Grammar)
class GrammarAdmin(admin.ModelAdmin):
    list_display = ('level', 'pattern')
    list_filter = ('level',)
    search_fields = ('pattern', 'meaning_en')
    ordering = ('level', 'pattern')

admin.site.register(Conversation)

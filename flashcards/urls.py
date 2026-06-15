from django.urls import path
from . import views

urlpatterns = [
    # 🔤 KANJI FLASHCARDS
    path('', views.flashcards, name='flashcards'),
    path('save/kanji/<int:kanji_id>/', views.toggle_save_kanji, name='toggle_save_kanji'),
    path('kanji-quiz/<str:level>/<str:mode>/', views.kanji_quiz, name='kanji_quiz'),

    # 📘 GRAMMAR FLASHCARDS
    path('grammar/<str:level>/', views.grammar_flashcards, name='grammar_flashcards'),
    path('save/grammar/<int:grammar_id>/', views.toggle_save_grammar, name='toggle_save_grammar'),

    # 🅰️ KANA
    path('kana/', views.kana, name='kana'),
    path('kana-quiz/', views.kana_quiz, name='kana_quiz'),
    path('update-score/', views.update_score, name='update_score'),
    
    # CONVERSATIONS
    path('conversation/<int:id>/', views.conversation_flashcard, name='conversation_flashcard'),
    path('conversation/<int:conv_id>/save/',
    views.toggle_save_conversation,
    name='toggle_save_conversation'),



    # 👤 ACCOUNT
    path("account/", views.account, name="account"),
    path("edit-profile/", views.edit_profile, name="edit_profile"),
]

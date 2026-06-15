from django.db import models
from django.contrib.auth.models import User


class Kanji(models.Model):
    character = models.CharField(max_length=10)   # 女
    reading = models.CharField(max_length=100)     # おんな
    meaning = models.CharField(max_length=100)    # women
    level = models.CharField(max_length=10) 

    def __str__(self):
        return self.character

class SavedKanji(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    kanji = models.ForeignKey(Kanji, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.kanji.character}"

class UserKanji(models.Model):
    STATUS_CHOICES = (
        ('known', 'Known'),
        ('unknown', 'Unknown'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    kanji = models.ForeignKey(Kanji, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    saved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.kanji.character}"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)

    emoji = models.CharField(max_length=10, blank=True)
    bio = models.TextField(max_length=200, blank=True)

    def __str__(self):
        return self.user.username
    
class Grammar(models.Model):
    LEVEL_CHOICES = [
        ('N5', 'N5'),
        ('N4', 'N4'),
        ('N3', 'N3'),
        ('N2', 'N2'),
    ]

    level = models.CharField(max_length=5, choices=LEVEL_CHOICES)

    pattern = models.CharField(max_length=100)  # 〜ている
    meaning_jp = models.TextField()
    meaning_en = models.TextField()

    example_jp = models.TextField()
    example_en = models.TextField()

    structure = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    saved_by = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return f"{self.pattern} ({self.level})"
    
class Conversation(models.Model):
    category = models.CharField(max_length=100)
    japanese = models.CharField(max_length=255)
    hiragana = models.CharField(max_length=255)
    meaning = models.CharField(max_length=255)

    def __str__(self):
        return self.japanese
    
class SavedConversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'conversation')
import random
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Kanji
from .models import SavedKanji
from .models import Grammar
from django.shortcuts import get_object_or_404
from .forms import ProfileForm
from .models import Profile
from django.http import JsonResponse
from .models import Conversation
from .models import Conversation, SavedConversation


# 🏠 Home page (guest + user)
def home(request):
    return render(request, 'home.html')


# 📝 Register page
def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        # Username шалгах
        if User.objects.filter(username=username).exists():
            return render(request, 'registration/register.html', {
                'error': 'Username аль хэдийн байна'
            })

        # User үүсгэх
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # Шууд login хийх
        login(request, user)
        return redirect('home')

    return render(request, 'registration/register.html')


# 🈶 Flashcards (login required)
@login_required
def flashcards(request):
    level = request.GET.get('level', 'N5')

    kanjis = list(
        Kanji.objects.filter(level=level).order_by('id')
    )

    if not kanjis:
        return render(request, 'flashcards/flashcard.html', {'kanji': None})

    index = request.session.get('kanji_index', 0)
    session_level = request.session.get('kanji_level')

    # level солигдвол index reset
    if session_level != level:
        index = 0
        request.session['kanji_level'] = level

    action = request.GET.get('action')

    if action == 'next' and index < len(kanjis) - 1:
        index += 1
    elif action == 'back' and index > 0:
        index -= 1

    request.session['kanji_index'] = index

    kanji = kanjis[index]

    is_saved = SavedKanji.objects.filter(
        user=request.user,
        kanji=kanji
    ).exists()

    return render(request, 'flashcards/flashcard.html', {
        'kanji': kanji,
        'level': level,
        'is_saved': is_saved,
        'can_go_back': index > 0,
        'can_go_next': index < len(kanjis) - 1,
        'position': f"{index + 1} / {len(kanjis)}"
    })


    
    
@login_required
def toggle_save_kanji(request, kanji_id):
    kanji = get_object_or_404(Kanji, id=kanji_id)
    
    level = request.POST.get('level', 'N5')

    saved = SavedKanji.objects.filter(user=request.user, kanji=kanji)

    if saved.exists():
        saved.delete()
    else:
        SavedKanji.objects.create(user=request.user, kanji=kanji)

    return redirect(f'/flashcards/?level={level}')


@login_required
def kanji_quiz(request, level, mode):

    # 🔁 RESET
    if request.GET.get("reset"):
        for key in ["quiz_ids", "current_index", "correct_count", "wrong_count"]:
            request.session.pop(key, None)

    # 🟢 SESSION INIT
    if "quiz_ids" not in request.session:
        kanjis = list(
            Kanji.objects.filter(level=level).order_by("?")[:20]
        )

        if not kanjis:
            return render(request, "flashcards/kanji_quiz.html", {
                "error": "No kanji found"
            })

        request.session["quiz_ids"] = [k.id for k in kanjis]
        request.session["current_index"] = 0
        request.session["correct_count"] = 0
        request.session["wrong_count"] = 0

    quiz_ids = request.session["quiz_ids"]
    index = request.session["current_index"]

    # 🏁 FINISH
    if index >= 20:
        return render(request, "flashcards/kanji_quiz.html", {
            "finished": True,
            "correct": request.session["correct_count"],
            "wrong": request.session["wrong_count"],
            "level": level,
            "mode": mode,
        })

    # ❓ CURRENT QUESTION
    question = get_object_or_404(Kanji, id=quiz_ids[index])

    # 📨 POST → CHECK → REDIRECT
    if request.method == "POST":
        selected = request.POST.get("answer")

        correct_answer = (
            question.meaning if mode == "meaning" else question.reading
        )

        if selected == correct_answer:
            request.session["correct_count"] += 1
        else:
            request.session["wrong_count"] += 1

        request.session["current_index"] += 1
        return redirect("kanji_quiz", level=level, mode=mode)

    # 🔹 CHOICES (GET үед)
    wrong = list(
        Kanji.objects
        .filter(level=level)
        .exclude(id=question.id)
        .order_by("?")[:3]
    )

    if mode == "meaning":
        correct = question.meaning
        wrong_values = [k.meaning for k in wrong]
    else:
        correct = question.reading
        wrong_values = [k.reading for k in wrong]

    choices = []
    for c in [correct] + wrong_values:
        choices.append({
            "value": c,
            "is_correct": c == correct
        })

    random.shuffle(choices)

    return render(request, "flashcards/kanji_quiz.html", {
        "question": question,
        "choices": choices,
        "index": index + 1,
        "total": 20,
        "level": level,
        "mode": mode,
    })


def grammar_flashcards(request, level):
    action = request.GET.get("action")
    level = request.GET.get("level") or level or "N5"
    grammars = list(Grammar.objects.filter(level=level).order_by("id"))

    if not grammars:
        return render(request, "flashcards/grammar.html", {"level": level})

    session_key = f"grammar_index_{level}"
    index = int(request.session.get(session_key, 0))

    if action == "next" and index < len(grammars) - 1:
        index += 1
    elif action == "back" and index > 0:
        index -= 1

    request.session[session_key] = index
    grammar = grammars[index]

    is_saved = request.user.is_authenticated and grammar.saved_by.filter(id=request.user.id).exists()

    context = {
        "grammar": grammar,
        "level": level,
        "position": f"{index+1} / {len(grammars)}",
        "can_go_next": index < len(grammars) - 1,
        "can_go_back": index > 0,
        "is_saved": is_saved,
    }

    return render(request, "flashcards/grammar.html", context)

    
@login_required
def toggle_save_grammar(request, grammar_id):
    grammar = get_object_or_404(Grammar, id=grammar_id)

    if request.user.is_authenticated:
        if request.user in grammar.saved_by.all():
            grammar.saved_by.remove(request.user)
        else:
            grammar.saved_by.add(request.user)

    level = grammar.level
    return redirect('grammar_flashcards', level=level)
    
def kana(request):
    hiragana = [
        ("あ","a"), ("い","i"), ("う","u"), ("え","e"), ("お","o"),
        ("か","ka"), ("き","ki"), ("く","ku"), ("け","ke"), ("こ","ko"),
        ("さ","sa"), ("し","shi"), ("す","su"), ("せ","se"), ("そ","so"),
        ("た","ta"), ("ち","chi"), ("つ","tsu"), ("て","te"), ("と","to"),
        ("な","na"), ("に","ni"), ("ぬ","nu"), ("ね","ne"), ("の","no"),
        ("は","ha"), ("ひ","hi"), ("ふ","fu"), ("へ","he"), ("ほ","ho"),
        ("ま","ma"), ("み","mi"), ("む","mu"), ("め","me"), ("も","mo"),
        ("や","ya"), ("ゆ","yu"), ("よ","yo"),
        ("ら","ra"), ("り","ri"), ("る","ru"), ("れ","re"), ("ろ","ro"),
        ("わ","wa"), ("を","wo"), ("ん","n"),
    ]

    katakana = [
        ("ア","a"), ("イ","i"), ("ウ","u"), ("エ","e"), ("オ","o"),
        ("カ","ka"), ("キ","ki"), ("ク","ku"), ("ケ","ke"), ("コ","ko"),
        ("サ","sa"), ("シ","shi"), ("ス","su"), ("セ","se"), ("ソ","so"),
        ("タ","ta"), ("チ","chi"), ("ツ","tsu"), ("テ","te"), ("ト","to"),
        ("ナ","na"), ("ニ","ni"), ("ヌ","nu"), ("ネ","ne"), ("ノ","no"),
        ("ハ","ha"), ("ヒ","hi"), ("フ","fu"), ("ヘ","he"), ("ホ","ho"),
        ("マ","ma"), ("ミ","mi"), ("ム","mu"), ("メ","me"), ("モ","mo"),
        ("ヤ","ya"), ("ユ","yu"), ("ヨ","yo"),
        ("ラ","ra"), ("リ","ri"), ("ル","ru"), ("レ","re"), ("ロ","ro"),
        ("ワ","wa"), ("ヲ","wo"), ("ン","n"),
    ]

    return render(request, 'flashcards/kana.html', {
        'hiragana': hiragana,
        'katakana': katakana,
    })
    
def kana_quiz(request):
    hiragana = [
        ("あ","a"), ("い","i"), ("う","u"), ("え","e"), ("お","o"),
        ("か","ka"), ("き","ki"), ("く","ku"), ("け","ke"), ("こ","ko"),
        ("さ","sa"), ("し","shi"), ("す","su"), ("せ","se"), ("そ","so"),
        ("た","ta"), ("ち","chi"), ("つ","tsu"), ("て","te"), ("と","to"),
        ("な","na"), ("に","ni"), ("ぬ","nu"), ("ね","ne"), ("の","no"),
        ("は","ha"), ("ひ","hi"), ("ふ","fu"), ("へ","he"), ("ほ","ho"),
        ("ま","ma"), ("み","mi"), ("む","mu"), ("め","me"), ("も","mo"),
        ("や","ya"), ("ゆ","yu"), ("よ","yo"),
        ("ら","ra"), ("り","ri"), ("る","ru"), ("れ","re"), ("ろ","ro"),
        ("わ","wa"), ("を","wo"), ("ん","n"),
    ]

    # 👉 Score session эхлүүлэх
    if 'score' not in request.session:
        request.session['score'] = 0
        request.session['total'] = 0

    question = random.choice(hiragana)
    choices = random.sample(hiragana, 4)

    if question not in choices:
        choices[0] = question

    random.shuffle(choices)

    context = {
        "question": question,
        "choices": choices,
        "score": request.session['score'],
        "total": request.session['total'],
    }

    return render(request, "flashcards/kana_quiz.html", context)

def update_score(request):
    correct = request.GET.get("correct") == "true"

    request.session['total'] += 1

    if correct:
        request.session['score'] += 1

    return JsonResponse({"status": "ok"})


def conversation_list(request):
    conversations = Conversation.objects.all()
    return render(request, 'flashcards/conversation_list.html', {
        'conversations': conversations
    })


def conversation_flashcard(request, id=1):
    conversations = Conversation.objects.all().order_by('id')
    current = get_object_or_404(Conversation, id=id)

    next_conv = conversations.filter(id__gt=id).first()
    prev_conv = conversations.filter(id__lt=id).last()

    is_saved = False
    if request.user.is_authenticated:
        is_saved = SavedConversation.objects.filter(
            user=request.user,
            conversation=current
        ).exists()

    context = {
        'conv': current,
        'next': next_conv,
        'prev': prev_conv,
        'is_saved': is_saved,
    }
    return render(request, 'flashcards/conversation_flashcard.html', context)


@login_required
def saved_conversations(request):
    saved = SavedConversation.objects.filter(user=request.user)

    return render(request, 'account/saved_conversations.html', {
        'saved': saved
    })


@login_required
def toggle_save_conversation(request, conv_id):
    conv = get_object_or_404(Conversation, id=conv_id)

    saved = SavedConversation.objects.filter(
        user=request.user,
        conversation=conv
    )

    if saved.exists():
        saved.delete()
    else:
        SavedConversation.objects.create(
            user=request.user,
            conversation=conv
        )

    return redirect('conversation_flashcard', id=conv.id)


# 👤 My Account page
@login_required
def account(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('account')   # refresh хийх
    else:
        form = ProfileForm(instance=profile)

    saved_kanji = SavedKanji.objects.filter(
        user=request.user
    ).select_related('kanji')

    saved_grammar = Grammar.objects.filter(saved_by=request.user)

    grammar_by_level = {
        "N5": [],
        "N4": [],
        "N3": [],
        "N2": [],
    }

    for g in saved_grammar:
        grammar_by_level[g.level].append(g)

    saved_conversations = SavedConversation.objects.filter(
        user=request.user
    ).select_related('conversation')

    return render(request, 'flashcards/account.html', {
        'profile': profile,
        'form': form,
        'saved_kanji': saved_kanji,
        'grammar_by_level': grammar_by_level,
        'saved_conversations': saved_conversations,
    })
    
    
@login_required
def edit_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('account')
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'flashcards/edit_profile.html', {
        'form': form
    })





# 🚪 Logout
def logout_view(request):
    logout(request)
    return redirect('home')

def logout_success(request):
    return render(request, 'registration/logout.html')

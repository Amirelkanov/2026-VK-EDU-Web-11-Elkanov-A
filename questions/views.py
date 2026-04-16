from django.shortcuts import render
from .utils import paginate, MOCK_TAGS


def index(request):
    questions = []
    for i in range(1, 31):
        questions.append(
            {
                "id": i,
                "title": f"Title {i}",
                "text": f"Text {i}",
                "author": f"User{i % 5 + 1}",
                "answers_count": i * 2,
                "tags": MOCK_TAGS[i % 3 : i % 3 + 2],
                "rating": (i * 3) % 20 - 10,
            }
        )

    page, paginator = paginate(questions, request, per_page=10)

    return render(
        request,
        "questions/index.html",
        {
            "questions": page.object_list,
            "page": page,
            "paginator": paginator,
        },
    )


def hot(request):
    questions = []
    for i in range(1, 31):
        questions.append(
            {
                "id": i,
                "title": f"Hottest Question {i}",
                "text": f"Text {i}",
                "author": f"User{i % 5 + 1}",
                "answers_count": i * 5,
                "tags": MOCK_TAGS[i % 2 : i % 2 + 2],
                "rating": 100 - i,
            }
        )

    page, paginator = paginate(questions, request, per_page=10)

    return render(
        request,
        "questions/hot.html",
        {
            "questions": page.object_list,
            "page": page,
            "paginator": paginator,
        },
    )


def tag_questions(request, tag):
    questions = []
    for i in range(1, 31):
        questions.append(
            {
                "id": i,
                "title": f"Question about {tag} #{i}",
                "text": f"Text {i}",
                "author": f"User{i % 5 + 1}",
                "answers_count": i,
                "tags": [tag, MOCK_TAGS[i % len(MOCK_TAGS)]],
                "rating": (i * 7) % 25 - 5,
            }
        )

    page, paginator = paginate(questions, request, per_page=10)

    return render(
        request,
        "questions/tag.html",
        {
            "questions": page.object_list,
            "page": page,
            "paginator": paginator,
            "tag": tag,
        },
    )


def question_detail(request, question_id):

    # Mock question data
    question = {
        "id": question_id,
        "title": f"Question {question_id}",
        "text": f"This is the full text of question {question_id}. " * 10,
        "author": "User1",
        "answers_count": 5,
        "tags": ["python", "django"],
        "rating": 5,
    }

    # Mock answers
    answers = []
    for i in range(1, 8):
        answers.append(
            {
                "id": i,
                "text": f"This is answer {i}. " * 5,
                "author": f"User{i}",
                "rating": i * 10 if i != 3 else 3,
                "is_correct": i == 1,
            }
        )

    page, paginator = paginate(answers, request, per_page=3)

    return render(
        request,
        "questions/question.html",
        {
            "question": question,
            "answers": page.object_list,
            "answers_count": len(answers),
            "page": page,
            "paginator": paginator,
        },
    )


def ask_question(request):
    return render(
        request,
        "questions/ask.html",
        {},
    )

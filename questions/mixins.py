from questions.utils import paginate
from .models import Question, Answer


class QuestionListMixin:
    questions_per_page = 10

    def get_questions_context(self, questions):
        page, paginator = paginate(
            questions, self.request, per_page=self.questions_per_page
        )

        user_votes = Question.objects.get_user_votes(
            page.object_list, self.request.user
        )
        for q in page.object_list:
            q.user_vote = user_votes.get(q.id, 0)

        return {
            "questions": page.object_list,
            "page": page,
            "paginator": paginator,
        }


class AnswersMixin:
    answers_per_page = 3

    def get_answers_page(self, question):
        answers = question.answers.select_related("author").order_by(
            "created_at", "-rating"
        )
        return paginate(answers, self.request, per_page=self.answers_per_page)

    def build_question_context(self, question, page, paginator, form):
        user_question_vote = Question.objects.get_user_votes([question], self.request.user).get(question.id, 0)
        answer_votes = Answer.objects.get_user_votes(
            page.object_list, self.request.user
        )

        question.user_vote = user_question_vote
        for answer in page.object_list:
            answer.user_vote = answer_votes.get(answer.id, 0)

        return {
            "question": question,
            "answers": page.object_list,
            "answers_count": question.answers_count,
            "page": page,
            "paginator": paginator,
            "form": form,
            "is_question_author": (
                self.request.user.is_authenticated
                and question.author_id == self.request.user.id
            ),
        }

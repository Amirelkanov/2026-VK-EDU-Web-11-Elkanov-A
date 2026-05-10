from questions.utils import paginate


class AnswersPaginationMixin:
    answers_per_page = 3

    def get_answers_page(self, question):
        answers = question.answers.select_related("author").order_by(
            "created_at", "-rating"
        )
        return paginate(answers, self.request, per_page=self.answers_per_page)

    def build_question_context(self, question, page, paginator, form):
        return {
            "question": question,
            "answers": page.object_list,
            "answers_count": question.answers_count,
            "page": page,
            "paginator": paginator,
            "form": form,
        }

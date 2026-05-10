from django import forms
from .models import Question, Answer, Tag


class AskForm(forms.ModelForm):
    tags = forms.CharField(
        label="Tags",
        required=True,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "tag1, tag2, tag3"}
        ),
    )

    class Meta:
        model = Question
        fields = ["title", "text"]
        labels = {
            "title": "Title",
            "text": "Details",
        }
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "text": forms.Textarea(attrs={"class": "form-control", "rows": 5}),
        }

    def clean_tags(self):
        tags_str = self.cleaned_data.get("tags", "")
        tag_names = [t.strip() for t in tags_str.split(",") if t.strip()]
        max_length = Tag._meta.get_field("name").max_length
        for tag_name in tag_names:
            if " " in tag_name:
                raise forms.ValidationError("Tags cannot contain spaces")
            if len(tag_name) > max_length:
                raise forms.ValidationError(
                    f"Tag is too long (max {max_length} characters)"
                )
        return tags_str

    def save(self, commit=True, author=None):
        question = super().save(commit=False)
        if author:
            question.author = author
        if commit:
            question.save()
            tags_str = self.cleaned_data.get("tags", "")
            if tags_str:
                tag_names = [t.strip() for t in tags_str.split(",") if t.strip()]
                for tag_name in tag_names:
                    tag, _ = Tag.objects.get_or_create(name=tag_name)
                    question.tags.add(tag)
        return question


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ["text"]
        widgets = {
            "text": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Enter your answer here...",
                }
            ),
        }

    def save(self, commit=True, author=None, question=None):
        answer = super().save(commit=False)
        if author:
            answer.author = author
        if question:
            answer.question = question
        if commit:
            answer.save()
        return answer

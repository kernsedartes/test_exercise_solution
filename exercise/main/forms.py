from django import forms
from .models import Post, Source


class AddQuoteForm(forms.ModelForm):
    new_source = forms.CharField(
        label="Новый источник",
        required=False,
        max_length=128,
        widget=forms.TextInput(
            attrs={"placeholder": "Введите название нового источника"}
        ),
    )
    add_new_source = forms.BooleanField(
        label="Добавить новый источник",
        required=False,
        widget=forms.CheckboxInput(),
    )

    class Meta:
        model = Post
        fields = ["quote", "source", "weight"]
        widgets = {
            "quote": forms.Textarea(
                attrs={"rows": 4, "placeholder": "Введите текст цитаты"}
            ),
            "source": forms.Select(attrs={"class": "form-select"}),
            "weight": forms.NumberInput(attrs={"min": 1, "max": 10}),
        }
        labels = {
            "quote": "Текст цитаты",
            "source": "Источник",
            "weight": "Вес цитаты (1-10)",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["source"].required = False

    def clean(self):
        cleaned_data = super().clean()
        add_new_source = cleaned_data.get("add_new_source")
        new_source = cleaned_data.get("new_source")
        source = cleaned_data.get("source")

        if add_new_source:
            if not new_source:
                raise forms.ValidationError(
                    "Пожалуйста, введите название нового источника."
                )
            if Source.objects.filter(name__iexact=new_source).exists():
                raise forms.ValidationError(
                    "Источник с таким названием уже существует."
                )
            if source:
                raise forms.ValidationError(
                    "Не выбирайте существующий источник, если добавляете новый."
                )
            source = Source.objects.create(name=new_source)
            cleaned_data["source"] = source
        else:
            if not source:
                raise forms.ValidationError(
                    "Выберите существующий источник, если не добавляете новый."
                )

        if source and source.post_set.count() >= 3:
            raise forms.ValidationError(
                f"У источника '{source.name}' уже максимальное количество цитат (3)."
            )

        return cleaned_data

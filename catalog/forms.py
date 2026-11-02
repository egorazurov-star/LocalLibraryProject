import datetime

from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _

from .models import BookInstance


class RenewBookForm(forms.Form):
    """Обычная форма продления книги библиотекарем."""
    renewal_date = forms.DateField(
        help_text="Enter a date between now and 4 weeks (default 3).",
        widget=forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
    )

    def clean_renewal_date(self):
        data = self.cleaned_data['renewal_date']

        # Дата не должна быть в прошлом
        if data < datetime.date.today():
            raise ValidationError(_('Invalid date - renewal in past'))

        # Дата не должна быть дальше, чем через 4 недели
        if data > datetime.date.today() + datetime.timedelta(weeks=4):
            raise ValidationError(_('Invalid date - renewal more than 4 weeks ahead'))

        # Всегда возвращаем очищенные данные
        return data


class RenewBookModelForm(ModelForm):
    """Тот же функционал, но на основе ModelForm (используется для демонстрации)."""

    def clean_due_back(self):
        data = self.cleaned_data['due_back']

        if data < datetime.date.today():
            raise ValidationError(_('Invalid date - renewal in past'))

        if data > datetime.date.today() + datetime.timedelta(weeks=4):
            raise ValidationError(_('Invalid date - renewal more than 4 weeks ahead'))

        return data

    class Meta:
        model = BookInstance
        fields = ['due_back']
        labels = {'due_back': _('Renewal date')}
        help_texts = {'due_back': _('Enter a date between now and 4 weeks (default 3).')}

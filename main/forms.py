# -*- encoding: utf-8 -*-
from django import forms

from main.models import Keyword

class NameForm(forms.Form):
    query = forms.CharField(label='Nombre')

class SlotTypeForm(forms.Form):
    query = forms.CharField(label='Slot o tipo')

class LvlForm(forms.Form):
    low_limit = forms.IntegerField(label='Nivel mínimo')
    upper_limit = forms.IntegerField(label='Nivel máximo')
    
class KeywordForm(forms.Form):
    keywords = set((kwd.keyword,kwd.keyword) for kwd in Keyword.objects.all())
    keyword = forms.ChoiceField(choices = keywords,label='Palabra clave')

class RegisterForm(forms.Form):
    username = forms.CharField(label='Usuario',widget=forms.TextInput,required=True)
    password = forms.CharField(label='Contraseña',widget=forms.PasswordInput,required=True)
    confirm = forms.CharField(label='Confirmar contraseña',widget=forms.PasswordInput,required=True)
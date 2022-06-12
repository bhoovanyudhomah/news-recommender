from django import forms

class CreateNewNews(forms.Form):
	category = forms.CharField(label="type category", max_length=200)
	content = forms.CharField(label="type content", max_length=200)
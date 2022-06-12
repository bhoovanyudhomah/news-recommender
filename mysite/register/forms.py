from django import forms
from django.db import models
from django.contrib.auth.forms import UserCreationForm  
from django.core.exceptions import ValidationError  
from django.forms.fields import EmailField  
from django.forms.forms import Form
from .models import User
from django.contrib.auth.hashers import check_password
from django.contrib.auth.hashers import make_password

class RegisterForm(forms.Form):
	username = forms.CharField(label='username', min_length=5, max_length=150) 
	email = forms.EmailField(label='email')
	password1 = forms.CharField(label='password', widget=forms.PasswordInput, max_length=100)
	password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput, max_length=100) 

	class Meta:
		model = User

		fields = ["username","email","password1","password2"]

	def clean(self):
		
		# data from the form is fetched using super function
		super(RegisterForm, self).clean()
		
		# extract the username from the data
		username = self.cleaned_data.get('username').lower()
		new = User.objects.filter(username = username)  
		if new.count(): 
			self._errors['username'] = self.error_class(['Username already exists'])

		#valitdate password
		password1 = self.cleaned_data.get('password1')
		password2 = self.cleaned_data.get('password2')
		if password1 != password2:
			self._errors['password2'] = self.error_class(['Passwords do not match '])

		#validate email
		email = self.cleaned_data.get('email')
		new = User.objects.filter(username = username)  
		if new.count(): 
			self._errors['email'] = self.error_class(['Email already exists'])

		# return any errors if found
		return self.cleaned_data

class LoginForm(forms.Form):
	username = forms.CharField(label='username', min_length=5, max_length=150)
	password = forms.CharField(label='password', widget=forms.PasswordInput, max_length=100)

	class Meta:
		fields = ["username","password"]

	def clean(self):
		
		# data from the form is fetched using super function
		super(LoginForm, self).clean()
		
		# extract the username from the form and check if it is present in database
		username = self.cleaned_data.get('username').lower()
		new = User.objects.filter(username = username)  
		if not new.count(): 
			self._errors['username'] = self.error_class(['Username does not exist'])
			return self.cleaned_data

		#valitdate password
		password = self.cleaned_data.get('password')
		hashedPassword = new[0].password
		# get salt of hashed password
		algo, iterations, salt, hashpw = hashedPassword.split('$')
		# hash input password with same hash
		if make_password(password, salt=salt) != hashedPassword:
			self._errors['password'] = self.error_class(['Wrong password'])
			return self.cleaned_data

		# return any errors if found
		return self.cleaned_data
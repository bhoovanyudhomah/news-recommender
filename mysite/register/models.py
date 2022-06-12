from django.db import models
from django.contrib.auth.models import User
from main.models import Category
# Create your models here.

class User(models.Model):
	username = models.CharField(max_length=150) 
	email = models.EmailField()
	password = models.CharField(max_length=100)

	def _str_(self):
		return self.name

class Preferences(models.Model):
	account_id = models.ForeignKey(User, on_delete=models.CASCADE)
	category_id = models.ForeignKey(Category, on_delete=models.CASCADE)
	operational = models.BooleanField()
	sources = models.TextField(null=True)
	keywords = models.TextField(null=True)

	def _str_(self):
		return self.name
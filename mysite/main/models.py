from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Category(models.Model):
	category = models.CharField(max_length=200)
	keywords = models.TextField()
	path = models.CharField(max_length=200)
	
	def _str_(self):
		return self.name 

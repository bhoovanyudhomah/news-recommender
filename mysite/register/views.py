from django.shortcuts import render, redirect
from .forms import RegisterForm, LoginForm
from .models import User, Preferences
from main.models import Category
from django.contrib.auth.hashers import make_password
from .import views

# Create your views here.
def register(response):
	if response.method == "POST":
		form = RegisterForm(response.POST)
		if form.is_valid():
			username=form.cleaned_data['username'] 
			email=form.cleaned_data['email']
			password= make_password(form.cleaned_data['password1'])

			t=User(username=username , email=email , password=password )
			# , sports=sports , politics=politics , education=education ,
			#  business=business , electronics=electronics)
			t.save()

			# upload preferences data into database
			# sort id and caterories according to category name to enter correct data
			# account_id = User.objects.filter(username=username)
			# category_id_set = Category.objects.values_list('id', flat=True).order_by('category')
			
			# operational= {
			# 	'sports':sports, 
			# 	'politics':politics, 
			# 	'education':education, 
			# 	'business':business, 
			# 	'electronics':electronics}
			# sorted_cats = sorted(operational.items(),  key=lambda x: x[0])
			# i=0
			# for category_id in category_id_set:
			# 	u=Preferences(account_id=account_id[0].id, category_id=category_id, operational=sorted_cats[i][1])
			# 	u.save()
			# 	i=i+1

			return redirect("/home/")
		else:
			return render(response, "register/register.html", {"form":form})
	else:

	    # If the request is a GET request then,
	    # create an empty form object and
	    # render it into the page
	    form = RegisterForm(None)  
	    return render(response, 'register/register.html', {'form':form})

def login(response):
	if response.method == "POST":
		form = LoginForm(response.POST)
		if form.is_valid():
			username=form.cleaned_data['username'] 
			password=form.cleaned_data['password']
			# create session for username
			response.session['username'] = username
			return render(response, "home/index.html")
		else:
			return render(response, 'registration/login.html', {'form':form})
	# if method is get
	else:
	    # If the request is a GET request then,
	    # create an empty form object and
	    # render it into the page
	    form = LoginForm(None)  
	    return render(response, 'registration/login.html', {'form':form})


def logout(response):
   try:
      del response.session['username']
   except:
      pass
   return redirect("home/")
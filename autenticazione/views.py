from django.shortcuts import render, redirect
from .forms import RegisterForm

def register(response):
    if response.user.is_authenticated: 
        return redirect("homepage")
    else:
        if response.method == "POST":
            form = RegisterForm(response.POST)
            if form.is_valid():
                form.save()
            return redirect("/login")
        else:
            form = RegisterForm()
            return render(response, "registration/register.html", {"form": form})
            


# Create your views here.

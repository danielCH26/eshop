from django.shortcuts import render, redirect
from .forms import RegistrationForm
from .models import  Account
from django.contrib import  messages, auth
from django.contrib.auth.decorators import login_required


# Create your views here.
def register(request):

    form = RegistrationForm()
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split("@")[0]
            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, username = username, password=password)
            user.phone_number = phone_number
            user.is_active=True
            user.save()
            messages.success(request, 'User registered succesfully')
            return redirect('register')

    ctx = {
        'form' : form
    }
    return render(request, 'accounts/register.html', ctx)

def login(request):

    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(email=email, password=password)
        print("post")
        print('email :', email)
        print('password :', password)
        print('user :', user)

        if user is not None:
            auth.login(request, user)
            print("Credenciales correctas")
            return redirect('home')
        else:
            messages.error(request, "The credentials doesn't match ")
            print("Credenciales incorrectas")
            return redirect('login')

    return render(request, 'accounts/login.html')
@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'Session closed ')
    return redirect('login')


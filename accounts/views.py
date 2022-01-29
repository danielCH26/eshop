from .forms import RegistrationForm
from .models import  Account
from django.contrib import  messages, auth
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import render, redirect
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import EmailMessage

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
            #user.is_active=True
            user.save()

            current_site = get_current_site(request)
            mail_subject = 'Please activate your account'
            body = render_to_string('accounts/account_verification_email.html', {
                'user' : user,
                'domain' : current_site,
                'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
                'token' : default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, body, to=[to_email])
            send_email.send()

            #messages.success(request, 'User registered succesfully')

            return redirect('/accounts/login/?command=verification&email='+email)

    ctx = {
        'form' : form
    }
    return render(request, 'accounts/register.html', ctx)

def login(request):

    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(email=email, password=password)

        if user is not None:
            auth.login(request, user)
            messages.success(request, "You have succesfully started session")
            return redirect('dashboard')
        else:
            messages.error(request, "The credentials doesn't match ")
            return redirect('login')

    return render(request, 'accounts/login.html')
@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'Session closed ')
    return redirect('login')


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk = uid)

    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations, your account is active!')
        return redirect('dashboard')

    else:
        messages.error(request, 'Activation failed!')
        return redirect('register')

@login_required(login_url='login')
def dashboard(request):
    return render(request, 'accounts/dashboard.html')

def forgotPassword(request):
    print('ForgotPassword')
    if request.method == 'POST':
        print('POST')
        email = request.POST['email']
        print(email)
        if Account.objects.filter(email=email).exists():
            user= Account.objects.get(email__exact=email)
            current_site = get_current_site(request)
            mail_subject = 'Recover Password'
            body = render_to_string('accounts/reset_password.html', {
                'user' : user,
                'domain' : current_site,
                'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
                'token' : default_token_generator.make_token(user),
            })

            to_email = email
            send_email= EmailMessage(mail_subject, body, to=[to_email])
            send_email.send()

            messages.success(request, 'We send you an email to reset your password')

            return redirect('login')
        else:
            print('Va por get')
            messages.error(request, "The user's account does not exist")
            return redirect('forgotPassword')

    return render(request,'accounts/forgotPassword.html')

def reset_password_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user=None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request,'Please reset your password')
        return redirect('resetPassword')

    else:
        messages.error(request, 'The link has expired')
        return redirect('login')

def resetPassword(request):
    if request.method== 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password succesfully changed')
            return redirect('login')
        else:
            messages.error(request, 'Failed password change')
            return redirect('resetPassword')

    else:
        return render(request,'accounts/resetPassword.html')


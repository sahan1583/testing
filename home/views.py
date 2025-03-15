from django.shortcuts import render, HttpResponse, redirect, HttpResponseRedirect
from django.contrib.auth.models import User, Group
from . import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test

# Create your views here.
def index(request):
    return render(request, 'index.html')

def home(request):
    return render(request, 'home.html')

def adminClick(request):
    return render(request, 'admin_click.html')

def memberClick(request):
    return render(request, 'member_click.html')

def memberSignup(request):
    if request.method == 'POST':
        form = forms.MemberUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.set_password(user.password)
            user.save()
            member_group = Group.objects.get_or_create(name='MEMBER')
            member_group[0].user_set.add(user)
            username = form.cleaned_data['username']
            messages.success(request, f'Account created successfully for {username}!')
            return HttpResponseRedirect('/memberlogin')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = forms.MemberUserForm()
    return render(request, 'member_signup.html', {"form": form})

def is_member(user):
    return user.groups.filter(name='MEMBER').exists()

def is_admin(user):
    return user.groups.filter(name='ADMIN').exists()

def afterlogin(request):
    if is_admin(request.user):
        return redirect('adminhome')
    elif is_member(request.user):
        return redirect('memberhome')
    else:
        return redirect('home')
    

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def adminHome(request):
    return render(request, 'admin_home.html')


@login_required(login_url='memberlogin')
@user_passes_test(is_member)
def memberHome(request):
    return render(request, 'member_home.html')


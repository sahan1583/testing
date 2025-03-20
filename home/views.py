from django.shortcuts import render, HttpResponse, redirect, HttpResponseRedirect, get_object_or_404
from django.contrib.auth.models import User, Group
from . import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Case

# Create your views here.
def not_logged_in(user):
    return not user.is_authenticated

@user_passes_test(not_logged_in, login_url='/afterlogin')
def index(request):
    return render(request, 'index.html')

@user_passes_test(not_logged_in, login_url='/afterlogin')
def home(request):
    return render(request, 'home.html')

@user_passes_test(not_logged_in, login_url='/afterlogin')
def adminClick(request):
    return render(request, 'admin_click.html')

@user_passes_test(not_logged_in, login_url='/afterlogin')
def memberClick(request):
    return render(request, 'member_click.html')

@user_passes_test(not_logged_in, login_url='/afterlogin')
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
    return caseList(request)


@login_required(login_url='memberlogin')
@user_passes_test(is_member)
def memberHome(request):
    return caseList(request)

@login_required(login_url='home')
def caseDetails(request, case_id):
    if is_admin(request.user):
        base_template = 'admin_base.html'
    else:
        base_template = 'member_base.html'

    admin = "False"
    if is_admin(request.user):
        admin = "True"

    case = get_object_or_404(Case, id=case_id)
    if request.method == "POST":
        if "delete" in request.POST:
            # delete the case
            # case.delete() 
            messages.success(request, f'Case successfully deleted!')
            return redirect('caselist')

        elif "status" in request.POST:
            new_status = request.POST.get("status")  # Get the selected status from form
            if new_status in ["open", "completed"]:  # Validate the status
                case.status = new_status
                case.save()  # Save changes to the database

        return redirect("case_details", case_id=case.id)  # Redirect to the same page
    
    return render(request, 'case_details.html', {'case': case, 'admin': admin, 'base_template': base_template})

@login_required(login_url='home')
def caseList(request):
    if is_admin(request.user):
        base_template = 'admin_base.html'
    else:
        base_template = 'member_base.html'
    cases = Case.objects.filter(approved=True)
    return render(request, 'case_list.html', {'cases': cases, 'base_template': base_template})

@user_passes_test(not_logged_in, login_url='/afterlogin')
def visitorHome(request):
    if request.method == 'POST':
        form = forms.CaseForm(request.POST, request.FILES)  # Handles form data and uploaded files
        if form.is_valid():
            case = form.save(commit=False)
            case.status = "open"  # Default status for new cases
            case.save()
            messages.success(request, f'New case successfully registered!')
            return redirect('visitor_home')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = forms.CaseForm()

    return render(request, 'visitor_home.html', {'form': form})

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def adminApproval(request):
    cases = Case.objects.filter(approved=False)
    return render(request, 'case_list.html', {'cases': cases, 'base_template': 'admin_base.html', 'approval': 'True'})

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def approvalCaseDetails(request, case_id):
    case = get_object_or_404(Case, id=case_id)
    if request.method == "POST":
        if "action" in request.POST:
            action = request.POST.get("action")
            if action == "approve":
                case.approved = True
                case.save()
                messages.success(request, f'Case successfully approved!')
            elif action == "reject":
                case.delete()
                messages.success(request, f'Case successfully rejected!')
        return redirect('adminapproval')
    return render(request, 'approval_case_details.html', {'case': case, 'admin': 'True', 'base_template': 'admin_base.html'})
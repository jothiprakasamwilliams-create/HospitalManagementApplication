from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.csrf import requires_csrf_token

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login, logout

from django.contrib import messages

from django.contrib.auth.decorators import login_required
from .decorators import *

from .models import *
from .forms import *
from .filters import *

########################################################################
#################### DASHBOARD  #####################################
@requires_csrf_token
def start(request):
    return render(request, 'accounts/medbook_html/index.html')

@requires_csrf_token
@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin', 'Nurse', 'Doctor', 'Receptionist'])
def home(request):

    patients = Patient.objects.all()
    count_patients = Patient.objects.all().count()
    d_staff = Staff.objects.filter(position = "DOCTOR")
    count_d_staff = Staff.objects.filter(position = "DOCTOR").count()
    n_staff = Staff.objects.filter(position = "NURSE")
    count_n_staff = Staff.objects.filter(position = "NURSE").count()
    r_staff = Staff.objects.filter(position = "RECEPTIONIST")
    
    patient_fil = PatientFilter(request.GET, queryset=patients)
    patients = patient_fil.qs
    
    
    context = {'patients':patients, 
    'd_staff':d_staff,
    'n_staff':n_staff,
    'r_staff':r_staff,
    'count_patients':count_patients,
    'count_d_staff':count_d_staff,
    'count_n_staff':count_n_staff,
    'patient_fil':patient_fil

    }

    return render(request, 'accounts/dashboard.html', context)



########################################################################
#################### PATIENT PROFILE #####################################
@requires_csrf_token
@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin', 'Nurse', 'Doctor', 'Receptionist'])
def patient(request, pk):

    patient = Patient.objects.get(id=pk)

    try:
        allergy_entry = PatientHasAllergy.objects.get(pid=patient)
    except PatientHasAllergy.DoesNotExist:
        allergy_entry = None
    # allergy_entry = PatientHasAllergy.objects.get(patient=patient)

    try:
        patient_allergies = PatientHasAllergy.objects.filter(pid=patient)
        allergies = []
        for patient_allergy in patient_allergies:
            allergies.extend(patient_allergy.allergy.all())
    except PatientHasAllergy.DoesNotExist:
        allergies = []
    
    try:
        next_appointment = NextAppointment.objects.filter(patient=patient).last()
    except NextAppointment.DoesNotExist:
        next_appointment = None

    diag = PatientHasDiagnosis.objects.filter(patient_id=patient)
    myFilter = DiagFilter(request.GET, queryset=diag)
    diag = myFilter.qs

    check_up = Condition_Check_UP.objects.filter(patient=patient)

    context = {'patient':patient, 'allergies_of_patient': allergies, 'next_appointment':next_appointment, 'diag':diag, 'check_up':check_up, 'allergy_entry':allergy_entry, 'myFilter':myFilter} 
    return render(request, 'accounts/patient.html', context)
    # return HttpResponse(diag.diagnosis)

################################################################################
####### PATIENT = CREATE, UPDATE #########################################
@requires_csrf_token
@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin', 'Receptionist'])
def create_patient(request):

    if request.method == 'POST':
        form = NewPatientForm(request.POST)
        if form.is_valid():
            patient = form.save()
            return redirect('patient', patient.id)
    else:
        form = NewPatientForm()
    
    context = {'form':form}
    return render(request, 'accounts/patient_form.html', context)

@requires_csrf_token
@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin', 'Receptionist'])
def update_patient(request, pk):

    patient = Patient.objects.get(id=pk)

    if request.method == 'POST':
        form = NewPatientForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            return redirect('patient', pk)
    else:
        form = NewPatientForm(instance=patient)

    context = {'form':form}
    return render(request, 'accounts/patient_form.html', context)


################################################################################
####### DIGNOSIS = CREATE, UPDATE #########################################
@requires_csrf_token
@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin', 'Doctor'])
def create_diagnosis(request, pk):

    # Check if user has a staff profile
    try:
        user_a = request.user
        s_id = user_a.staffUsername
        initial_data = {'doctor': s_id, 'patient_id': pk}
    except:
        # User doesn't have a staff profile, only set patient_id
        initial_data = {'patient_id': pk}

    if request.method == 'POST':
        form = DiagnosisForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('patient', pk)
    else:
        form = DiagnosisForm(initial=initial_data)
    
    context = {'form':form}
    return render(request, 'accounts/diagnosis_form.html', context)

@requires_csrf_token
@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin', 'Doctor'])
def update_diagnosis(request, pk):
    entry = PatientHasDiagnosis.objects.get(id=pk)
    
    if request.method == 'POST':
        form = DiagnosisForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            return redirect('patient', entry.patient_id.id)
    else:
        form = DiagnosisForm(instance=entry)
    
    context = {'form':form}
    return render(request, 'accounts/diagnosis_form.html', context)


################################################################################
####### CHECK UP = CREATE, UPDATE #########################################
@requires_csrf_token
@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin', 'Nurse'])
def create_checkup(request, pk):

    # Check if user has a staff profile
    try:
        user_a = request.user
        s_id = user_a.staffUsername
        initial_data = {'nurse': s_id, 'patient': pk}
    except:
        # User doesn't have a staff profile, only set patient
        initial_data = {'patient': pk}

    if request.method == 'POST':
        form = CheckUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('patient', pk)
    else:
        form = CheckUpForm(initial=initial_data)
        
    context = {'form':form}
    return render(request, 'accounts/check_up_form.html', context)

@requires_csrf_token
@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin', 'Nurse'])
def update_checkup(request, pk):
    entry = Condition_Check_UP.objects.get(id=pk)
    
    if request.method == 'POST':
        form = CheckUpForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            return redirect('patient', entry.patient.id)
    else:
        form = CheckUpForm(instance=entry)
    
    context = {'form':form}
    return render(request, 'accounts/check_up_form.html', context)


####################################################################################3
########################### NEW APPOINTMENT ################################
@requires_csrf_token
@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin', 'Doctor', 'Receptionist'])
def create_appointment(request):

    user_a = request.user
    initial_data = {}

    # Check if user has a staff profile
    try:
        s_id = user_a.staffUsername
        if s_id.position == 'RECEPTIONIST':
            initial_data = {'receptionits': s_id}
        elif s_id.position == 'DOCTOR':
            initial_data = {'staff': s_id}
    except:
        # User doesn't have a staff profile, leave initial_data empty
        pass

    if request.method == 'POST':
        form = NewAppointment(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = NewAppointment(initial=initial_data)
        
    context = {'form':form}
    return render(request, 'accounts/new_appointment.html', context)

####################################################################################3
########################### ALLGRGENS ################################
@requires_csrf_token
@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin', 'Nurse', 'Doctor'])
def create_allergy(request, p_id):

    patient_id = Patient.objects.get(id=p_id)
    initial_data = {'pid': patient_id}
    
    if request.method == 'POST':
        form = AllergensForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('patient', p_id)
    else:
        form = AllergensForm(initial=initial_data)
        
    context = {'form':form}
    return render(request, 'accounts/create_allergy.html', context)

@requires_csrf_token
@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin', 'Nurse', 'Doctor'])
def update_allergy(request, pk, p_id):
    
    allergy_entry = PatientHasAllergy.objects.get(id=pk)
    
    if request.method == 'POST':
        form = AllergensForm(request.POST, instance=allergy_entry)
        if form.is_valid():
            form.save()
            return redirect('patient', p_id)
    else:
        form = AllergensForm(instance=allergy_entry)
        
    context = {'form':form}
    return render(request, 'accounts/create_allergy.html', context)


####################################################################################3
########################### REGISTER ################################

@unathenticated_user
def registerPage(request):
    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            group = Group.objects.get(name='Patient')
            user.groups.add(group)

            username = form.cleaned_data.get('username')
            messages.success(request, 'Account was created for ' + username)
            return redirect('login')

    context = {'form':form}
    return render(request, 'accounts/register.html', context)


#######################################################################
########################### LOGIN ################################
@requires_csrf_token
@unathenticated_user
def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            print(user.groups.all())
            if 'Patient' in str(user.groups.all()):
                return redirect('user-page')
            return redirect('home')

        else:
            messages.info(request, 'Username OR password is incorrect!')

    context = {}
    return render(request, 'accounts/login.html', context)


#######################################################################
########################### LOGOUT ################################
@requires_csrf_token
@login_required(login_url='login')
def logoutUser(request):
    logout(request)
    return redirect('login')


#######################################################################
########################### USERPAGE ################################
@requires_csrf_token
@login_required(login_url='login')
@allowed_users(allowed_roles=['Patient'])
def userPage(request):

    try:
        patient = request.user.patient
    except:
        return render(request, 'accounts/no_account.html')
    
    diag = patient.patient.all()
    check_up = patient.checkuppid.all()
    next_app = patient.patient_next_app.all()

    context = {'patient':patient, 'diag':diag, 'check_up':check_up, 'next_app':next_app}
    return render(request, 'accounts/user.html', context)


#######################################################################
########################### _________ ################################

from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.core.files.storage import FileSystemStorage
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from django.db import transaction
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.http import FileResponse, Http404
from datetime import datetime
import os
import io
import zipfile
import pandas as pd
from PIL import Image
from io import BytesIO
from django.core.files import File
from django.core.validators import validate_integer
from django.core.paginator import Paginator

from django.contrib.auth import get_user_model
from .models import MyCustomUser, Profile, ReunionRegistration
from .forms import ProfileForm, UserForm
from .decorators import user_is_alumni, user_is_admin, user_is_superuser
from django.contrib.auth.decorators import login_required


# Create your views here.
def index(request):
    context= {}
    
    return render(request, "index.html", context)

def signin_view(request):
    context= {}
    show_login_modal = False
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            if user.is_alumni:
                return redirect('app:alumni_profile', pk=user.pk)
            elif user.is_admin:
                return redirect('app:admin_dashboard') 
            elif user.is_superuser:
                return redirect('/admin/') 
        else:
            context['error'] = 'Invalid email or password'
            show_login_modal = True
    context['show_login_modal'] = show_login_modal
    return HttpResponseRedirect('/')



def alumni_signup(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        name = request.POST['name']
        roll = int(request.POST['roll'])
        series = request.POST['series']
        phone_number = request.POST['phone_number']
        whatsapp_no = request.POST.get('whatsapp_no', None)  # Optional
        current_position = request.POST['current_position']
        current_organization = request.POST['current_organization']
        previous_experience = request.POST.get('previous_experience', None)  # Optional
        skills = request.POST.get('skills', None)  # Optional
        present_address = request.POST['present_address']
        home_district = request.POST['home_district']
        blood_group = request.POST['blood_group']
        marital_status = request.POST.get('marital_status', None)  # Optional
        linkedin = request.POST.get('linkedin', None)  # Optional
        facebook = request.POST.get('facebook', None)  # Optional
        name_of_degree1 = request.POST['name_of_degree1']  # Optional
        institution1 = request.POST['institution1']  # Optional
        name_of_degree2 = request.POST['name_of_degree2']  # Optional
        institution2 = request.POST['institution2']  # Optional
        name_of_degree3 = request.POST['name_of_degree3']  # Optional
        institution3 = request.POST['institution3']  # Optional
        
        # Validate inputs, this is a simplistic example, you could do more comprehensive checks
        if MyCustomUser.objects.filter(email=email).exists():
            return render(request, 'alumni_signup.html', {'error_message': 'Email already exists'})
        
        with transaction.atomic():
            user = MyCustomUser.objects.create_user(email=email, password=password, name=name, is_alumni=True)
            profile = Profile.objects.create(
                user=user, roll=roll, series=series, phone_number=phone_number, whatsapp_no=whatsapp_no,
                current_position=current_position, current_organization=current_organization, previous_experience=previous_experience, 
                skills=skills, present_address=present_address, home_district=home_district, blood_group=blood_group,
                marital_status=marital_status, linkedin=linkedin, facebook=facebook,
                name_of_degree1=name_of_degree1, institution1=institution1,
                name_of_degree2=name_of_degree2, institution2=institution2,
                name_of_degree3=name_of_degree3, institution3=institution3,
            )
            
            if 'profile_picture' in request.FILES:
                profile_picture = request.FILES['profile_picture']
                fs = FileSystemStorage()

                img = Image.open(profile_picture)
                img_format = img.format

                if img.size[0] > 2000 or img.size[1] > 2000:
                    img.thumbnail((2000, 2000), Image.BICUBIC)

                img_io = BytesIO()
                img.save(img_io, format=img_format, quality=80)  # You can experiment with quality to meet your requirements
                img_content = File(img_io, name=profile_picture.name)

                # Save compressed image
                filename = fs.save(profile_picture.name, img_content)
                profile.profile_picture = filename
                profile.save()

            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('app:index')
    else:
        return render(request, 'alumni_signup.html', {
            'SERIES_CHOICES': Profile.SERIES_CHOICES,
            'BLOOD_GROUP_CHOICES': Profile.BLOOD_GROUP_CHOICES,
            'MARITAL_STATUS_CHOICES': Profile.MARITAL_STATUS_CHOICES
        })



def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')


@login_required
def alumni_profile(request, pk):
    alumni = MyCustomUser.objects.get(pk=pk)
    profile = alumni.profile

    if request.method == 'POST':
        profile_picture = request.FILES.get('profile_picture')
        profile.profile_picture = profile_picture
        profile.save()

        img_path = os.path.join(settings.MEDIA_ROOT, str(profile.profile_picture))
        img = Image.open(img_path)
        img.thumbnail((1000, 1000))

        file_path = os.path.join(settings.MEDIA_ROOT, 'profile_pics', profile_picture.name)
        
        # Loop to compress the image
        quality = 90
        while quality >= 10:
            img.save(file_path, quality=quality, optimize=True)
            filesize = os.path.getsize(file_path)
            if filesize < 500 * 1024:
                break 
            quality -= 10  

        profile.profile_picture.name = 'profile_pics/' + profile_picture.name
        profile.save()

    return render(request, 'alumni_profile.html', {'alumni': alumni, 'profile': profile})



@user_is_alumni
def edit_profile(request):
    user_pk = request.user.pk
    user = MyCustomUser.objects.get(pk=user_pk)
    profile, created = Profile.objects.get_or_create(user=user)

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user.name = request.POST['full_name']
            user.save()
            user_form.save()
            profile_form.save()
            return redirect('app:alumni_profile', pk=user_pk)
        else:
            print(f"User form errors: {user_form.errors}")
            print(f"Profile form errors: {profile_form.errors}")

        
    else:
        user_form = UserForm(instance=user)
        profile_form = ProfileForm(instance=profile)

    return render(request, 'edit_profile.html', {'user_form': user_form, 'profile_form': profile_form})


def admin_signup(request):
    context = {}
    error_message = ''
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        name = request.POST.get('name')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password == confirm_password:
            try:
                with transaction.atomic():
                    User = get_user_model()
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        name=name,
                        password=password
                    )
                    return redirect('app:index')  
            except Exception as e:
                error_message = str(e)
        else:
            error_message = 'Passwords do not match'
        
    context['error_message'] = error_message
    return render(request, 'admin_signup.html', context)



        
def all_alumni(request):
    years = [str(year) for year in range(2005, 2017)]
    series_filter = request.GET.get('series', '')  # Get the 'series' parameter from the request
    if series_filter:
        profiles = Profile.objects.filter(series=series_filter)  # Filter by series if provided
    else:
        profiles = Profile.objects.all()  # Otherwise, display all
    
    paginator = Paginator(profiles, 12)  # Show 12 profiles per page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'all_alumni.html', {'years': years, 'page_obj': page_obj, 'series_filter': series_filter})




@user_is_admin
def admin_dashboard(request):
    search_query = request.GET.get('search', '')
    if search_query:
        reunion_registrations = ReunionRegistration.objects.filter(
            Q(name__icontains=search_query) | 
            Q(roll_number__icontains=search_query)
        )
    else:
        reunion_registrations = ReunionRegistration.objects.all()

    paginator = Paginator(reunion_registrations, 10) # Show 10 entries per page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'admin_dashboard.html', context)


@user_is_admin
def export_excel(request):
    queryset = ReunionRegistration.objects.all()
    df = pd.DataFrame.from_records(queryset.values(
        'name', 'roll_number', 'email', 'number_of_guests', 'driver', 'total_amount_paid', 'is_payment_varified', 'upload_payment_slip'
    ))
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    output.seek(0)
    
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    zip_filename = f"ReunionRegistrations_{current_time}.zip"

    s = io.BytesIO()
    with zipfile.ZipFile(s, 'w') as zipf:
        zipf.writestr('ReunionRegistrations.xlsx', output.getvalue())
        
        image_folder_path = 'Media/payment_slips/'
        for obj in ReunionRegistration.objects.all():
            image_path = os.path.join(image_folder_path, os.path.basename(obj.upload_payment_slip.name))
            if os.path.exists(image_path):
                with open(image_path, 'rb') as f:
                    zipf.writestr(f'payment_slips/{os.path.basename(image_path)}', f.read())

    response = HttpResponse(s.getvalue(), content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename={zip_filename}'
    
    return response







def about(request):
    return render(request, 'about.html')


def first_reunion(request):
    context = {}
    return render(request, 'first_reunion.html', context)



def first_reunion_registration(request):
    context = {}
    error_message = ''
    registration_successful = False
    
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        roll_number = request.POST.get('roll_number')
        number_of_guests = request.POST.get('number_of_guests')
        driver = request.POST.get('driver')
        total_amount_paid = request.POST.get('total_amount_paid')
        upload_payment_slip = request.FILES.get('upload_payment_slip')

        try:       
            with transaction.atomic():
                validate_integer(roll_number)
                validate_integer(number_of_guests)
                validate_integer(driver)
                validate_integer(total_amount_paid)
                
                new_registration = ReunionRegistration(
                    name=name,
                    email=email,
                    roll_number=int(roll_number),
                    number_of_guests=int(number_of_guests),
                    driver=int(driver),
                    total_amount_paid=int(total_amount_paid),
                    upload_payment_slip=upload_payment_slip
                )
                new_registration.save()
                registration_successful = True  # set flag to true if saved successfully
        except Exception as e:
            error_message = str(e)

    context['error_message'] = error_message
    context['registration_successful'] = registration_successful
    return render(request, 'first_reunion_registration.html', context)

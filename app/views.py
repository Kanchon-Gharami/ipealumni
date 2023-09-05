from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.core.files.storage import FileSystemStorage
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from django.db import transaction
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.http import FileResponse, Http404
from datetime import datetime
import os
import io
import zipfile
import csv
from zipfile import ZipFile
import pandas as pd
from PIL import Image
from io import BytesIO
from django.core.files import File
from django.core.validators import validate_integer
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.timezone import make_naive
from django.core.exceptions import ValidationError

from django.contrib.auth import get_user_model
from .models import MyCustomUser, Profile, ReunionRegistration, Notice, Achievement, Carousel, GalleryImage
from .forms import ProfileForm, UserForm, ConfirmPaymentForm
from .decorators import user_is_alumni, user_is_admin, user_is_superuser
from django.contrib.auth.decorators import login_required


# Create your views here.
def index(request):
    latest_notices = Notice.objects.all().order_by('-datetime_field')[:5]
    latest_achievements = Achievement.objects.all().order_by('-datetime_field')[:3]
    latest_carousels = Carousel.objects.all().order_by('-datetime_field')[:3]
    
    image_list = GalleryImage.objects.filter(tag='home_gallery').order_by('-id')
    paginator = Paginator(image_list, 6)  # Show 6 images per page
    
    page = request.GET.get('page')
    try:
        images = paginator.page(page)
    except PageNotAnInteger:
        images = paginator.page(1)
    except EmptyPage:
        images = paginator.page(paginator.num_pages)


    faculty_count = Profile.objects.filter(series='faculty_member').count()
    alumni_count = Profile.objects.all().count()
    ReunionRegistration_count = ReunionRegistration.objects.all().count()
    achievement_count = Achievement.objects.all().count()

    context = {
        'latest_notices': latest_notices,
        'latest_achievements': latest_achievements,
        'latest_carousels': latest_carousels,
        'faculty_count': faculty_count,
        'alumni_count': alumni_count,
        'ReunionRegistration': ReunionRegistration_count,
        'achievement_count': achievement_count,
    }
    context['images'] = images
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
        try:
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
        except ValidationError as e:
            error_message = e.message
            return render(request, 'alumni_signup.html', {
                'SERIES_CHOICES': Profile.SERIES_CHOICES,
                'BLOOD_GROUP_CHOICES': Profile.BLOOD_GROUP_CHOICES,
                'MARITAL_STATUS_CHOICES': Profile.MARITAL_STATUS_CHOICES,
                'error_message': error_message
            })
        except Exception as e:
            error_message = str(e)
            return render(request, 'alumni_signup.html', {
                'SERIES_CHOICES': Profile.SERIES_CHOICES,
                'BLOOD_GROUP_CHOICES': Profile.BLOOD_GROUP_CHOICES,
                'MARITAL_STATUS_CHOICES': Profile.MARITAL_STATUS_CHOICES,
                'error_message': error_message
            })
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
        profiles = Profile.objects.filter(series=series_filter).order_by('roll') 
    else:
        profiles = Profile.objects.all().order_by('roll')   # Otherwise, display all
    
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

    if request.method == 'POST':
        id_to_delete = request.POST.get('id_to_delete')
        if id_to_delete:
            try:
                obj = ReunionRegistration.objects.get(id=id_to_delete)
                obj.delete()
            except ReunionRegistration.DoesNotExist:
                return JsonResponse({'status': 'failed', 'error': 'Object does not exist'}, safe=False)
        return redirect('app:admin_dashboard')

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'admin_dashboard.html', context)


@user_is_admin
def export_excel(request):
    queryset = ReunionRegistration.objects.all()
    df = pd.DataFrame.from_records(queryset.values(
        'name', 'roll_number', 'email', 'number_of_guests', 'driver', 
        'total_amount_paid', 'is_payment_varified', 'upload_payment_slip', 
        'transaction_id', 'phone_no'  # Added new fields
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
            if obj.upload_payment_slip:  # Check if 'upload_payment_slip' exists
                image_path = os.path.join(image_folder_path, os.path.basename(obj.upload_payment_slip.name))
                if os.path.exists(image_path):
                    with open(image_path, 'rb') as f:
                        zipf.writestr(f'payment_slips/{os.path.basename(image_path)}', f.read())

    response = HttpResponse(s.getvalue(), content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename={zip_filename}'
    
    return response


@user_is_admin
@transaction.atomic  # Ensures atomicity of the database operations
def confirm_payment(request, pk):
    error_message = ""
    obj = ReunionRegistration.objects.get(pk=pk)
    form = ConfirmPaymentForm(request.POST or None)
    
    if request.method == 'POST':
        if form.is_valid():
            try:
                with transaction.atomic():
                    obj.is_payment_varified = True
                    obj.save()
                    return redirect('app:admin_dashboard')
            except Exception as e:
                error_message = str(e)
    print(error_message)
    context = {
        'form': form,
        'error_message': error_message,
    }
    return redirect('app:admin_dashboard')



@user_is_admin
def adminpannel_notice(request):
    search_query = request.GET.get('search', '')
    if search_query:
        notices = Notice.objects.filter(title__icontains=search_query)
    else:
        notices = Notice.objects.all()
    
    paginator = Paginator(notices, 10)  # Show 10 notices per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'notices': page_obj}
    return render(request, 'adminpannel_notice.html', context)


@user_is_admin
def create_notice(request):
    if request.method == "POST":
        title = request.POST['title']
        paragraph = request.POST.get('paragraph', '') 
        file = request.FILES.get('file')  

        new_notice = Notice(
            title=title,
            paragraph=paragraph,
            file=file 
        )
        new_notice.save()

    return HttpResponseRedirect(reverse('app:adminpannel_notice'))

@user_is_admin
def edit_notice(request):
    if request.method == "POST":
        notice_id = request.POST['notice_id']
        title = request.POST['title']
        paragraph = request.POST.get('paragraph', '')  
        file = request.FILES.get('file') 

        notice_to_edit = Notice.objects.get(id=notice_id)
        notice_to_edit.title = title
        notice_to_edit.paragraph = paragraph
        if file:
            notice_to_edit.file = file 
        notice_to_edit.save()

        return HttpResponseRedirect(reverse('app:adminpannel_notice'))




@user_is_admin
def delete_notice(request):
    if request.method == "POST":
        notice_id = request.POST['notice_id']
        Notice.objects.get(id=notice_id).delete()

        return HttpResponseRedirect(reverse('app:adminpannel_notice'))


@user_is_admin
def export_notice(request):
    notices = Notice.objects.all().values('id', 'title', 'paragraph', 'datetime_field', 'file')  # Changed 'image' to 'file'
    notices_list = list(notices)
    for notice in notices_list:
        if notice['file']:  # Changed 'image' to 'file'
            notice['file'] = str(notice['file'])
        if notice['datetime_field']:
            notice['datetime_field'] = make_naive(notice['datetime_field'])
    
    df = pd.DataFrame.from_records(notices_list)

    buffer = BytesIO()

    with ZipFile(buffer, 'w') as zipf:
        # Save DataFrame to Excel
        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        excel_data = excel_buffer.getvalue()
        zipf.writestr('notices.xlsx', excel_data)

        # Add files to the ZIP archive
        for notice in notices_list:
            if notice['id'] and Notice.objects.filter(id=notice['id']).first().file:  # Changed 'image' to 'file'
                file_path = Notice.objects.get(id=notice['id']).file.path  # Changed 'image' to 'file'
                zipf.write(file_path, os.path.basename(file_path))

    buffer.seek(0)
    response = HttpResponse(buffer.read(), content_type='application/zip')
    buffer.close()
    response['Content-Disposition'] = 'attachment; filename=notices.zip'

    return response



@user_is_admin
def adminpannel_achievement(request):
    search_query = request.GET.get('search', '')
    if search_query:
        achievements = Achievement.objects.filter(title__icontains=search_query)
    else:
        achievements = Achievement.objects.all()
    
    paginator = Paginator(achievements, 10)  # Show 10 achievements per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'achievements': page_obj}
    return render(request, 'adminpannel_achievement.html', context)


@user_is_admin
def create_achievement(request):
    if request.method == "POST":
        title = request.POST['title']
        paragraph = request.POST['paragraph']
        image = request.FILES.get('image')

        new_achievement = Achievement(
            title=title,
            paragraph=paragraph,
            image=image
        )
        new_achievement.save()

    return HttpResponseRedirect(reverse('app:adminpannel_achievement'))


@user_is_admin
def edit_achievement(request):
    if request.method == "POST":
        achievement_id = request.POST['achievement_id']
        title = request.POST['title']
        paragraph = request.POST['paragraph']
        image = request.FILES.get('image')

        achievement_to_edit = Achievement.objects.get(id=achievement_id)
        achievement_to_edit.title = title
        achievement_to_edit.paragraph = paragraph
        if image:
            achievement_to_edit.image = image
        achievement_to_edit.save()

    return HttpResponseRedirect(reverse('app:adminpannel_achievement'))


@user_is_admin
def delete_achievement(request):
    if request.method == "POST":
        achievement_id = request.POST['achievement_id']
        Achievement.objects.get(id=achievement_id).delete()

    return HttpResponseRedirect(reverse('app:adminpannel_achievement'))

@user_is_admin
def export_achievement(request):
    achievements = Achievement.objects.all().values('id', 'title', 'paragraph', 'image')
    achievements_list = list(achievements)

    for achievement in achievements_list:
        if achievement['image']:
            achievement['image'] = str(achievement['image'])

    df = pd.DataFrame.from_records(achievements_list)

    buffer = BytesIO()

    with ZipFile(buffer, 'w') as zipf:
        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        excel_data = excel_buffer.getvalue()
        zipf.writestr('achievements.xlsx', excel_data)

        for achievement in achievements_list:
            if achievement['id'] and Achievement.objects.filter(id=achievement['id']).first().image:
                image_path = Achievement.objects.get(id=achievement['id']).image.path
                zipf.write(image_path, os.path.basename(image_path))

    buffer.seek(0)
    response = HttpResponse(buffer.read(), content_type='application/zip')
    buffer.close()
    response['Content-Disposition'] = 'attachment; filename=achievements.zip'
    return response


@user_is_admin
def admin_carousel(request):
    latest_carousels = Carousel.objects.all().order_by('-id')[:3]
    context = {'latest_carousels': latest_carousels}
    return render(request, 'admin_carousel.html', context)

@user_is_admin
def delete_carousel(request, carousel_id):
    Carousel.objects.filter(id=carousel_id).delete()
    return HttpResponseRedirect(reverse('app:admin_carousel'))

@user_is_admin
def create_carousel(request):
    if request.method == "POST":
        title = request.POST.get('title')
        image = request.FILES.get('image')
        Carousel.objects.create(quote=title, image=image)
    return HttpResponseRedirect(reverse('app:admin_carousel'))


@user_is_admin
def admin_gallary(request):
    gallery_images = GalleryImage.objects.all().order_by('-id')
    context = {'gallery_images': gallery_images}

    if request.method == 'POST':
        caption = request.POST.get('caption')
        tag = request.POST.get('tag')
        image = request.FILES.get('image')

        new_image = GalleryImage(caption=caption, tag=tag, image=image)
        new_image.save()

        return redirect('app:admin_gallary')
    return render(request, 'admin_gallary.html', context)

# Gallary image delete
@user_is_admin
def delete_image(request, image_id):
    image = get_object_or_404(GalleryImage, id=image_id)
    image.image.delete(save=True)  # This will also delete the image file from the storage backend
    image.delete()
    return redirect('app:admin_gallary')


@user_is_admin
def admin_alumnimanagement(request):
    search_query = request.GET.get('search', '')
    profiles_list = Profile.objects.filter(user__is_alumni=True)

    # Search functionality
    if search_query:
        profiles_list = profiles_list.filter(
            Q(user__email__icontains=search_query) |
            Q(user__name__icontains=search_query) |
            Q(roll__icontains=search_query) |
            Q(phone_number__icontains=search_query)
        )

    # Pagination functionality
    paginator = Paginator(profiles_list, 10)  # Show 10 profiles per page
    page_number = request.GET.get('page')
    profiles = paginator.get_page(page_number)

    context = {
        'profiles': profiles,
        'search_query': search_query
    }
    return render(request, 'admin_alumnimanagement.html', context)


@user_is_admin
def edit_membership(request):
    if request.method == 'POST':
        profile_id = request.POST.get('profile_id')
        new_membership = request.POST.get('membership')
        profile = Profile.objects.get(id=profile_id)
        profile.membership = new_membership
        profile.save()
        return redirect('app:admin_alumnimanagement')  

@user_is_admin
def delete_user(request):
    if request.method == 'POST':
        profile_id = request.POST.get('profile_id')
        profile = Profile.objects.get(id=profile_id)
        user = profile.user
        user.delete()
        return redirect('app:admin_alumnimanagement')

@user_is_admin
def export_alumni_data(request):
    # Create CSV file
    csv_filename = "alumni_data.csv"
    csv_path = os.path.join(settings.MEDIA_ROOT, csv_filename)
    
    fieldnames = [
        'Name', 'Email', 'Roll', 'Phone',
        'Series', 'Current Position', 'Current Organization',
        'Previous Experience', 'Certificate', 'Skills',
        'Present Address', 'Home District', 'Blood Group',
        'Marital Status', 'LinkedIn', 'Facebook',
        'Membership', 'Name of Degree 1', 'Institution 1',
        'Name of Degree 2', 'Institution 2', 'Name of Degree 3',
        'Institution 3'
    ]
    
    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for profile in Profile.objects.all():
            writer.writerow({
                'Name': profile.user.name,
                'Email': profile.user.email,
                'Roll': profile.roll,
                'Phone': profile.phone_number,
                'Series': profile.series,
                'Current Position': profile.current_position,
                'Current Organization': profile.current_organization,
                'Previous Experience': profile.previous_experience,
                'Certificate': profile.certificate,
                'Skills': profile.skills,
                'Present Address': profile.present_address,
                'Home District': profile.home_district,
                'Blood Group': profile.get_blood_group_display(),
                'Marital Status': profile.get_marital_status_display(),
                'LinkedIn': profile.linkedin,
                'Facebook': profile.facebook,
                'Membership': profile.get_membership_display(),
                'Name of Degree 1': profile.name_of_degree1,
                'Institution 1': profile.institution1,
                'Name of Degree 2': profile.name_of_degree2,
                'Institution 2': profile.institution2,
                'Name of Degree 3': profile.name_of_degree3,
                'Institution 3': profile.institution3,
            })
    
    # Create ZIP file
    zip_filename = "alumni_data.zip"
    zip_path = os.path.join(settings.MEDIA_ROOT, zip_filename)
    
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        # Add the CSV file
        zipf.write(csv_path, csv_filename)

        # Add images
        for profile in Profile.objects.all():
            if profile.profile_picture:
                picture_path = profile.profile_picture.path
                zipf.write(picture_path, os.path.basename(picture_path))

    # Create FileResponse and serve the ZIP
    response = FileResponse(open(zip_path, 'rb'))
    response['Content-Type'] = 'application/zip'
    response['Content-Disposition'] = f'attachment; filename={zip_filename}'
    
    return response




def about(request):
    return render(request, 'about.html')


def first_reunion(request):
    
    # Fetch GalleryImage objects with tag 'first_reunion'
    gallery_images = GalleryImage.objects.filter(tag='first_reunion')
    
    # Paginator for gallery images
    image_paginator = Paginator(gallery_images, 10)  # Show 10 images per page
    image_page_number = request.GET.get('image_page')
    image_page_obj = image_paginator.get_page(image_page_number)
    
    context = {
        'gallery_images': image_page_obj,
    }
    return render(request, 'first_reunion.html', context)


def first_reunion_participant(request):
    search_query = request.GET.get('search', '')

    if search_query:
        reunion_registrations = ReunionRegistration.objects.filter(
            Q(name__icontains=search_query) |
            Q(roll_number__icontains=search_query) |
            Q(email__icontains=search_query)
        ).order_by('roll_number') 
    else:
        reunion_registrations = ReunionRegistration.objects.all().order_by('roll_number') 

    paginator = Paginator(reunion_registrations, 10)  # Show 10 records per page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'reunion_registrations': page_obj,
        'search_query': search_query,
    }
    return render(request, 'first_reunion_participant.html', context)



def first_reunion_registration(request):
    context = {}
    error_message = ''
    registration_successful = False
    
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        roll_number = request.POST.get('roll_number')
        number_of_guests = request.POST.get('number_of_guests', 0)  # Default to 0
        driver = request.POST.get('driver', 0)  # Default to 0
        total_amount_paid = request.POST.get('total_amount_paid')
        upload_payment_slip = request.FILES.get('upload_payment_slip', None)  # Default to None
        transaction_id = request.POST.get('transaction_id', '')  # Default to empty string
        phone_no = request.POST.get('phone_no', '')  # Default to empty string

        try:       
            with transaction.atomic():
                validate_integer(roll_number)
                validate_integer(total_amount_paid)
                
                # Conditionally validate these only if they are not empty
                if number_of_guests:
                    validate_integer(number_of_guests)
                if driver:
                    validate_integer(driver)

                new_registration = ReunionRegistration(
                    name=name,
                    email=email,
                    roll_number=int(roll_number),
                    total_amount_paid=int(total_amount_paid),
                    upload_payment_slip=upload_payment_slip,
                    transaction_id=transaction_id,
                    phone_no=phone_no
                )
                
                # Conditionally set these only if they are not empty
                if number_of_guests:
                    new_registration.number_of_guests = int(number_of_guests)
                if driver:
                    new_registration.driver = int(driver)
                    
                new_registration.save()
                registration_successful = True  # set flag to true if saved successfully
        except Exception as e:
            error_message = str(e)

    context['error_message'] = error_message
    context['registration_successful'] = registration_successful
    return render(request, 'first_reunion_registration.html', context)



def all_notices(request):
    search_query = request.GET.get('search', '')

    if search_query:
        all_notices_list = Notice.objects.filter(title__icontains=search_query).order_by('-datetime_field')
    else:
        all_notices_list = Notice.objects.all().order_by('-datetime_field')

    paginator = Paginator(all_notices_list, 15) 
    page = request.GET.get('page')
    all_notices = paginator.get_page(page)

    context = {
        'all_notices': all_notices,
        'search_query': search_query,
    }

    return render(request, "all_notices.html", context)


def single_notice(request, pk):
    notice = get_object_or_404(Notice, pk=pk)
    context = {
        'notice': notice,
        'file_url': notice.file.url if notice.file else None,
    }
    return render(request, 'single_notice.html', context)



def all_achievement(request):
    search_query = request.GET.get('search', '')

    if search_query:
        all_achievement_list = Achievement.objects.filter(title__icontains=search_query).order_by('-datetime_field')
    else:
        all_achievement_list = Achievement.objects.all().order_by('-datetime_field')

    paginator = Paginator(all_achievement_list, 15) 
    page = request.GET.get('page')
    all_achievement = paginator.get_page(page)

    context = {
        'all_achievement': all_achievement,
        'search_query': search_query,
    }

    return render(request, "all_achievement.html", context)


def single_achievement(request, pk):
    achievement = get_object_or_404(Achievement, pk=pk)
    context = {
        'achievement': achievement,
    }
    return render(request, 'single_achievement.html', context)


def interest(request):
    return render(request, 'interest.html')


def giving(request):
    return render(request, 'giving.html')


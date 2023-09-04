from django.urls import path

from app.views import *

app_name = "app"

urlpatterns = [
    path('', index, name='index'),
    path('alumni_signup/', alumni_signup, name='alumni_signup'),
    path('signin/', signin_view, name='signin'),
    path('logout/', logout_view, name='logout'),
    path('alumni_profile/<int:pk>/', alumni_profile, name='alumni_profile'),
    path('edit_profile/', edit_profile, name='edit_profile'),

    path('about/', about, name='about'),
    path('all_notices/', all_notices, name='all_notices'),
    path('single_notice/<int:pk>/', single_notice, name='single_notice'),
    path('all_achievement/', all_achievement, name='all_achievement'),
    path('single_achievement/<int:pk>/', single_achievement, name='single_achievement'),
    path('first_reunion/', first_reunion, name='first_reunion'),
    path('first_reunion_registration/', first_reunion_registration, name='first_reunion_registration'),
    path('all_alumni/', all_alumni, name='all_alumni'),
    path('interest/', interest, name='interest'),
    path('giving/', giving, name='giving'),
    path('first_reunion_participant/', first_reunion_participant, name='first_reunion_participant'),

    path('admin_signup/', admin_signup, name='admin_signup'),
    path('admin_dashboard/', admin_dashboard, name='admin_dashboard'),
    path('admin_dashboard/export_excel/', export_excel, name='export_excel'),
    path('confirm_payment/<int:pk>/', confirm_payment, name='confirm_payment'),
    path('adminpannel_notice/', adminpannel_notice, name='adminpannel_notice'),
    path('create_notice/', create_notice, name='create_notice'),
    path('edit_notice/', edit_notice, name='edit_notice'),
    path('delete_notice/', delete_notice, name='delete_notice'),
    path('export_notice/', export_notice, name='export_notice'),
    path('adminpannel_achievement/', adminpannel_achievement, name='adminpannel_achievement'),
    path('create_achievement/', create_achievement, name='create_achievement'),
    path('edit_achievement/', edit_achievement, name='edit_achievement'),
    path('delete_achievement/', delete_achievement, name='delete_achievement'),
    path('export_achievement/', export_achievement, name='export_achievement'),
    path('admin_carousel/', admin_carousel, name='admin_carousel'),
    path('delete_carousel/<int:carousel_id>/', delete_carousel, name='delete_carousel'),
    path('create_carousel/', create_carousel, name='create_carousel'),
    path('admin_gallary/', admin_gallary, name='admin_gallary'),
    path('delete_image/<int:image_id>/', delete_image, name='delete_image'),
    path('admin_alumnimanagement/', admin_alumnimanagement, name='admin_alumnimanagement'),
    path('delete_user/', delete_user, name='delete_user'),
    path('edit_membership/', edit_membership, name='edit_membership'),
    path('export_alumni_data/', export_alumni_data, name='export_alumni_data'),

]



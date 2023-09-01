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
    path('first_reunion/', first_reunion, name='first_reunion'),
    path('first_reunion_registration/', first_reunion_registration, name='first_reunion_registration'),
    path('all_alumni/', all_alumni, name='all_alumni'),

    
    path('admin_signup/', admin_signup, name='admin_signup'),
    path('admin_dashboard/', admin_dashboard, name='admin_dashboard'),
    path('admin_dashboard/export_excel/', export_excel, name='export_excel'),

]

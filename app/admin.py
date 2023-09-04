from django.contrib import admin
from app.models import *
# Register your models here.

admin.site.register(MyCustomUser)
admin.site.register(Profile)
admin.site.register(ReunionRegistration)
admin.site.register(Notice)
admin.site.register(Achievement)
admin.site.register(Carousel)
admin.site.register(GalleryImage)



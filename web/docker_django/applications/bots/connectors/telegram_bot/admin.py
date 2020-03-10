from django.contrib import admin
from .models import Question, UsersQuestion, UserInformation

admin.site.register(Question)
admin.site.register(UsersQuestion)
admin.site.register(UserInformation)

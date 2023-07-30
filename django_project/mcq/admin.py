from django.contrib import admin
from .models import Question, Section, Choice, Answer

# Register your models here.
admin.site.register(Question)
admin.site.register(Section)
admin.site.register(Choice)
admin.site.register(Answer)



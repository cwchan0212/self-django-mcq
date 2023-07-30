# Import Django Debug Toolbar library
from django.urls import path, include
from . import views

urlpatterns = [
#---------------------------------------------------------------------------------------------------------------------#
    # Map the path to the Django Debug Toolbar
    # path('__debug__/', include('debug_toolbar.urls')),
#---------------------------------------------------------------------------------------------------------------------#
    # Map the paths to main page index and login/logout + random quote
    path('', views.index, name='index'),
    path("data/section", views.section_index, name="section_index"),
    path("data/section/add", views.section_add, name="section_add"),
    path("data/section/action", views.section_action, name="section_action"),
    
    path("data/question", views.question_index, name="question_index"),
    path("data/question/new", views.question_new, name="question_new"),
    path("data/question/add", views.question_add, name="question_add"),
    path("data/question/action", views.question_action, name="question_action"),
    path("data/question/search", views.question_search, name="question_search"),

    path("data/quiz", views.quiz_index, name="quiz_index"),
    path("data/quiz/mode", views.quiz_mode, name="quiz_mode"),
    path("data/quiz/<int:question_id>", views.quiz_answer, name="quiz_answer"),

    path("data/study", views.study_index, name="study_index"),
    
]
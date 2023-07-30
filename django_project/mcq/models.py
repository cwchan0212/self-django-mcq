from django.db import models
from django.utils import timezone
from django.core.paginator import Paginator

import random
# Create your models here.

###################################################################################################
# Model "Section"
class Section(models.Model):
    section_id = models.IntegerField(null = False, primary_key = True)
    section_text = models.CharField(null = False, max_length = 255)
    questions_min_drawn = models.IntegerField(null = False)
    questions_max_drawn = models.IntegerField(null = False)

    def __str(self):
        print(f"{section_id}, {section_text}")

    def all():
        return Section.objects.all().order_by("section_id")


    def id(section_id):
        section = Section.objects.get(section_id = section_id)
        return section

    def insert(section_dictionary):
        section = Section.objects.create(**section_dictionary)        
        section_id = Section.objects.last().section_id
        return section_id

    def update(section_id, section_dictionary):
        row_affected = Section.objects.filter(section_id = section_id).update(**section_dictionary)
        return row_affected

    def delete(section_id):
        row_affected = Section.objects.filter(section_id = section_id).delete()
        return row_affected

###################################################################################################
# Model "Question"
class Question(models.Model):
    question_id = models.IntegerField(null = False, primary_key = True)
    question_text = models.CharField(null = False, max_length = 1000)
    question_explanation = models.TextField(null=True)
    section = models.ForeignKey(Section, on_delete = models.CASCADE)    

    def id(question_id):
        question = Question.objects.get(question_id = question_id)
        return question

    def insert(question_dictionary):
        question = Question.objects.create(**question_dictionary)
        question_id = Question.objects.last().question_id
        return question_id

    def update(question_id, question_dictionary):
        row_affected = Question.objects.filter(question_id = question_id).update(**question_dictionary)
        return row_affected

    def delete(question_id):
        row_affected = Question.objects.filter(question_id = question_id).delete()
        return row_affected

    def all(order_way=0):
        if order_way:
            questions = Question.objects.select_related("section").all().order_by('-question_id')
        else:
            questions = Question.objects.select_related("section").all().order_by('question_id')
        return questions

    def all_with_page(page_number, order_way=0):
        number_of_page = 50
        if order_way:
            questions = Question.objects.select_related("section").all().order_by('-question_id')
        else:
            questions = Question.objects.select_related("section").all().order_by('question_id')
        paginator = Paginator(questions, number_of_page)
        try:
            page_object = paginator.page(page_number)
        except:
            page_object = paginator.page(paginator.num_pages)        
        return page_object

 
    def one(question_id):
        question = Question.objects.select_related("section").get(question_id = question_id)
        choices = Choice.objects.filter(question=question)
        answers = Answer.objects.filter(question=question)
        return question, choices, answers
   
    def one_section(section_id):
        questions = Question.objects.select_related("section").filter(section_id = section_id)
        choices = Choice.objects.filter(question__in=questions)
        answers = Answer.objects.filter(question__in=questions)
        return questions, choices, answers

    def one_section_random(section_id):
        question_count = Question.objects.select_related("section").filter(section_id = section_id).count()
        count = 24 if question_count > 24 else question_count        
        question_ids = list(Question.objects.values_list('question_id', flat=True))
        random.shuffle(question_ids)
        random_question_ids = question_ids[:count]
        questions = Question.objects.select_related('section').filter(question_id__in=random_question_ids)
        choices = Choice.objects.filter(question__in=questions)
        answers = Answer.objects.filter(question__in=questions)
        return  questions, choices, answers

    def search_by_keyword(section_id, keyword):
        if section_id != "all":
            questions = Question.objects.select_related("section").filter(
                section_id = section_id, 
                question_text__icontains = keyword
            )
        else:
            questions = Question.objects.select_related("section").filter(question_text__icontains = keyword)  
        return questions

    def search_by_keyword_with_page(section_id, keyword, page_number):
        number_of_page = 25
        if section_id != "all":
            questions = Question.objects.select_related("section").filter(
                section_id = section_id,
                question_text__icontains = keyword
            ).order_by("question_id")
        else:
            questions = Question.objects.select_related("section").filter(
                question_text__icontains = keyword
            ).order_by("question_id")
        paginator = Paginator(questions, number_of_page)
        try:
            page_object = paginator.page(page_number) 
        except:
            page_object = paginator.page(paginator.num_pages)
        return page_object

###################################################################################################
# Model "Choice"
class Choice(models.Model):
    choice_id = models.IntegerField(null = False, primary_key = True)
    choice_text = models.CharField(null = False, max_length = 255)
    question = models.ForeignKey(Question, on_delete = models.CASCADE, related_name="choice_set")

    def id(choice_id):
        choice = Choice.objects.get(choice_id = choice_id)
        return choice

    def insert(choice_dictionary):
        choice = Choice.objects.create(**choice_dictionary)
        choice_id = Choice.objects.last().choice_id
        return choice_id
    
    def update(choice_id, choice_dictionary):
        row_affected = Choice.objects.filter(choice_id = choice_id).update(**choice_dictionary)
        return row_affected

###################################################################################################
# Model "Answer"
class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete = models.CASCADE, related_name="answer_set")
    choice = models.ForeignKey(Choice, on_delete = models.CASCADE)

    def insert(answer_dictionary):
        answer = Answer.objects.create(**answer_dictionary)
        return answer

    def delete(question_id):
        row_affected = Answer.objects.filter(question_id = question_id).delete()
        return row_affected

    def fetch(question_id):
        question = Question.objects.filter(question_id = question_id).values('question_explanation').first()
        answers = Answer.objects.filter(question_id = question_id).values_list('choice_id', flat=True)
        return question["question_explanation"], list(answers)
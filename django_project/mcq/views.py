import random, json
from django.utils.http import urlencode
from django.http import JsonResponse
from django.forms.models import model_to_dict

from django.utils import timezone
from datetime import datetime

from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from .models import Section, Question, Choice, Answer

# Create your views here.

###################################################################################################
# Index page redirect to /data/quiz/
def index(request):
    try:
        del request.session["position"] 
    except:
        pass
    return redirect("/data/quiz")

###################################################################################################
# Section: index
def section_index(request):
    request.session["position"] = "section"
    context = {}
    sections = Section.all()
    headers = {
        "text": "Section: Classify questions by sections",
        "image": "/static/img/setup-section.png"
    }
    if sections:
        context = {
            "sections": sections,
            "headers": headers,
        }
    return render(request, "data/section/index.html", context)

###################################################################################################
# Section: add new 
def section_add(request):
    if request.method == "POST":
        section_text = request.POST.get("section_text").strip()
        questions_min_drawn = request.POST.get("questions_min_drawn").strip()
        questions_max_drawn = request.POST.get("questions_max_drawn").strip()
        if section_text and questions_min_drawn and questions_max_drawn:
            section_dictionary = {
                "section_text": section_text,
                "questions_min_drawn": int(questions_min_drawn),
                "questions_max_drawn": int(questions_max_drawn)
            }
            section_id = Section.insert(section_dictionary)
            messages.success(request, f"The section is CREATED successfully. [#{section_id}]")
        return HttpResponseRedirect("/data/section")
    else:
        return HttpResponseRedirect("/data/section")

###################################################################################################
# Section: update or delete 
def section_action(request):
    section_dictionary = {}
    if request.method == "POST":
        section_id = request.POST.get("section_id").strip()
        section_text = request.POST.get("section_text").strip()
        questions_min_drawn = request.POST.get("questions_min_drawn").strip()
        questions_max_drawn = request.POST.get("questions_max_drawn").strip()
        section_dictionary = {
            "section_text": section_text,
            "questions_min_drawn": questions_min_drawn,
            "questions_max_drawn": questions_max_drawn,
        }
        if request.POST.get("section_mode") == "update":
            if section_id and section_text and questions_min_drawn and questions_max_drawn:
                section = Section.update(section_id, section_dictionary)
                messages.success(request, f"The section is UPDATED successfully. [#{section_id}]")
                return HttpResponseRedirect("/data/section")
            else:
                return HttpResponseRedirect("/data/section")
        elif request.POST.get("section_mode") == "delete":
            if section_id:
                section = Section.delete(section_id)
                messages.success(request, f"The section is DELETED successfully. [#{section_id}]")
                return HttpResponseRedirect("/data/section")
    else:
        return HttpResponseRedirect("/data/section")

###################################################################################################
# Question: index
def question_index(request):
    request.session["position"] = "question"
    questions = None
    direction = -1
    page_number = request.GET.get("page", 1)
    headers = {
        "text": "Question: Store the question banks",
        "image": "/static/img/setup-question.png"
    }
    questions = Question.all_with_page(page_number, direction)
    context = {
        "questions": questions,
        "headers": headers,
    }
    return render(request, "data/question/index.html", context)
    
###################################################################################################
# Question: Add new
def question_new(request):
    context = {}
    sections = Section.all()
    question_list = ["answer_type", "section_id", "question_text", "choice_text", "answer_id"]
    headers = {
        "text": "Question: Add new question",
        "image": "/static/img/question.png"
    }
    if sections:
        context = {
            "sections": sections,
            "headers": headers,
        }
    return render(request, "data/question/add.html", context)

###################################################################################################
# question: add new 
def question_add(request):
    context, question_form_dictionary = {}, {}
    if request.method == "POST":
        question_form_dictionary = request.POST.copy()
        number_of_option = 8
        answer_type, section_id = 0, 0 
        answer_type_checked = False
        question_text, action = "", ""
        choice_text, answer_id = [], []

        if "answer_type" not in question_form_dictionary: 
            question_form_dictionary["answer_type"] = ""

        if "answer_id" not in question_form_dictionary: 
            question_form_dictionary["answer_id"] = ""

        section_id = question_form_dictionary.get("section_id")
        question_text = question_form_dictionary.get("question_text").strip()
        question_explanation = question_form_dictionary.get("question_explanation").strip()
        answer_type = question_form_dictionary.get("answer_type")
        choice_text = question_form_dictionary.getlist("choice_text")
        answer_id = question_form_dictionary.getlist("answer_id")

        if not section_id:
            messages.error(request, "Please select the section.")
        else:
            question_form_dictionary["section_id"] = int(section_id)
        if not question_text:
            messages.error(request, "Please select the question.")

        if not answer_type or (answer_type != "1" and answer_type != "2"):
            messages.error(request, "Please select the answer type.")
        else:
            question_form_dictionary["answer_type"] = int(answer_type)

        if answer_type == "1" and choice_text.count("") > number_of_option - 2:
            messages.error(request, f"Please select the choice X ??? .  {answer_type} {choice_text}")
        else:
            question_form_dictionary["choice_text"] = choice_text

        if "" in answer_id:
            messages.error(request, "Please select the answer(s).")
        else:   
            question_form_dictionary["answer_id"] = answer_id

        message_list = list(messages.get_messages(request))

        if not message_list:
            section = Section.id(section_id)
            question_dictonary = {
                "question_text": question_text,
                "question_explanation": question_explanation,
                "section": section,
            }
            question_id = Question.insert(question_dictonary)

            if question_id:
                question_one = Question.id(question_id)
                choice_id_list = []

                if answer_type == "1":
                    choice_range = range(number_of_option)
                elif answer_type == "2":
                    choice_range = range(number_of_option, len(choice_text))
                else:
                    choice_range = []

                for index in choice_range:
                    one = choice_text[index].strip()
                    if one: 
                        choice_dictionary = {
                            "choice_text": one,
                            "question": question_one,
                        }
                        choice_id = Choice.insert(choice_dictionary)
                        choice_id_list.append(choice_id)

                for index, one in enumerate(answer_id):
                    if answer_type == "1":
                        choice_id = choice_id_list[int(one)-1]
                    elif answer_type == "2":
                        choice_id = choice_id_list[int(one)-1-number_of_option]

                    choice_one = Choice.id(choice_id)
                    answer_dictionary = {
                        "question": question_one,
                        "choice": choice_one,
                    }
                    answer = Answer.insert(answer_dictionary)
                    
                messages.success(request, f"The question is CREATED successfully. [#{question_id}]")
                return HttpResponseRedirect("/data/question")

            return HttpResponse(question_id)
        else:
            sections = Section.all()
            if sections:
                context = {
                    "sections": sections,
                    "messages": message_list,
                    "input": question_form_dictionary
                }
            return render(request, "data/question/add.html", context)

###################################################################################################
# Question: edit / update / delete
def question_action(request):
    context = {}
    action = request.POST.get("action")
    question_id = request.POST.get("question_id")
    headers = {
        "text": "Question: Modify the question",
        "image": "/static/img/question.png"
    }
    if request.method == "POST" and action and question_id:        
        if action == "edit":
            sections = Section.all()
            question_one = Question.one(question_id)
            question, choice, answer = question_one
            context = {
                "sections": sections,
                "question": question,
                "choices": choice,
                "answers": answer,
                "headers": headers,
            }
            return render(request, "data/question/form.html", context)
        if action == "update":
            question_form_dictionary = dict(request.POST)
            section_id, question_id, question_text, question_explanation, choice_id, choice_text, answer_id, action = "", "", "", "", [], [], [], ""
            for key, value in question_form_dictionary.items():
                if key == "section_id":
                    section_id = int(value[0])
                elif key == "question_id":
                    question_id = int(value[0])
                elif key == "question_text":
                    question_text = value[0].strip()
                elif key == "question_explanation":
                    question_explanation = value[0].strip()
                elif key == "choice_id":
                    choice_id = [int(v) for v in value if v]
                elif key == "choice_text":
                    choice_text = [v.strip() for v in value if v]
                elif key == "answer_id":
                    answer_id = [int(v) for v in value if v]
                elif key == "action":
                    action = value

            question_dictionary, choice_dictionary, answer_dictionary = {}, {}, {}
            choice_id_list = []

            if section_id and question_id and question_text and choice_id and choice_text and answer_id and action:
                this_section = Section.id(section_id)
                question_dictionary = {
                    "question_text": question_text,
                    "question_explanation": question_explanation,
                    "section": this_section
                }
                question_updated = Question.update(question_id, question_dictionary)

                if question_updated:
                    if choice_id and answer_id: 
                        for index, id in enumerate(choice_id):
                            choice_dictionary = {
                                "choice_text": choice_text[index],
                                "question_id": question_id
                            }
                            choice_updated = Choice.update(id, choice_dictionary)
                        answer_deleted = Answer.delete(question_id)
                        if answer_deleted:
                            question_one = Question.id(question_id)
                            for index, id in enumerate(answer_id):
                                choice_one = Choice.id(id)
                                answer_dictionary = {
                                    "question": question_one,
                                    "choice": choice_one,
                                }
                                answer_one = Answer.insert(answer_dictionary)

                            messages_to_remove = messages.get_messages(request)
                            for message in messages_to_remove:
                                message.delete()

                            messages.success(request, f"The question is UPDATED successfully. [#{question_id}]")
                            return HttpResponseRedirect("/data/question")

        elif action == "delete":
            row_affected = Question.delete(question_id)
            messages.success(request, f"The question is DELETED successfully. [#{question_id}]")
            return HttpResponseRedirect("/data/question")

###################################################################################################
# Question: search
def question_search(request):
    request.session["position"] = "search"
    referral_url = request.META.get('HTTP_REFERER', None)

    if referral_url is not None and "search" not in referral_url and "inputs" in request.session:
        del request.session["inputs"]

    sections = Section.all()
    page_number = request.GET.get("page", 1)
    questions = None

    if request.method == "POST":
        inputs = {
            "section_id": request.POST.get("section_id"),
            "keyword": request.POST.get("keyword").strip()
        }
        request.session["inputs"] = inputs
    elif request.method == "GET":
        inputs = request.session.get("inputs", {})
    else:
        return HttpResponse("Method not allowed", status=405)
    
    section_id, keyword = inputs.get("section_id"), inputs.get("keyword")

    if section_id and keyword:
        questions = Question.search_by_keyword_with_page(section_id, keyword, page_number)

    context = {
        "sections": sections,
        "section_id": section_id,
        "inputs": inputs,
        "questions": questions
    }
    return render(request, "data/question/search.html", context)

###################################################################################################
# Quiz: index
def quiz_index(request, section_id="1"):    
    request.session["position"] = "quiz"
    sections = Section.all()
    context = {
        "sections": sections,
        "inputs": ""
    }
    if request.method == "POST":
        section_id = request.POST.get("section_id")
        if section_id:
            request.session["section_id"] = section_id
            quiz_mode = request.POST.get("quiz_mode")
            request.session["quiz_mode"] = quiz_mode
            quiz_mode_session = request.POST.get("quiz_mode_session")
            request.session['quiz_mode_session'] = quiz_mode_session
            request.session["quiz_mode"] = request.session["quiz_mode_session"] if request.session["quiz_mode"] is None else request.session["quiz_mode"]
            if sections:            
                if request.session["quiz_mode"] == "random": 
                    questions, choices, answers = Question.one_section_random(section_id = section_id)
                else:
                    questions, choices, answers = Question.one_section(section_id = section_id)
                inputs = {
                    "section_id": section_id,
                }
                context = {
                    "questions": questions,
                    "sections": sections,
                    "choices": choices,
                    "answers": answers,
                    "inputs": inputs,
                    "quiz_mode": quiz_mode
                }
        else:
            quiz_mode = request.POST.get("quiz_mode")
    return render(request, "data/quiz/index.html", context)

###################################################################################################
# Quiz: mode (obsolete)
def quiz_mode(request):
    referrer = request.META.get('HTTP_REFERER')
    suffix_referrer = referrer.split("/")[-1]

    if request.method == "POST":
        section_id = request.POST.get("section_id")
        request.session['section_id'] = section_id
        quiz_mode = request.POST.get("quiz_mode")
        request.session["quiz_mode"] = quiz_mode
    return redirect(referrer)

###################################################################################################
# Quiz: Answer in JSON (obsolete)
def quiz_answer(request, question_id):
    explanation, answers = Answer.fetch(question_id)
    response = {
        "explanation": explanation,
        "answers": answers
    }    
    return JsonResponse(response)

###################################################################################################
# Study: Index
def study_index(request):
    request.session["position"] = "study"
    headers = {
        "text": "Study: Master the knowledge ",
        "image": "/static/img/study.png"
    }

    context = {
        "headers": headers
    }
    return render(request, "data/study/index.html", context)
import random, json
from django.utils.http import urlencode
from django.http import JsonResponse
from django.forms.models import model_to_dict
from django.utils import timezone
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from .models import Section, Question, Choice, Answer, Picture
# Create your views here.
###################################################################################################
# Index page redirect to /data/quiz/
def index(request):
    try:
        del request.session["position"] 
    except:
        pass
    return redirect("/data/home")

def home_index(request):
    request.session["position"] = "home"

    headers = {
        "text": "Get ready!?",
        "image": "/static/img/home.png"
    }
    request.session["headers"] = headers
    context = {
        "headers": headers
    }

    return render(request, "data/home.html", context)

###################################################################################################
# Section: index
def section_index(request):
    request.session["position"] = "section"
    context = {}
    sections = Section.all()
    headers = {
        "text": "Classify questions by sections",
        "image": "/static/img/setup-section.png"
    }
    request.session["headers"] = headers
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
        "text": "Store the question banks",
        "image": "/static/img/setup-question.png"
    }
    request.session["headers"] = headers
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
        "text": "Add new question",
        "image": "/static/img/question.png"
    }
    request.session["headers"] = headers
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
        "text": "Modify the questions",
        "image": "/static/img/question.png"
    }
    request.session["headers"] = headers
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
    headers = {
        "text": "Search questions",
        "image": "/static/img/search.png"
    }
    request.session["headers"] = headers
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
    number_of_items = 12
    if section_id and keyword:
        questions = Question.search_by_keyword_with_page(section_id, keyword, page_number, number_of_items)
    context = {
        "sections": sections,
        "section_id": section_id,
        "inputs": inputs,
        "questions": questions,
        "headers": headers,
        "number_of_items": number_of_items,
    }
    return render(request, "data/question/search.html", context)
###################################################################################################
# Quiz: index
def quiz_index(request, section_id="6"):    
    request.session["position"] = "quiz"
    sections = Section.all()
    context = {
        "sections": sections,
        "inputs": ""
    }
    headers = {
        "text": "Test your knowledge",
        "image": "/static/img/quiz.png"
    }
    request.session["headers"] = headers

    if request.method == "GET":
        # default section_id = 6
        questions, choices, answers = Question.one_section_random(section_id = section_id)
        inputs = {
            "section_id": section_id, 
        }
        context = {
            "questions": questions,
            "sections": sections,
            "choices": choices,
            "answers": answers,
            "inputs": inputs,
            "quiz_mode": "random"
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
# Picture: Index
def picture_index(request):
    request.session["position"] = "picture"
    sections = Section.all()
    headers = {
        "text": "Manage media library",
        "image": "/static/img/picture.png"
    }
    request.session["headers"] = headers
    context = {
        "sections": sections,
        "headers": headers,
    }
    if request.method == "GET":
        pictures = None
        direction = -1
        page_number = request.GET.get("page", 1)
        pictures = Picture.all_with_page(page_number, direction)
        context["pictures"] = pictures
        return render(request, "data/picture/index.html", context)
    
    elif request.method == "POST":
        if request.POST.get("picture_mode") == "add":
            section_id = request.POST.get("section_id")
            prefix = request.POST.get("prefix").strip()
            description = request.POST.get("description").strip()
            inputs = {
                "section_id": section_id,
                "prefix": prefix,
                "description": description,
            }
            context = {
                "sections": sections,
                "headers": headers,
                "inputs": inputs
            }
            if not prefix: 
                messages.error(request, "Please enter the prefix.")
            if not description:
                messages.error(request, "Please enter the description.")
            if not request.FILES:
                messages.error(request, "Please upload the picture.")
            else: 
                picture_file = request.FILES['picture']
                picture_filename = picture_file.name
                picture_blob = picture_file.read()
                picture_size = picture_file.size
            message_list = list(messages.get_messages(request))
            if not message_list:      
                section = Section.id(inputs["section_id"])
                picture_dictionary = {
                    "picture_prefix": inputs["prefix"],
                    "picture_filename": picture_filename,
                    "picture_description": inputs["description"],
                    "picture_blob": picture_blob,
                    "picture_size": picture_size,
                    "section": section
                }
                picture_id = Picture.insert(picture_dictionary)
                if picture_id:
                    pictures = Picture.all()
                    sections = Section.all()
                    context = {
                        "pictures": pictures,
                        "sections": sections,
                    }
                    messages.success(request, f"The picture is CREATED successfully. [#{picture_id}]")
                    return redirect("/data/picture")  
            else:
                context = {
                    "sections": Section.all(),
                    "pictures": Picture.all(),
                    "inputs": inputs,
                }        
        elif request.POST.get("picture_mode") == "update": 
            picture_id = request.POST.get("picture_id")
            section_id = request.POST.get("section_id")
            prefix = request.POST.get("prefix").strip()
            description = request.POST.get("description").strip()
            picture_dictionary = {
                "picture_prefix": prefix,
                "picture_description": description,
                "section": Section.id(section_id),
            }
            if section_id and picture_id and prefix and description:
                row_affected = Picture.update(picture_id, picture_dictionary)
                context = {
                    "sections": Section.all(),
                    "pictures": Picture.all(),
                }
                messages.success(request, f"The picture is UPDATED successfully. [#{picture_id}]")
            else:
                if prefix is None:
                    messages.error(request, f"Please enter the prefix.")
                if description is None:
                    messages.error(request, f"Please enter the description.")
        elif request.POST.get("picture_mode") == "delete":
            picture_id = request.POST.get("picture_id")
            if picture_id:
                row_affected = Picture.delete(picture_id)
                pictures = Picture.all()
                context = {
                    "sections": sections,
                    "pictures": pictures,
                }
                messages.success(request, f"The picture is DELETED successfully. [#{picture_id}]")
        referral_url = request.META.get('HTTP_REFERER', None)
        suffix_referrer = referral_url.split("/")[-1]
        redirect_url = "/data/picture"
        if "?page=" in suffix_referrer:
            redirect_url = f"/data/{suffix_referrer}"
        return redirect(redirect_url)
###################################################################################################
# Study: Index
def study_index(request):
    request.session["position"] = "study"
    headers = {
        "text": "Master the knowledge ",
        "image": "/static/img/study.png"
    }
    pictures = Picture.all()
    # pictures = {
    #     "2_1": [2, "mapofuk.jpg", "The countries that make up the UK: England, Scotland, Wales and Northern Ireland"],
    #     "3_1": [3, "stonehenge-aerial.jpg", "The world heritage site of Stonehenge"],
    #     "3_2": [3, "anglo-saxon-helmet.jpg", "An Anglo-Saxon helmet found at Sutton Hoo – currently on display at the British Museum"],
    #     "3_3": [3, "bayeux-tapestry.jpg", "Part of the Bayeux Tapestry – the linen cloth is nearly 70 metres (230 feet) and is embroidered with coloured wool"],
    #     "3_4": [3, "York-Minister-Stained-Glass.jpg", "York Minister Stained Glass"],        
    #     "3_5": [3, "henry-the-eighth.jpg", "Henry VIII was king of England from 21 April 1509 until his death on 28 January 1547"],
    #     "3_6": [3, "Elizabeth-I.jpg", "Elizabeth I was the younger daughter of Henry VIII"],
    #     "3_7": [3, "Shakespeare.jpg", "Shakespeare is widely regarded as the greatest writer in the English language"],
    #     "3_8": [3, "st-georges-cross.jpg", "St. Andrew’s Cross of Scotland"],
    #     "3_9": [3, "Richard-Arkwright-carding-machine.jpg", "Richard Arkwright’s carding machine"],
    #     "3_10": [3, "The-Battle-of-Trafalgar.jpg", "The Battle of Trafalgar (21 October 1805) was a naval engagement fought by the British Royal Navy against the combined fleets of the French Navy and Spanish Navy"],
    #     "3_11": [3, "union-jack.jpg", "The Union Flag also known as the Union Jack"],		
    #     "3_12": [3, "england-flag-300x180.jpg", "The crosses of the three countries which combined to form the Union Flag"],
    #     "3_13": [3, "scotland-flag-300x180.jpg", "The crosses of the three countries which combined to form the Union Flag"],	
    #     "3_14": [3, "st-patrick-flag-300x180.jpg", "The crosses of the three countries which combined to form the Union Flag"],
    #     "3_15": [3, "union-jack-1-300x180.jpg", "The crosses of the three countries which combined to form the Union Flag"],
    #     "3_16": [3, "wales-flag.jpg", "The official Welsh Flag"],
    #     "3_17": [3, "clifton-suspension-bridge.jpg", "The Clifton suspension Bridge, designed by Isambard Kingdom Brunel, spanning the Avon Gorge"],		
    #     "3_18": [3, "soldiers-trences-ww2.jpg", "Soldiers fighting in the trenches during the First World War"],
    #     "3_19": [3, "winston-churchill.jpg", "Winston Churchill, best known for his leadership of the UK during the Second World War"],
    #     "3_20": [3, "raf-ww2.jpg", "The Royal Air Force helped to defend Britain in the Second World War"],
    #     "4_1": [4, "uk-cities.jpg", "The cities of the UK"],		
    #     "4_2": [4, "westminster-abbey.jpg", "Westminster Abbey has been the coronation church since 1066 and is the final resting place of 17 monarchs"],		
    #     "4_3": [4, "Christmas-Day-meal.jpg", "A typical Christmas Day meal"],		
    #     "4_4": [4, "diwali-leicester.jpg", "Diwali is popularly known as the Festival of lights"],		
    #     "4_5": [4, "cenotaph.jpg", "Unveiled in 1920, the Cenotaph is the centerpiece to the Remembrance Day service"],
    #     "4_6": [4, "cricket.jpg", "Cricket is one of the many famous sports originating in Britain"],
    #     "4_7": [4, "royal-albert-hall.jpg", "The Royal Albert Hall is the venue for the Last Night of the Proms"],
    #     "4_8": [4, "tate-modern.jpg", "Tate modern is based in the former Bank side Power Station in central London"],
    #     "4_9": [4, "big-ben.jpg", "Big Ben"],
    #     "4_10": [4, "eden-project.jpg", "The Eden Project"],
    #     "4_11": [4, "edinburgh-castle.jpg", "Edinburgh Castle"],		
    #     "4_12": [4, "giants-causeway.jpg", "The Giant’s Causeway"],
    #     "4_13": [4, "loch-lomond.jpg", "Loch Lomond and the Trossachs National Park"],
    #     "4_14": [4, "london-eye.jpg", "London Eye"],
    #     "4_15": [4, "snowdonia.jpg", "Snowdonia"],
    #     "4_16": [4, "tower-of-london.jpg", "The Tower of London"],
    #     "4_17": [4, "lake-district.jpg", "The Lake District"],	
    #     "5_1": [5, "queen-of-england.jpg", "Queen Elizabeth II, head of state of the UK"],
    #     "5_2": [5, "houses-of-parliament.jpg", "The Houses of Parliament, one of the centres of political life in the UK and a World Heritage Site"],
    #     "5_3": [5, "The-Welsh-Assembly-building.jpg", "The Welsh Assembly building, opened in March 2006"],
    #     "5_4": [5, "Scottish-Parliament-Building.jpg", "The Scottish Parliament Building, opened in October 2004"],
    #     "5_5": [5, "stormont.jpg", "The Northern Ireland Building, known as Stormont"],
    #     "5_6": [5, "english-police.jpg", "The police in the UK protect life and property, prevent disturbances, and prevent and detect crime"],	
    #     "5_7": [5, "homework.jpg", "Parents often help in classrooms, by supporting activities or listening to children read"],	
    #     "5_8": [5, "volunteer-work.jpg", "Voluntary organization work to improve the lives of people, animals and environment in many different ways"],	
    # }
    request.session["headers"] = headers
    context = {
        "headers": headers,
        "pictures": pictures,
    }
    return render(request, "data/study/index.html", context)
###################################################################################################
def reference_index(request):

    request.session["position"] = "reference"
    headers = {
        "text": "Master the knowledge ",
        "image": "/static/img/study.png"
    }
    return render(request, "data/reference/index.html")
from django import template
from django.utils.safestring import mark_safe
import math, base64

register = template.Library()

@register.filter
def choice_count(choices, question_id):
    return choices.filter(question_id=question_id).count()

@register.filter
def answer_count(answers, question_id):
    return answers.filter(question_id=question_id).count()

@register.filter
def answer_list(answers, question_id):
    return answers.filter(question_id=question_id).values_list('choice_id', flat=True)

@register.filter
def modulo(dividend, divisor):
    return dividend % divisor

@register.filter
def quotient(dividend, divisor):
    return math.ceil(dividend / divisor)

@register.filter
def stringToInteger(string):
    num = 0 
    try:
        num = int(string)
    except:
        return -1
    return num


@register.filter
def replace_string(string, word1, word2=None):
    if word2 is None:
        return string.replace(word1, "")
    return string.replace(word1, word2)

@register.filter
def row_height(a, b):
    print(a, b, type(a), type(b))
    return (a - int(b))

@register.filter
def choice_type(choices, answers):
    true_choice = choices.filter(choice_text="True").exists()
    false_choice = choices.filter(choice_text="False").exists()

    if true_choice and false_choice and len(answers) == 1:
        return "radio"
    else:
        return "checkbox"

@register.filter
def picture_source(pictures, picture_id):
    picture_path = ""
    if pictures:
        for picture in pictures:
            if picture.picture_id == picture_id:
                picture_path = f"data:image/png;base64,{ encode_base64(picture.picture_blob) }"
                return picture_path
        #picture_path = f"/static/img/{pictures[article_index][0]}/{pictures[article_index][1]}"
    return picture_path

@register.filter
def picture_text(pictures, picture_id):
    picture_alt = ""
    if pictures:
        for picture in pictures:
            if picture.picture_id == picture_id:
                picture_alt = f"{picture.picture_description}"
                return picture_alt
    return picture_alt

@register.filter
def picture_grid(pictures, article_index):
    picture_html = ""

    if pictures and article_index:
        picture_html = f'''
            <div class="container_picture">
                <div class="picture_source">
                    <img alt="{picture_text(pictures, article_index)}" title="{picture_text(pictures, article_index)}" src="{picture_source(pictures, article_index)}">
                </div>
                <div class="picture_text">
                    {picture_text(pictures, article_index)}
                </div>
            </div>
        '''   
    return picture_html

@register.filter
def encode_base64(binary_data):
    return base64.b64encode(binary_data).decode('utf-8')

@register.filter
def picture_box(pictures, picture_id):
    picture_html = ""
    
    for picture in pictures:
        if picture.picture_id == picture_id:
            #print(picture)

            picture_html = f'''
                <div class="container_picture">
                    <div class="picture_source">
                        <img alt="{ picture.picture_description }" title="{ picture.picture_description }" 
                            src="data:image/png;base64,{ encode_base64(picture.picture_blob) }" />
                    </div>
                    <div class="picture_text">
                        { picture.picture_description }
                    </div>
                </div>
            '''
            return picture_html
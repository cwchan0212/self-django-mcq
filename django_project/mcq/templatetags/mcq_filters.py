from django import template
import math

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
def replace_string(string, word1, word2=None):
    if word2 is None:
        return string.replace(word1, "")
    return string.replace(word1, word2)

@register.filter
def choice_type(choices, answers):
    true_choice = choices.filter(choice_text="True").exists()
    false_choice = choices.filter(choice_text="False").exists()

    if true_choice and false_choice and len(answers) == 1:
        return "radio"
    else:
        return "checkbox"
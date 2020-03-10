import datetime
import random
import time
import telepot
import pymorphy2
from fstring import fstring
from django.http import HttpResponse
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.loop import MessageLoop

from telegram_bot.models import Question, UsersQuestion, UserInformation

TOKEN = '566642144:AAFqwMUm9iXt4bRIdUmEDYA_c6eUckBhQxY'
TelegramBot = telepot.Bot(TOKEN)

keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='1', callback_data='button1'),
     InlineKeyboardButton(text='2', callback_data='button2'),
     InlineKeyboardButton(text='3', callback_data='button3')],
])

keyboard2 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Деталі', callback_data='more'),
     InlineKeyboardButton(text='Вибір послуг', callback_data='back'),
     InlineKeyboardButton(text='Інформація', callback_data='grammar')],
])
keyboard3 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Більше деталей', callback_data='more'),
     InlineKeyboardButton(text='Попередній список', callback_data='back')],
])


def index(request):
    bot = telepot.Bot(TOKEN)
    MessageLoop(bot, {'chat': on_chat_message,
                      'callback_query': on_callback_query}).run_as_thread()
    print('Слухаю Вас ...')
    while 1:
        time.sleep(10)
        return HttpResponse("Привіт! Я бот")


def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    commands = ['/start']
    user_question = UsersQuestion.objects.filter(user_id=chat_id)
    user_information = UserInformation.objects.filter(user_id=chat_id).first()
    lenght = len(user_question)
    if lenght > 0:
        if msg["text"] == user_question[lenght - 1].question.answer_text:
            cost_question = user_question[lenght - 1].question.cost
            score = user_information.score + cost_question
            word_name_1 = get_name_for_number(cost_question)
            word_name_2 = get_name_for_number(score)
            date = user_information.date_registered
            TelegramBot.sendMessage(chat_id,
                                    text=fstring('Супер! Вас записано'),
                                    reply_markup=keyboard3)
            user_question[lenght - 1].answer = msg["text"]
            user_question[lenght - 1].save()
            user_information.score = score
            user_information.save()
        elif msg["text"] not in commands:
            TelegramBot.sendMessage(chat_id,
                                    text=fstring('На жаль, зайнято'),
                                    parse_mode='Markdown',
                                    reply_markup=keyboard2)
            user_question[lenght - 1].answer = msg["text"]
            user_question[lenght - 1].save()
    if msg["text"] == commands[0]:
        if not user_information:
            now = datetime.datetime.now()
            user_information = UserInformation(user_id=chat_id, date_registered=now.strftime("%Y-%m-%d"), score=0)
            user_information.save()
        TelegramBot.sendMessage(chat_id, 'Выберите категорию', reply_markup=keyboard)


def on_callback_query(msg):
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
    print('Callback Query:', query_id, from_id, query_data)
    msg_idf = telepot.message_identifier(msg['message'])

    if query_data == 'back':
        TelegramBot.editMessageText(msg_idf, text="Виберіть категорію", reply_markup=keyboard)
    elif query_data == 'grammar':
        photos = ['https://englsecrets.ru/wp-content/uploads/2013/05/formy-glagola-to-be.jpg',
                  'http://englishtexts.ru/wp-content/VerbToBe.png',
                  'https://lingvoelf.ru/images/english_grammar/at_on_in.JPG']
        user_question = UsersQuestion.objects.filter(user_id=from_id)
        lenght = len(user_question)
        type = user_question[lenght - 1].question.type_question
        TelegramBot.deleteMessage(msg_idf)
        TelegramBot.sendPhoto(chat_id=from_id, photo=photos[type - 1])
        TelegramBot.sendMessage(chat_id=from_id,
                                text='Продовжуємо ?',
                                reply_markup=keyboard3)
    else:
        if query_data == 'button1':
            question = generete_question_by_type(Question.TYPE_DO)

        if query_data == 'button2':
            question = generete_question_by_type(Question.TYPE_AM)

        if query_data == 'button3':
            question = generete_question_by_type(Question.TYPE_IN)

        if query_data == 'more':
            user_question = UsersQuestion.objects.filter(user_id=from_id)
            lenght = len(user_question)
            type = user_question[lenght - 1].question.type_question
            question = generete_question_by_type(type)

        users_question = UsersQuestion(user_id=from_id, question=question)
        cost_question = question.cost
        word_name = get_name_for_number(cost_question)
        users_question.save()
        TelegramBot.editMessageText(msg_idf,
                                    fstring('Послуга №: {question.question_text} (+{cost_question} {word_name})')
                                    )


def generete_question_by_type(type):
    questions = Question.objects.filter(type_question=type)
    return random.choice(questions)


def get_name_for_number(number):
    morph = pymorphy2.MorphAnalyzer()
    word = morph.parse('point')[0]
    v1, v2, v3 = word.inflect({'sing', 'nomn'}), word.inflect({'gent'}), word.inflect({'plur', 'gent'})
    if number % 10 == 1 and number % 100 != 11:
        search_word = v1.word
    elif number % 10 in (2, 3, 4) and number % 100 not in (12, 13, 14):
        search_word = v2.word
    else:
        search_word = v3.word
    return search_word

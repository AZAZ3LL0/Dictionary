import telebot
from telebot import types
import openai
import json

token_gpt = ''
token = ''

bot = telebot.TeleBot(token)

termins = open("termins.txt", "r", encoding="utf-8")
termins = termins.readlines()
termins = [i.split(" : ") for i in termins]


class Copilot:

    def clear_text(self, text):
        a = text.replace("\n", " ")
        b = a.split()
        c = " ".join(b)

        return c

    def get_answer(self, question):
        prompt = question

        openai.api_key = token_gpt
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=512,
            temperature=0.5,
        )

        json_object = response

        # Convert the JSON object to a JSON string
        json_string = json.dumps(json_object)

        # Parse the JSON string using json.loads()
        parsed_json = json.loads(json_string)

        text = parsed_json['choices'][0]['text']
        cleared_text = self.clear_text(text)

        return cleared_text


copilot = Copilot()


@bot.message_handler(commands=['start'])  # создаем команду
def start(message):
    markup = types.InlineKeyboardMarkup()
    bot.send_message(message.chat.id,
                     "Привет, {0.first_name}! Введи термин, который хочешь узнать:".format(message.from_user),
                     reply_markup=markup)


@bot.message_handler(commands=['all'])  # создаем команду
def write_all_terms(message):
    markup = types.InlineKeyboardMarkup()
    a = ""
    for termin in termins:
        a += termin[0] + ";" + "\n"
    bot.send_message(message.chat.id, "Вот список терминов:\n\n" + a, reply_markup=markup)


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    flag = False
    for ticket in termins:
        if ticket[0].lower().strip() == message.text.lower().strip():
            bot.send_message(message.chat.id, ticket[0] + " - " + ticket[1])
            flag = True
    if not flag:
        print(message.text)
        opred = copilot.get_answer("Краткое определение " + message.text)
        bot.send_message(message.chat.id, opred)
        file = open("termins.txt", 'a', encoding="utf-8")
        file.write("\n" + " : ".join([message.text, opred]))
        file.close()


bot.infinity_polling(interval=0, timeout=5 * 60)

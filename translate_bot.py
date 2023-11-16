import telebot
import speech_recognition
import soundfile
import requests
import psycopg2
from googletrans import Translator, LANGUAGES
import gtts
import os

token = '6495475084:AAHxh71Zic5FydYvYLH0Oef92287-ELmIjg'
bot = telebot.TeleBot(token)

connection = psycopg2.connect(
    database = 'translate_bot',
    user = 'postgres',
    password = '123',
    host = 'localhost'
)

source_language = ''
target_language = ''

def create_buttons_language() :
    btn_markup = telebot.types.InlineKeyboardMarkup(row_width = 3)
    btn = telebot.types.InlineKeyboardButton(f'Английский {"🇬🇧"}', callback_data = 'en')
    btn2 = telebot.types.InlineKeyboardButton(f'Русский {"🇷🇺"}', callback_data = 'ru')
    btn3 = telebot.types.InlineKeyboardButton(f'Польский {"🇵🇱"}', callback_data = 'pl')
    btn4 = telebot.types.InlineKeyboardButton(f'Немецкий {"🇩🇪"}', callback_data = 'de')
    btn5 = telebot.types.InlineKeyboardButton(f'Греческий {"🇬🇷"}', callback_data = 'el')
    btn_markup.add(btn, btn2, btn3, btn4, btn5)
    return btn_markup

@bot.message_handler(content_types = ['voice'])
def translate_voice(message):
    try:
        voice_url = bot.get_file_url(message.voice.file_id)
        ogg_file_path = f'C:/Python Projects/telegram_bots/translate_bot/voices/{message.from_user.first_name}{message.message_id + 1}.ogg'
        wav_file_path = f'C:/Python Projects/telegram_bots/translate_bot/voices/{message.from_user.first_name}{message.message_id + 1}.wav'
        response = requests.get(voice_url)

        with open(ogg_file_path, 'wb') as file:
            file.write(response.content)
        
        data, samplerate = soundfile.read(ogg_file_path)

        soundfile.write(wav_file_path, data, samplerate)

        recognizer = speech_recognition.Recognizer()

        with speech_recognition.AudioFile(wav_file_path) as source:
            audio = recognizer.record(source)

        text = recognizer.recognize_google(audio, language = 'ru')
        message.text = text
        message_answer(message)

    except Exception as e:
        bot.reply_to(message, f"Ошибка: {e}")

@bot.message_handler(commands = ['set_source_language'])
def set_source_language(message):
    btn_markup = telebot.types.InlineKeyboardMarkup(row_width = 3)
    btn = telebot.types.InlineKeyboardButton('Английский', callback_data = 'en_en')
    btn2 = telebot.types.InlineKeyboardButton('Русский', callback_data = 'ru_ru')
    btn3 = telebot.types.InlineKeyboardButton('Польский', callback_data = 'pl_pl')
    btn4 = telebot.types.InlineKeyboardButton('Немецкий', callback_data = 'de_de')
    btn5 = telebot.types.InlineKeyboardButton('Греческий', callback_data = 'el_el')
    btn_markup.add(btn, btn2, btn3, btn4, btn5)
    bot.send_message(message.chat.id, 'Выбери язык на которы ВЫ будете говорить:', reply_markup = btn_markup)

@bot.message_handler(commands = ['start','choice_language'])
def command_buttons(message):
    btn_markup = create_buttons_language()
    bot.send_message(message.chat.id, 'Выбери исходный язык:', reply_markup = btn_markup)
    
@bot.callback_query_handler(func = lambda call: True)
def callback_language_buttons(call):
    global source_language, target_language
    if call.data in ['en', 'ru', 'el', 'de', 'pl']:
        source_language = call.data
        bot.send_message(call.message.chat.id, f'Исходный язык: {source_language}')
        btn_markup = telebot.types.InlineKeyboardMarkup(row_width = 3)
        btn = telebot.types.InlineKeyboardButton(f'Английский {"🇬🇧"}', callback_data = 'en_target')
        btn2 = telebot.types.InlineKeyboardButton(f'Русский {"🇷🇺"}', callback_data = 'ru_target')
        btn3 = telebot.types.InlineKeyboardButton(f'Польский {"🇵🇱"}', callback_data = 'pl_target')
        btn4 = telebot.types.InlineKeyboardButton(f'Немецкий {"🇩🇪"}', callback_data = 'de_target')
        btn5 = telebot.types.InlineKeyboardButton(f'Греческий {"🇬🇷"}', callback_data = 'el_target')
        btn_markup.add(btn, btn2, btn3, btn4, btn5)
        bot.send_message(call.message.chat.id, f'Выберите целевой язык:', reply_markup = btn_markup)
    elif call.data in ['en_target', 'ru_target', 'pl_target', 'de_target', 'el_target']:
        target_language = call.data.split('_')[0]
        bot.send_message(call.message.chat.id, f'Целевой язык: {target_language}')
        bot.send_message(call.message.chat.id, f'Отправляйте текст или голосовое сообщение, а я его переведу')

def send_voice_message(chat_id, text: str):
    tts = gtts.gTTS(text, lang = target_language)

    audio_file = "voice_message.mp3"
    tts.save(audio_file)

    with open(audio_file, "rb") as audio:
        bot.send_voice(chat_id, audio)
    
    os.remove(audio_file)


@bot.message_handler(content_types = ['text'])
def message_answer(message):
    if source_language and target_language:
        with connection.cursor() as cursor:
            cursor.execute(f"""
                INSERT INTO translations (source_text, telegram_id)
                VALUES ('{message.text}', '{message.from_user.id}')
            """)
            connection.commit()
        translator = Translator()
        translation = translator.translate(message.text, dest = target_language)
        bot.send_message(message.chat.id, f'Перевод: {translation.text}')
        send_voice_message(message.chat.id, translation.text)
    else:
        bot.send_message(message.chat.id, "Сначало выберите исходный и целевой язык! Что бы это сделать напишите /start либо /choice_language")

bot.polling(non_stop = True)

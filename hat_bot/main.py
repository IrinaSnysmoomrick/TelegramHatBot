# -*- coding: utf-8 -*-
"""
Telegram bot main code
"""

import configparser

import telebot
from telebot import apihelper
from telebot import types
from flask import Flask, request
import logging
import os

from hat_bot.hat_game_container import HatGameContainer


def main():
    config = configparser.ConfigParser()
    config.sections()
    BOT_CONFIG_FILE = 'bot.conf'
    config.read(BOT_CONFIG_FILE)
    TOKEN = config['DEFAULT']['TOKEN']
    PROXY = config['DEFAULT']['PROXY_URL']
    
    apihelper.proxy = {'https': PROXY}
    bot = telebot.TeleBot(TOKEN) 
            
    game_container = HatGameContainer()
    logging.basicConfig(filename='game_log.txt',level=logging.INFO, format='%(asctime)s %(message)s')

    """Try to put code for buttons there"""

    markup = types.ReplyKeyboardMarkup()
    start_game = types.KeyboardButton('Начать игру')
    round = types.KeyboardButton('Новый раунд')
    registration = types.KeyboardButton('Зарегистрироваться на игру')
    result = types.KeyboardButton('Результат игры')
    get_word = types.KeyboardButton('Вытащить слово')
    put_word = types.KeyboardButton('Добавить слово')
    finish = types.KeyboardButton('Завершить игру')

    markupStartGame = types.ReplyKeyboardMarkup()
    markupStartGame.add(start_game, registration)

    markupRegistration = types.ReplyKeyboardMarkup()
    markupRegistration.add(registration)

    markupAfterRegistration = types.ReplyKeyboardMarkup()
    markupAfterRegistration.add(round, put_word)

    markupRunGame = types.ReplyKeyboardMarkup()
    markupRunGame.add(get_word, result)

    markupEndRound = types.ReplyKeyboardMarkup()
    markupEndRound.add(round, result)

    markupFinishGame = types.ReplyKeyboardMarkup()
    markupFinishGame.add(result, finish)

    # if user_game is None:
    #     bot.send_message(user_id, 'Создать игру', reply_markup=markupStartGame, parse_mode='markdown')
    # elif user_game.status == 1:
    #     bot.send_message(user_id, 'Зарегистрироваться на игру', reply_markup=markupRegistration, parse_mode='markdown')
    # elif user_game.status > 1 and user_game.status < 5:
    #     bot.send_message(user_id, 'Участвовать в игре', reply_markup=markupRunGame, parse_mode='markdown')
    # elif user_game.status == 5:
    #     bot.send_message(user_id, 'Завершить игру', reply_markup=markupFinishGame, parse_mode='markdown')
    # else:
    #     bot.send_message(user_id, 'Выход', reply_markup=markupFinishGame, parse_mode='markdown')

    @bot.message_handler(commands=['start'])
    def start_game_command(message):
        markup.add(start_game, registration)
        bot.send_message(message.chat.id, '''Играем в шляпу!''', reply_markup=markupStartGame, parse_mode='markdown')

    @bot.message_handler(commands=['help'])
    def help_game(message):
        bot.send_message(message.from_user.id, 'http://thehat.ru/rules/')

    @bot.message_handler(content_types=['text'])
    def get_text_message(message):
        user_id = message.from_user.id
        #Если игрок еще не участвует ни в одной игре, то в user_game вернется пустая игра
        user_game = game_container.get_user_game(user_id)
        user_name = message.from_user.first_name

        try:
            if message.text == 'Начать игру':
                bot.send_message(user_id, 'Поехали! Сколько человек будет в каждой команде?')
                logging.info(f'{user_id} - {user_name} start a game')
                bot.register_next_step_handler(message, get_team_size)
            elif message.text == 'Зарегистрироваться на игру':
                bot.send_message(user_id, 'Введите номер игры.')
                logging.info(f'{user_id} - {user_name} registration on a game')
                bot.register_next_step_handler(message, game_registration)
            elif message.text == 'Новый раунд':
                logging.info(f'{user_id} - {user_name} start a new round')
                players = game_container.get_game_players(user_game.game_number)
                s = user_game.start_new_round()
                if user_game.status < 2:
                    bot.send_message(user_id, s, reply_markup=markupAfterRegistration, parse_mode='markdown')
                else:
                    for p in players:
                        if s == 'Конец игры':
                            bot.send_message(p, s, reply_markup=markupFinishGame, parse_mode='markdown')
                        else:
                            bot.send_message(p, s, reply_markup=markupRunGame, parse_mode='markdown')
            elif message.text == 'Результат игры':
                logging.info(f'{user_id} - {user_name} get the result of the game')
                if user_game.status < 4:
                    bot.send_message(user_id, user_game.get_result(), reply_markup=markupEndRound, parse_mode='markdown')
                else:
                    players = game_container.get_game_players(user_game.game_number)
                    for p in players:
                        bot.send_message(p, user_game.get_result(), reply_markup=markupFinishGame, parse_mode='markdown')
            elif message.text == 'Добавить слово':
                logging.info(f'{user_id} - {user_name} adding a new word')
                bot.send_message(user_id, 'Введите слово')
                bot.register_next_step_handler(message, put_word_method)
            elif message.text == 'Вытащить слово':
                logging.info(f'{user_id} - {user_name} get a word from the game word list')
                team_number = user_game.get_team_number(user_id)
                word = user_game.get_word()
                if word is None:
                    players = game_container.get_game_players(user_game.game_number)
                    for p in players:
                        bot.send_message(p, 'Слова закончились.', reply_markup=markupEndRound, parse_mode='markdown')
                else:
                    keyboard = types.InlineKeyboardMarkup(row_width=2)
                    key_ok = types.InlineKeyboardButton(text='+', callback_data=f'{word}:yes:{user_id}:{team_number}')
                    key_cancel = types.InlineKeyboardButton(text='-', callback_data=f'{word}:no:{user_id}:{team_number}')
                    keyboard.add(key_ok, key_cancel)
                    bot.send_message(user_id, word, reply_markup=keyboard)
            elif message.text == 'Завершить игру':
                logging.info(f'{user_id} - {user_name} finish the game {user_game.game_number}')
                players = game_container.get_game_players(user_game.game_number)
                for p in players:
                    bot.send_message(p, 'Игра завершена', reply_markup=markupStartGame, parse_mode='markdown')
                game_container.finish_game(user_id)

        except Exception as exc:
            logging.error(f'{user_id} - {user_name} unexpected error happened')
            if user_game is None:
                bot.send_message(user_id, 'Неправильный порядок действий', reply_markup=markupStartGame, parse_mode='markdown')
            elif user_game.status == 1:
                bot.send_message(user_id, 'Неправильный порядок действий', reply_markup=markupAfterRegistration, parse_mode='markdown')
            elif user_game.status == 2:
                bot.send_message(user_id, 'Неправильный порядок действий', reply_markup=markupRunGame, parse_mode='markdown')
            elif user_game.status > 2 and user_game.status < 5:
                bot.send_message(user_id, 'Неправильный порядок действий', reply_markup=markupEndRound, parse_mode='markdown')
            elif user_game.status == 5:
                bot.send_message(user_id, 'Неправильный порядок действий', reply_markup=markupFinishGame, parse_mode='markdown')

    #количество участников в каждой команде
    def get_team_size(message):
        try:
            team_size = int(message.text)
            game_number = game_container.start_new_game(team_size)
            bot.send_message(message.from_user.id, f'Отлично! Игра номер {game_number}, по {team_size} участников в команде.', reply_markup=markupRegistration, parse_mode='markdown');
            logging.info(f'{message.from_user.id} - {message.from_user.first_name} created a new game with number {game_number}')
        except ValueError:
            bot.send_message(message.from_user.id, 'Цифрами, пожалуйста.')
        #except:
        #    bot.send_message(message.from_user.id, 'Неправильный порядок действий при указании количества игроков.', reply_markup=markupStartGame, parse_mode='markdown')


    def game_registration(message):
        try:
            game_number = int(message.text)
        except ValueError:
            bot.send_message(message.from_user.id, 'Некорректный номер игры.', reply_markup=markupStartGame, parse_mode='markdown')
            logging.error(f'{message.from_user.id} - {message.from_user.first_name} incorrect game number during registration process')
        try:
            game_number = int(message.text)
            game_container.reg_player(message.from_user.id, game_number, message.from_user.first_name)
            markup = types.ReplyKeyboardMarkup()
            markup.add(round, put_word)
            bot.send_message(message.from_user.id, 'Участник успешно добавлен в игру!', reply_markup=markupAfterRegistration, parse_mode='markdown')
            logging.info(f'{message.from_user.id} - {message.from_user.first_name} registered to the game {game_number}')
        except:
            bot.send_message(message.from_user.id, 'Неправильный порядок действий', reply_markup=markupStartGame,parse_mode='markdown')
            logging.error(f'{message.from_user.id} - {message.from_user.first_name} unexpected error during registration process')

    @bot.callback_query_handler(func=lambda call: True)
    def callback_worker(call):
        w, d, chat_id, team_number = call.data.split(':')
        user_game = game_container.get_user_game(call.from_user.id)
        if d == 'yes':
            user_game.check_word(w,True, int(team_number))
        elif d == 'no':
            user_game.check_word(w,False, int(team_number))
        bot.send_message(chat_id, 'Next')

    def put_word_method(message):
        try:
            user_game = game_container.get_user_game(message.from_user.id)
            bot.send_message(message.from_user.id, user_game.add_word(message.text), reply_markup=markupAfterRegistration, parse_mode='markdown')
            logging.info(f'{message.from_user.id} - {message.from_user.first_name} put a word {message.text} into a list of words for {user_game.game_number}')
        except:
            bot.send_message(message.from_user.id, 'Что-то пошло не так.', reply_markup=markupAfterRegistration, parse_mode='markdown')
            logging.error(f'{message.from_user.id} - {message.from_user.first_name} unexpected error during adding a new word')

    if "HEROKU" in list(os.environ.keys()):
        logger = telebot.logger
        telebot.logger.setLevel(logging.INFO)

        server = Flask(__name__)

        @server.route("/bot", methods=['POST'])
        def getMessage():
            bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
            return "!", 200

        @server.route("/")
        def webhook():
            bot.remove_webhook()
            bot.set_webhook(
                url="https://min-gallows.herokuapp.com/bot")  # этот url нужно заменить на url вашего Хероку приложения
            return "?", 200

        server.run(host="0.0.0.0", port=os.environ.get('PORT', 80))
    else:
        # если переменной окружения HEROKU нету, значит это запуск с машины разработчика.
        # Удаляем вебхук на всякий случай, и запускаем с обычным поллингом.
        bot.remove_webhook()
        bot.polling(none_stop=True)

if __name__ == '__main__':
    main()
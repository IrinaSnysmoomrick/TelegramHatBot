# -*- coding: utf-8 -*-
"""
Telegram bot main code
"""

import configparser

import telebot
from telebot import apihelper
from telebot import types

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

    @bot.message_handler(content_types=['text'])
    def get_text_message(message):
        user_id = message.from_user.id
        user_game = game_container.get_user_game(user_id)

        try:
            if message.text == '/start':
                #bot.send_message(user_id, game_container.get_help())
                markup.add(start_game, registration)
                bot.send_message(message.chat.id, '''Играем в шляпу!''', reply_markup=markupStartGame, parse_mode='markdown')
            elif message.text == '/help':
                bot.send_message(user_id, 'http://thehat.ru/rules/')
            elif message.text == 'Начать игру':
                bot.send_message(user_id, 'Поехали! Сколько человек будет в каждой команде?')
                bot.register_next_step_handler(message, get_team_size)
            elif message.text == 'Зарегистрироваться на игру':
                bot.send_message(user_id, 'Введите номер игры.')
                bot.register_next_step_handler(message, game_registration)
            elif message.text == 'Новый раунд':
                players = game_container.get_game_players(user_game.game_number)
                s = user_game.start_new_round()
                for p in players:
                    if s == 'Конец игры':
                        bot.send_message(p, s, reply_markup=markupFinishGame, parse_mode='markdown')
                    else:
                        bot.send_message(p, s, reply_markup=markupRunGame, parse_mode='markdown')
            elif message.text == 'Результат игры':
                if user_game.status < 4:
                    bot.send_message(user_id, user_game.get_result(), reply_markup=markupEndRound, parse_mode='markdown')
                else:
                    players = game_container.get_game_players(user_game.game_number)
                    for p in players:
                        bot.send_message(p, user_game.get_result(), reply_markup=markupFinishGame, parse_mode='markdown')
            elif message.text == 'Добавить слово':
                bot.send_message(user_id, 'Введите слово')
                bot.register_next_step_handler(message, put_word_method)
            elif message.text == 'Вытащить слово':
                team_number = user_game.get_team_number(user_id)#int(message.text)
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
                    #TODO - что здесь надо выводить в сообщении?
                    #bot.send_message(user_id, word, reply_markup=markupRunGame, parse_mode='markdown')
            elif message.text == 'Завершить игру':
                players = game_container.get_game_players(user_game.game_number)
                for p in players:
                    bot.send_message(p, 'Игра завершена', reply_markup=markupStartGame, parse_mode='markdown')
                game_container.finish_game(user_id)
            else:
                if message.text.isdigit():
                    game_registration(message)
                else:
                    put_word_method(message)
        except ValueError as err:
            bot.send_message(user_id, err)


    def get_team_size(message): #количество команд
        try:
            team_size = int(message.text)
        except:
            bot.send_message(message.from_user.id, 'Цифрами, пожалуйста.');
        game_number = game_container.start_new_game(team_size)
        bot.send_message(message.from_user.id, f'Отлично! Игра номер {game_number}, по {team_size} участников в команде.', reply_markup=markupRegistration, parse_mode='markdown');


    def game_registration(message):
        try:
            game_number = int(message.text)
        except:
            bot.send_message(message.from_user.id, 'Некорректный номер игры.', reply_markup=markupStartGame, parse_mode='markdown')
        try:
            game_container.reg_player(message.from_user.id, game_number, message.from_user.first_name)
            markup = types.ReplyKeyboardMarkup()
            markup.add(round, put_word)
            bot.send_message(message.from_user.id, 'Участник успешно добавлен в игру!', reply_markup=markupAfterRegistration, parse_mode='markdown')
        except ValueError as err:
            bot.send_message(message.from_user.id, err, reply_markup=markupAfterRegistration,parse_mode='markdown')

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
        user_game = game_container.get_user_game(message.from_user.id)
        bot.send_message(message.from_user.id, user_game.add_word(message.text), reply_markup=markupAfterRegistration, parse_mode='markdown')

    bot.polling(none_stop=True, interval=0)

if __name__ == '__main__':
    main()
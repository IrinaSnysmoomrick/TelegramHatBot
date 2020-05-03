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

    @bot.message_handler(content_types=['text'])
    def get_text_message(message):
        user_id = message.from_user.id
        user_game = game_container.get_user_game(user_id)

        try:
            if message.text == '/start':
                bot.send_message(user_id, user_game.get_help())
            elif message.text == "/start_game":
                bot.send_message(user_id, 'Поехали! Сколько человек будет в каждой команде?')
                bot.register_next_step_handler(message, get_team_size);
            elif message.text == '/help':
                bot.send_message(user_id, game_container.get_help())
            elif '/reg' in message.text:
                try:
                    _, i = message.text.split(' ')
                except:
                    bot.send_message(user_id, 'Не указан номер игры.')
                game_n = int(i)
                game_container.reg_player(user_id, game_n, message.from_user.first_name)
                bot.send_message(user_id, 'Участник добавлен в игру!')
            elif message.text == '/round':
                bot.send_message(user_id, user_game.start_new_round())
            elif message.text == '/result':
                bot.send_message(user_id, user_game.get_result())
            elif message.text.isdigit():
                team_number = int(message.text)
                word = user_game.get_word()
                if word is None:
                    bot.send_message(user_id, 'Слова закончились.')
                else:
                    keyboard = types.InlineKeyboardMarkup(row_width=2)
                    key_ok = types.InlineKeyboardButton(text='+', callback_data=f'{word}:yes:{user_id}:{team_number}')
                    key_cancel = types.InlineKeyboardButton(text='-', callback_data=f'{word}:no:{user_id}:{team_number}')
                    keyboard.add(key_ok, key_cancel)
                    bot.send_message(user_id, word, reply_markup=keyboard)
            else:
                bot.send_message(user_id, user_game.add_word(message.text))
        except ValueError as err:
            bot.send_message(user_id, err)


    def get_team_size(message): #количество команд
        try:
            team_size = int(message.text)
        except:
            bot.send_message(message.from_user.id, 'Цифрами, пожалуйста.');
        game_number = game_container.start_new_game(team_size)
        bot.send_message(message.from_user.id, f'Отлично! Игра номер {game_number}, по {team_size} участников в команде.');


    @bot.callback_query_handler(func=lambda call: True)
    def callback_worker(call):
        w, d, chat_id, team_number = call.data.split(':')
        user_game = game_container.get_user_game(call.from_user.id)
        if d == 'yes':
            user_game.check_word(w,True, int(team_number))
        elif d == 'no':
            user_game.check_word(w,False, int(team_number))
        bot.send_message(chat_id, 'Next')

    
    bot.polling(none_stop=True, interval=0)

if __name__ == '__main__':
    main()
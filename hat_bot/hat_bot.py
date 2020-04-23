# -*- coding: utf-8 -*-
"""
Редактор Spyder

Это временный скриптовый файл.
"""

import telebot
from telebot import apihelper
from telebot import types
import random


class HatBot:
    
    def __init__(self):
        """Constructor"""
        self.words = []
        self.used_words = []
        self.teams={}
        self.teams_cnt = 0
        
    def add_word(self, word):
        """Adding a new word into the word list"""
        self.words.append(word)
    
    def get_word(self):
        """Getting a word from word list and put it into list of used words"""
        if not self.words:
            return None
        else:
            w = self.words.pop(random.randint(0, len(self.words) - 1))
            return w
        
    def check_word(self, word, is_ok, team_number = 0):
        print(team_number)
        if is_ok:
            self.teams[team_number] += 1
            self.used_words.append(word)
        else:
            self.words.append(word)
            
    
    def start_new_round(self):
        """Start new rownd - exchange values from list of used words to word list"""
        self.words = self.used_words
        self.used_words = []
    
    def start_new_game(self):
        """Start new game, reset lists"""
        self.words = []
        self.used_words = []
        self.teams = {i+1: 0 for i in range(self.teams_cnt)}
        print(self.teams_cnt)
        print(self.teams)
        
    
def main():
    apihelper.proxy = {'https':'socks5h://svf:Railroadranger1@fedorov.cf:1080'} 
    
    bot = telebot.TeleBot('1099016441:AAHM0pvg9Oa6RyZ-P20gF98XljhgTzVEJMY')       
    
    hat_game = HatBot()
        
    
    @bot.message_handler(content_types=['text'])
    def get_text_message(message):
        if message.text == "/start": 
            bot.send_message(message.from_user.id, 'Поехали! Сколько будет команд?')
            bot.register_next_step_handler(message, get_teams_cnt);
        elif message.text == '/round':
            hat_game.start_new_round()
            bot.send_message(message.from_user.id, 'Новый раунд')
        elif message.text.isdigit():# == '1':
            team_number = int(message.text)
            word = hat_game.get_word() 
            if word is None:
                bot.send_message(message.from_user.id, 'Слова закончились')                             
            else:
                keyboard = types.InlineKeyboardMarkup(row_width=2)
                key_ok = types.InlineKeyboardButton(text='+', callback_data=f'{word}:yes:{message.from_user.id}:{team_number}')
                key_cancel = types.InlineKeyboardButton(text='-', callback_data=f'{word}:no:{message.from_user.id}:{team_number}')
                keyboard.add(key_ok, key_cancel)
                bot.send_message(message.from_user.id, word, reply_markup=keyboard)
        else:
            hat_game.add_word(message.text)
            bot.send_message(message.from_user.id, 'Слово успешно добавлено')
        print(hat_game.words)
        print(hat_game.used_words)
 

    def get_teams_cnt(message): #количество команд
        try:
            hat_game.teams_cnt = int(message.text)
        except:
            bot.send_message(message.from_user.id, 'Цифрами, пожалуйста');
        bot.send_message(message.from_user.id, f'Играет {hat_game.teams_cnt} команд');  
        hat_game.start_new_game()

        
    @bot.callback_query_handler(func=lambda call: True)
    def callback_worker(call):
        w, d, chat_id, team_number = call.data.split(':')
        print(team_number)
        if d == 'yes':
            hat_game.check_word(w,True, int(team_number))
        elif d == 'no':
            hat_game.check_word(w,False)
        bot.send_message(chat_id, 'Next')
        print(hat_game.words)
        print(hat_game.used_words)

    
    bot.polling(none_stop=True, interval=0)

if __name__ == '__main__':
    main()
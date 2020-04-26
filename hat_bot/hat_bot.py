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
        self.teams = {}
        self.team_members = {}
        self.members = []
        self.member_cnt = 0
        self.game_number = 0
        
    def start_new_game(self):
        """Start new game, reset lists"""
        self.words = []
        self.used_words = []
        self.game_number = random.randint(1,1000)
        
    def reg_member(self, user_name):
        if user_name in self.members:
            return 'Участник уже добавлен в игру!'
        else:
            self.members.append(user_name)
            return 'Участник добавлен в игру!'
        
    def start_new_round(self):
        """Start new rownd - exchange values from list of used words to word list"""
        #если список команд не сформирован, то сформировать
        #и это первый раунд, оправить каждому участнику номер его команды
        #если это не первый раунд, то перенести список слов из использованных в общий
        if len(self.used_words) > 0:
            self.words = self.used_words
            self.used_words = []
        if len(self.members) == 0:
            return 'Нет зарегистрированных участников игры.'
        elif len(self.team_members) == 0:
            return(self.get_teams())
            
    def get_teams(self):
        #self.member_cnt
        #посчитаем количество зарегистрированных участников
        random.shuffle(self.members)
        cnt = len(self.members)
        for i in range(0, cnt, self.member_cnt):
            self.team_members[i+1] = self.members[i:i + self.member_cnt]
        s = ''
        for key, value in self.team_members.items():
            s += 'Команда ' + str(key) + ': ' + str(value) + '\n'
            self.teams[key] = 0
        return s        
        
    def add_word(self, word):
        """Adding a new word into the word list"""
        if word in self.words:
            return 'Такое слово уже есть в шляпе'
        else:
            self.words.append(word)
            return 'Слово успешно добавлено'
    
    def get_word(self):
        """Getting a word from word list and put it into list of used words"""
        if not self.words:
            return None
        else:
            w = self.words.pop(random.randint(0, len(self.words) - 1))
            return w
        
    def check_word(self, word, is_ok, team_number = 0):
        if is_ok:
            self.teams[team_number] += 1
            self.used_words.append(word)
        else:
            self.words.append(word)
            
    def get_result(self):
        s = ''
        for key, value in self.teams.items():
            s += 'команда ' + str(key) + ' - ' + str(value) + ' очков' + '\n'  
        return s
    
    def get_help(self):
        return ("Доступные команды:\n"
                "/start_game - начать новую игру. Бот пришлет вам номер начатой игры\n"
                "/reg game_number - заявить об участии в игре, где game_number - номер, полученный при выполнении команды start_game\n"
                "/round - начать разыгрывать слова из ""шляпы""\n"
                "/result - подвести итоги игры\n"
                "любое слово не из списка команд, будет добавлено в ""шляпу""\n"
                "отправить число = номеру команды - вытянуть слово из ""шляпы"""
                )
        
    
def main():
    apihelper.proxy = {} 
    
    bot = telebot.TeleBot()       
    
    hat_game = HatBot()
            
    
    @bot.message_handler(content_types=['text'])
    def get_text_message(message):
        if message.text == "/start_game": 
            bot.send_message(message.from_user.id, 'Поехали! Сколько человек будет в каждой команде?')
            bot.register_next_step_handler(message, get_members_cnt);
        elif message.text == '/help':
            bot.send_message(message.from_user.id, hat_game.get_help())
        elif '/reg' in message.text:
            _, i = message.text.split(' ')
            bot.send_message(message.from_user.id, hat_game.reg_member(message.from_user.first_name))
        elif message.text == '/round':
            bot.send_message(message.from_user.id, hat_game.start_new_round())
        elif message.text == '/result':
            bot.send_message(message.from_user.id, hat_game.get_result())
        elif message.text.isdigit():
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
            bot.send_message(message.from_user.id, hat_game.add_word(message.text))
 

    def get_members_cnt(message): #количество команд
        try:
            hat_game.member_cnt = int(message.text)
        except:
            bot.send_message(message.from_user.id, 'Цифрами, пожалуйста');
        hat_game.start_new_game()
        bot.send_message(message.from_user.id, f'Отлично! Игра номер {hat_game.game_number}, по {hat_game.member_cnt} участников в команде');  

        
    @bot.callback_query_handler(func=lambda call: True)
    def callback_worker(call):
        w, d, chat_id, team_number = call.data.split(':')
        print(team_number)
        if d == 'yes':
            hat_game.check_word(w,True, int(team_number))
        elif d == 'no':
            hat_game.check_word(w,False, int(team_number))
        bot.send_message(chat_id, 'Next')

    
    bot.polling(none_stop=True, interval=0)

if __name__ == '__main__':
    main()
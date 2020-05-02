# -*- coding: utf-8 -*-
"""

"""

import telebot
from telebot import apihelper
from telebot import types
import random
import configparser


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
        l = []
        for i in range(0, cnt - 1, self.member_cnt):
            #print(l)
            if cnt - i == self.member_cnt + 1:
                l.append(self.members[i:i + self.member_cnt + 1])
            else:
                l.append(self.members[i:i + self.member_cnt])
        self.team_members = dict((i+1,j) for i, j in enumerate(l))
        #self.team_members = dict((i+1,j) for i,j in enumerate(l))
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
        print('inside the method')
        print(self)
        print(self.teams)
        print(self.teams[team_number])
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
    
    hat_game = HatBot()
    
    #dictionary with running games
    #key - game_number, values - game object
    games = {}
    
    #dictionary for connection players and games
    #pair - key - user_id, values - game_number
    game_players = {}
    
    user_game = HatBot()
    
    config = configparser.ConfigParser()
    config.sections()
    BOT_CONFIG_FILE = 'bot.conf'
    config.read(BOT_CONFIG_FILE)
    TOKEN = config['DEFAULT']['TOKEN']
    PROXY = config['DEFAULT']['PROXY_URL']
    
    apihelper.proxy = {'https': PROXY} 
    
    bot = telebot.TeleBot(TOKEN) 
            
    
    @bot.message_handler(content_types=['text'])
    def get_text_message(message):
        #when user send a message, we get a link between user and game
        #TODO - connection should be via unique identifier, not just first name
        user_id = message.from_user.id

        user_game = get_user_game(user_id)
        if message.text == '/start':
            bot.send_message(user_id, hat_game.get_help())
        elif message.text == "/start_game": 
            bot.send_message(user_id, 'Поехали! Сколько человек будет в каждой команде?')
            game_number = bot.register_next_step_handler(message, get_members_cnt);
            # make link between player and his/her game
        elif message.text == '/help':
            bot.send_message(user_id, hat_game.get_help())
        elif '/reg' in message.text:
            _, i = message.text.split(' ')
            game_n = int(i)
            # if the user is not in a list of any games, get game number from the message and 
            # create a connection between the user and the game
            if user_id not in game_players.keys():
                game_players[user_id] = game_n
                user_game = games[game_n]
            bot.send_message(message.from_user.id, user_game.reg_member(message.from_user.first_name))
        elif message.text == '/round':
            # here we assume that user has already registered to a game
            # TODO - make a try-catch block here to avoid situations when 
            # random user tryes to run the command without registration to any game
            bot.send_message(message.from_user.id, user_game.start_new_round())
            print(user_game.teams)
        elif message.text == '/result':
            bot.send_message(message.from_user.id, user_game.get_result())
        elif message.text.isdigit():
            team_number = int(message.text)
            word = user_game.get_word() 
            if word is None:
                bot.send_message(message.from_user.id, 'Слова закончились')                             
            else:
                keyboard = types.InlineKeyboardMarkup(row_width=2)
                key_ok = types.InlineKeyboardButton(text='+', callback_data=f'{word}:yes:{user_id}:{team_number}')
                key_cancel = types.InlineKeyboardButton(text='-', callback_data=f'{word}:no:{user_id}:{team_number}')
                keyboard.add(key_ok, key_cancel)
                bot.send_message(user_id, word, reply_markup=keyboard)
                print('in main code')
                print(user_game)
                print(user_game.teams)
        else:
            bot.send_message(message.from_user.id, user_game.add_word(message.text))
 

    def get_members_cnt(message): #количество команд
        try:
            member_cnt = int(message.text)
        except:
            bot.send_message(message.from_user.id, 'Цифрами, пожалуйста');
        new_game = HatBot()
        new_game.member_cnt = member_cnt
        new_game.start_new_game()
        # add a new game into the list of running games
        games[new_game.game_number] = new_game
        bot.send_message(message.from_user.id, f'Отлично! Игра номер {new_game.game_number}, по {new_game.member_cnt} участников в команде');  
        #game_players[message.from_user.id] = new_game.game_number
        # TODO can we do this a such way?
        return new_game.game_number

    # TODO - now we don't get a value for user_game. check which steps I skept - adding into games or
    # game_players dictionariess
    def get_user_game(user_id):
        print(user_id)
        print(game_players)
        if user_id in game_players.keys():
            print('user_id in game_players')
            user_game_number = game_players.get(user_id)
            return games[user_game_number]


    @bot.callback_query_handler(func=lambda call: True)
    def callback_worker(call):
        w, d, chat_id, team_number = call.data.split(':')
        print('user_id output')
        print(call)
        user_game = get_user_game(call.from_user.id)
        print('callback_worker')
        print(user_game)
        print(user_game.teams)
        if d == 'yes':
            user_game.check_word(w,True, int(team_number))
        elif d == 'no':
            user_game.check_word(w,False, int(team_number))
        bot.send_message(chat_id, 'Next')

    
    bot.polling(none_stop=True, interval=0)

if __name__ == '__main__':
    main()
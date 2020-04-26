# -*- coding: utf-8 -*-
"""
Created on Sat Apr 18 20:56:48 2020

@author: Sergey Fedorov
"""

import sys
sys.path.append('..')
from hat_bot.hat_bot import HatBot


test_hat_bot = HatBot()

def test_start_new_game(n):
    #присваивание номера игры	
	#вопрос - сколько игроков в команде?
    game_number = test_hat_bot.start_new_game(n)
    assert(game_number, None)
    
def test_registration(n, gamer_name):
    #регистрация участников:
	#добавление игроков в общий список. Номер игры + список логинов    
    test_hat_bot.gamer_registration(n, gamer_name)
    #проверяем, есть ли указанный геймер нейм в списке логинов
    u = test_hat_bot.members[n]
    assert(gamer_name in u)
    
def test_new_round():
    #начало игрового раунда:      
	#если список команд не сформирован, то сформировать
	#если это не первый раунд, то перенести список слов из использованных в общий 
    test_hat_bot.start_new_round()
    cnt = len(test_hat_bot.team_members) > 0
    assert(cnt, True)

#def test_get_team_number(gamer_name):    
    #получить номер команды по имени пользователя


def test_add_word():
    test_hat_bot.add_word('word')
    l = ('word' in test_hat_bot.words)
    assert(l, True)
    
def test_get_word():
    test_hat_bot.start_new_game()
    test_hat_bot.add_word('word')
    w = test_hat_bot.get_word()
    assert(w, 'word')    
    
    
if __name__ == '__main__':

    test_get_word()  
    
    
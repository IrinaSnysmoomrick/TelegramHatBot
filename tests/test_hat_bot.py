# -*- coding: utf-8 -*-
"""
Created on Sat Apr 18 20:56:48 2020

@author: Sergey Fedorov
"""

import sys
sys.path.append('..')
from hat_bot.main import HatGame


def test_start_new_game():
    """Initialize new game"""
    test_hat_bot = HatGame()
    test_hat_bot.start_new_game()
    assert test_hat_bot.game_number > 0
    assert len(test_hat_bot.words) == 0
    assert len(test_hat_bot.round_words) == 0
    assert len(test_hat_bot.teams) == 0
    assert len(test_hat_bot.members) == 0 
    assert len(test_hat_bot.team_members) == 0
    
    
def test_registration():
    """A new player registration"""
    test_hat_bot = HatGame()
    test_hat_bot.start_new_game()
    gamer_name = "User1"
    test_hat_bot.reg_member(gamer_name)
    assert len(test_hat_bot.members) == 1
    assert gamer_name in test_hat_bot.members
    

def test_add_word():
    """Adding a new word into the game"""
    test_hat_bot = HatGame()
    test_hat_bot.start_new_game()
    s = test_hat_bot.add_word("word1")
    assert s, "Слово успешно добавлено"
    s = test_hat_bot.add_word("word2")
    assert s == "Слово успешно добавлено"
    assert len(test_hat_bot.words) == 2
    assert ('word1' in test_hat_bot.words) == True
    assert ('word2' in test_hat_bot.words) == True
    s = test_hat_bot.add_word("word1")
    assert s == "Такое слово уже есть в шляпе"
    
    
def test_get_teams():
    """Division participants into teams"""    
    test_hat_bot = HatGame()
    test_hat_bot.team_size = 2
    test_hat_bot.start_new_game()
    test_hat_bot.reg_member("User1")
    test_hat_bot.reg_member("User2")
    test_hat_bot.reg_member("User3")
    test_hat_bot.reg_member("User4")
    test_hat_bot.reg_member("User5")
    test_hat_bot.get_teams()
    assert len(test_hat_bot.team_members) == 2
    assert len(test_hat_bot.team_members[1]) == 2
    assert len(test_hat_bot.team_members[2]) == 3   
    assert len(test_hat_bot.teams) == 2

    
def test_new_round():
    """Start new game round"""
    test_hat_bot = HatGame()
    test_hat_bot.team_size = 2
    test_hat_bot.start_new_game()
    test_hat_bot.reg_member("User1")
    test_hat_bot.reg_member("User2")
    test_hat_bot.reg_member("User3")
    test_hat_bot.reg_member("User4")
    test_hat_bot.reg_member("User5")
    test_hat_bot.add_word("word1")    
    test_hat_bot.start_new_round
    assert len(test_hat_bot.team_members) == 2
    assert len(test_hat_bot.words) == 1
    assert len(test_hat_bot.round_words) == 0
    assert len(test_hat_bot.teams) == 2

    
def test_get_word():
    test_hat_bot = HatGame()
    test_hat_bot.add_word('word')
    w = test_hat_bot.get_word()
    assert w == 'word'
    w = test_hat_bot.get_word()
    assert w is None
    
def test_check_word():
    test_hat_bot = HatGame()
    test_hat_bot.start_new_game()
    test_hat_bot.reg_member("User1")
    test_hat_bot.reg_member("User2")
    test_hat_bot.reg_member("User3")
    test_hat_bot.reg_member("User4")
    test_hat_bot.team_size = 1
    test_hat_bot.add_word("word1")
    test_hat_bot.add_word('word2')
    test_hat_bot.start_new_round
    # обработать ошибку: member_cnt < 2
    
def test_check_word():
    test_hat_bot = HatGame()
    test_hat_bot.start_new_game()
    test_hat_bot.reg_member("User1")
    test_hat_bot.reg_member("User2")
    test_hat_bot.reg_member("User3")
    test_hat_bot.reg_member("User4")
    test_hat_bot.team_size = 2
    test_hat_bot.add_word("word1")
    test_hat_bot.add_word('word2')
    test_hat_bot.start_new_round
    w = test_hat_bot.get_word()
    test_hat_bot.check_word(w, True, 1)
    assert len(test_hat_bot.words) == 1
    assert len(test_hat_bot.round_words) == 1
    assert test_hat_bot.teams[1] == 1
    
    w = test_hat_bot.get_word()
    test_hat_bot.check_word(w, False, 1)
    assert len(test_hat_bot.words) == 1
    assert len(test_hat_bot.round_words) == 1
    assert test_hat_bot.teams[1] == 1
    
    w = test_hat_bot.get_word()
    test_hat_bot.check_word(w, True, 2)
    assert len(test_hat_bot.words) == 0
    assert len(test_hat_bot.round_words) == 2
    assert test_hat_bot.teams[2] == 1   
    
    w = test_hat_bot.get_word()
    assert w is None
    
    
if __name__ == '__main__':

    test_get_word()  
    
    
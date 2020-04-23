# -*- coding: utf-8 -*-
"""
Created on Sat Apr 18 20:56:48 2020

@author: Sergey Fedorov
"""

import sys
sys.path.append('..')
from hat_bot.hat_bot import HatBot


test_hat_bot = HatBot()

def test_start_new_game():
    test_hat_bot.start_new_game()
    w = test_hat_bot.get_word()
    assert(w, None)

def test_add_word():
    test_hat_bot.add_word('word')
    
def test_get_word():
    test_hat_bot.start_new_game()
    test_hat_bot.add_word('word')
    w = test_hat_bot.get_word()
    assert(w, 'word')    
    
    
if __name__ == '__main__':

    test_get_word()  
    
    
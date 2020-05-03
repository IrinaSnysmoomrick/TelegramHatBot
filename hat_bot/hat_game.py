"""
Hat Game class
"""
import random


class HatGame:

    def __init__(self):
        """Constructor"""
        self.words = []
        self.round_words = []
        self.teams = {}
        self.team_members = {}
        self.members = []
        self.team_size = 0
        self.game_number = random.randint(1,1000)
        self.statuses = {1:'Старт', 2:'Раунд 1', 3:'Раунд 2', 4:'Раунд 3', 5:'Конец игры'}
        self.status = 1

    def reg_member(self, user_name):
        """Registration a user into game"""
        if user_name in self.members:
            raise ValueError('Участник уже добавлен в игру.')
        else:
            self.members.append(user_name)
            return 'Участник добавлен в игру!'

    def start_new_round(self):
        """Start new rownd - exchange values from list of used words to word list"""
        self.round_words = self.words
        if len(self.members) == 0:
            raise ValueError('Нет зарегистрированных участников игры.')
        elif self.status > 4:
            raise ValueError('Все раунды игры уже пройдены.')
        elif len(self.team_members) == 0:
            teams = (self.get_teams())
            self.status += 1
            return f'{self.statuses[self.status]}\n{teams}'
        else:
            self.status += 1
            return str(self.statuses[self.status])

    def get_teams(self):
        """Split up all game members into teams"""
        random.shuffle(self.members)
        cnt = len(self.members)
        l = []
        if cnt < 2:
            raise ValueError('На игру зарегистрировалось меньше 2 человек.')
        for i in range(0, cnt - 1, self.team_size):
            if cnt - i == self.team_size + 1:
                l.append(self.members[i:i + self.team_size + 1])
            else:
                l.append(self.members[i:i + self.team_size])
        self.team_members = dict((i + 1, j) for i, j in enumerate(l))
        s = ''
        for key, value in self.team_members.items():
            s += 'Команда ' + str(key) + ': ' + str(value) + '\n'
            self.teams[key] = 0
        return s

    def add_word(self, word):
        """Adding a new word into the word list"""
        if word in self.words:
            raise ValueError('Такое слово уже есть в шляпе.')
        else:
            self.words.append(word)
            return 'Слово успешно добавлено.'

    def get_word(self):
        """Getting a word from word list and put it into list of used words"""
        if not self.round_words:
            return None
        else:
            w = self.round_words.pop(random.randint(0, len(self.round_words) - 1))
            return w

    def check_word(self, word, is_ok, team_number=0):
        """Has a team guessed the word correctly or not"""
        if is_ok:
            self.teams[team_number] += 1
        else:
            self.round_words.append(word)

    def get_result(self):
        """Show teams' point"""
        s = ''
        for key, value in self.teams.items():
            s += 'Команда ' + str(key) + ' - ' + str(value) + ' очков.' + '\n'
        return s

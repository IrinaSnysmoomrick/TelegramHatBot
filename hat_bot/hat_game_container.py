"""
How to work with set of games implementation
"""
from hat_bot.hat_game import HatGame


class HatGameContainer:
    def __init__(self):
        self.games = {}
        self.game_players = {}

    def start_new_game(self, team_size):
        """Start new game method"""
        new_game = HatGame()
        new_game.team_size = team_size
        self.games[new_game.game_number] = new_game
        return new_game.game_number

    def reg_player(self, user_id, game_id, user_name):
        """Add a new player into list of members"""
        if game_id not in self.games.keys():
            raise ValueError('Игра с таким номером не создана.')
        if self.games[game_id].status > 1:
            raise ValueError('Этап регистрации на игру уже завершен.')
        if self.get_user_game(user_id) is None:
            # if the user is not in a list of any other games,
            # add him/her into the requested game
            self.games[game_id].reg_member(user_id, user_name)
            # add the player into list with connections player-game
            self.game_players[user_id] = game_id
        elif self.game_players[user_id] == game_id:
            raise ValueError('Участник уже зарегистрирован на этой игре.')
        else:
            raise ValueError(f'Участник уже зарегистрирован на игре {self.game_players[user_id]}.')

    def get_user_game(self, user_id):
        """Get a game by user_id"""
        if user_id in self.game_players.keys():
            user_game_number = self.game_players.get(user_id)
            return self.games[user_game_number]
        else:
            return None

    def get_help(self):
        """Show a list of available commands"""
        return ("Доступные команды:\n"
                "/start_game - начать новую игру. Бот пришлет вам номер начатой игры\n"
                "/reg game_number - заявить об участии в игре, где game_number - номер, полученный при выполнении команды start_game\n"
                "/round - начать разыгрывать слова из ""шляпы""\n"
                "/result - подвести итоги игры\n"
                "любое слово не из списка команд, будет добавлено в ""шляпу""\n"
                "отправить число = номеру команды - вытянуть слово из ""шляпы"""
                )

    def finish_game(self, user_id):
        user_game = self.get_user_game(user_id)
        self.game_players = {key:val for key, val in self.game_players.items() if val != user_game.game_number}
        self.games.pop(user_game.game_number)

    def get_game_players(self, game_id):
        return list(key for key, value in self.game_players.items() if value == game_id)
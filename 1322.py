# -*- coding: utf-8 -*-

# Подземелье было выкопано ящеро-подобными монстрами рядом с аномальной рекой, постоянно выходящей из берегов.
# Из-за этого подземелье регулярно затапливается, монстры выживают, но не герои, рискнувшие спуститься к ним в поисках
# приключений.
# Почуяв безнаказанность, ящеры начали совершать набеги на ближайшие деревни. На защиту всех деревень не хватило
# солдат и вас, как известного в этих краях героя, наняли для их спасения.
#
# Карта подземелья представляет собой json-файл под названием rpg.json. Каждая локация в лабиринте описывается объектом,
# в котором находится единственный ключ с названием, соответствующем формату "Location_<N>_tm<T>",
# где N - это номер локации (целое число), а T (вещественное число) - это время,
# которое необходимо для перехода в эту локацию. Например, если игрок заходит в локацию "Location_8_tm30000",
# то он тратит на это 30000 секунд.
# По данному ключу находится список, который содержит в себе строки с описанием монстров а также другие локации.
# Описание монстра представляет собой строку в формате "Mob_exp<K>_tm<M>", где K (целое число) - это количество опыта,
# которое получает игрок, уничтожив данного монстра, а M (вещественное число) - это время,
# которое потратит игрок для уничтожения данного монстра.
# Например, уничтожив монстра "Boss_exp10_tm20", игрок потратит 20 секунд и получит 10 единиц опыта.
# Гарантируется, что в начале пути будет две локации и один монстр
# (то есть в коренном json-объекте содержится список, содержащий два json-объекта, одного монстра и ничего больше).
#
# На прохождение игры игроку дается 123456.0987654321 секунд.
# Цель игры: за отведенное время найти выход ("Hatch")
#
# По мере прохождения вглубь подземелья, оно начинает затапливаться, поэтому
# в каждую локацию можно попасть только один раз,
# и выйти из нее нельзя (то есть двигаться можно только вперед).
#
# Чтобы открыть люк ("Hatch") и выбраться через него на поверхность, нужно иметь не менее 280 очков опыта.
# Если до открытия люка время заканчивается - герой задыхается и умирает, воскрешаясь перед входом в подземелье.
#
#

import csv
import json
import re
from decimal import Decimal
from datetime import datetime
import time
from termcolor import cprint

remaining_time = '123456.0987654321'
exp = '0'
field_names = ['current_location', 'current_experience', 'current_date']
start_time = datetime.now()
elapsed = datetime.now() - start_time
with open("rpg.json", "r") as read_file:
    data_for_game = json.load(read_file)
    game_map = dict(data_for_game)
LOST_TIME = '10000'
END_GAME_MESSAGE = 'Игра Окончена'
DEATH_MESSAGE = 'Вы не успели выбраться из подземелья и умерли ужасной смертью'
WIN_MESSAGE = 'Вы выбрались! Ура!'
DEADLOCK_MESSAGE = 'Вы зашли в тупик и умерли ужасной смертью'


class GamersState:
    """
    Состояние игрока
    """

    def __init__(self, location, experience, current_time):
        self.location = location
        self.experience = experience
        self.current_time = current_time


class MyRPG:

    def __init__(self):
        self.user_state = dict()

    def run_game(self, map_of_the_dungeon, rem_time, experience, elapsed_time):
        monster_list = []
        location_list = []
        for key, items in map_of_the_dungeon.items():
            self.output_messages(rem_tm=rem_time, something_in_location=items, exp=experience)
            if Decimal(rem_time) <= 0 or items == 'You are winner' and int(experience) >= 280 or len(items) == 0:
                self.recording_results_to_csv()
                break
            cprint(f'Прошло времени {elapsed_time}', color='green')
            cprint(f'Вы вошли в локацию {key} и видите перед собой:', color='green')
            self.location_information(items, monster_list, location_list)
            user_input = self.output_menu()
            if user_input == '1':
                self.attack_on_monsters(mob_list=monster_list, something_in_location=items, loca=key,
                                        map=map_of_the_dungeon, exp=experience, rem_tm=rem_time)
            elif user_input == '2':
                self.moving_to_location(mob_list=monster_list, something_in_location=items, loca=key,
                                        map=map_of_the_dungeon, exp=experience, rem_tm=rem_time,
                                        loca_list=location_list)
            elif user_input == '3':
                cprint(END_GAME_MESSAGE, color='red')
                self.recording_results_to_csv()
                break
            else:
                new_time = self.time_calculation(for_what=LOST_TIME, tm=rem_time)
                cprint(f'Теряясь в нерешительности вы теряете {LOST_TIME} секунд (неверный ввод)', color='yellow')
                cprint(f'У вас {experience} опыта и осталось {new_time} секунд до наводнения', color='yellow')
                elapsed_time = datetime.now() - start_time
                self.user_state['situation'] = GamersState(location=key, experience=experience,
                                                           current_time=datetime.now())
                self.run_game(map_of_the_dungeon, new_time, experience, elapsed_time)

    @staticmethod
    def output_messages(rem_tm, something_in_location, exp):
        if Decimal(rem_tm) <= 0:
            cprint(END_GAME_MESSAGE, color='red')
            cprint(DEATH_MESSAGE, color='red')
        elif something_in_location == 'You are winner' and int(exp) >= 280:
            cprint(WIN_MESSAGE, color='green')
        elif len(something_in_location) == 0:
            cprint(DEADLOCK_MESSAGE, color='red')
            cprint(END_GAME_MESSAGE, color='red')

    def attack_on_monsters(self, mob_list, something_in_location, loca, map, exp, rem_tm):
        """
        Атака на монстра
        """

        if len(mob_list) == 0:
            cprint(f'Тут больше нет монстров', color='cyan')
            elapsed_time = datetime.now() - start_time
            self.run_game(map, rem_tm, exp, elapsed_time)
        elif len(mob_list) == 1:
            cprint(f'Идём в атаку на {mob_list[0]}', color='cyan')

            new_experience = self.experience_calculation(mob=mob_list[0], score=exp)
            new_time = self.time_calculation(for_what=mob_list[0], tm=rem_tm)
            cprint(f'У вас {new_experience} опыта и осталось {new_time} секунд до наводнения', color='yellow')
            something_in_location.remove(mob_list[0])
            elapsed_time = datetime.now() - start_time
            self.user_state['situation'] = GamersState(location=loca, experience=new_experience,
                                                       current_time=datetime.now())
            self.run_game(map, new_time, new_experience, elapsed_time)

        else:
            print(f'Какого монстра хотите атаковать?')
            self.selecting_variant(mob_list)
            monster_choice = input('Введите номер \n')
            cprint(f'Идём в атаку на {mob_list[int(monster_choice) - 1]}', color='cyan')

            new_experience = self.experience_calculation(mob=mob_list[int(monster_choice) - 1],
                                                         score=exp)
            new_time = self.time_calculation(for_what=mob_list[int(monster_choice) - 1], tm=rem_tm)
            cprint(f'У вас {new_experience} опыта и осталось {new_time} секунд до наводнения', color='yellow')
            something_in_location.remove(mob_list[int(monster_choice) - 1])
            elapsed_time = datetime.now() - start_time
            self.user_state['situation'] = GamersState(location=loca, experience=new_experience,
                                                       current_time=datetime.now())
            self.run_game(map, new_time, new_experience, elapsed_time)

    def moving_to_location(self, mob_list, something_in_location, loca, map, exp, rem_tm, loca_list):
        """
        Переход в новую локацию
        """

        if len(loca_list) == 1:
            cprint(f'Переходим в локацию {loca_list[0]}', color='cyan')
            rem_time = self.time_calculation(for_what=loca_list[0], tm=rem_tm)
            cprint(f'У вас {exp} опыта и осталось {rem_time} секунд до наводнения', color='yellow')
            for x in mob_list:
                something_in_location.remove(x)
            elapsed_time = datetime.now() - start_time
            self.user_state['situation'] = GamersState(location=loca_list[0], experience=exp,
                                                       current_time=datetime.now())
            self.run_game(something_in_location[0], rem_time, exp, elapsed_time)
        else:
            print(f'В какую локацию хотите перейти?')
            self.selecting_variant(loca_list)
            for x in mob_list:
                something_in_location.remove(x)
            location_choise = input('Введите номер \n')
            if self.selecting_variant(loca_list) < int(location_choise) or int(location_choise) <= 0:
                new_time = self.time_calculation(for_what=LOST_TIME, tm=rem_tm)
                cprint(f'Теряясь в нерешительности вы теряете {LOST_TIME} секунд (неверный ввод)',
                       color='yellow')
                cprint(f'У вас {exp} опыта и осталось {new_time} секунд до наводнения', color='yellow')
                elapsed_time = datetime.now() - start_time
                self.user_state['situation'] = GamersState(location=loca, experience=exp,
                                                           current_time=datetime.now())
                self.run_game(map, new_time, exp, elapsed_time)
            else:
                cprint(f'Переходим в локацию {loca_list[int(location_choise) - 1]}', color='cyan')
                new_time = self.time_calculation(for_what=loca_list[int(location_choise) - 1],
                                                 tm=rem_tm)
                cprint(f'У вас {exp} опыта и осталось {new_time} секунд до наводнения', color='yellow')
                elapsed_time = datetime.now() - start_time
                self.user_state['situation'] = GamersState(
                    location=loca_list[int(location_choise) - 1],
                    experience=exp,
                    current_time=datetime.now())
                self.run_game(something_in_location[int(location_choise) - 1], new_time, exp, elapsed_time)

    @staticmethod
    def output_menu():
        """
        Меню действий
        """
        user_input = input('Что будете делать?\nВыберите действие:\n\n'
                           '1.Атаковать монстра\n'
                           '2.Перейти в другую локацию\n'
                           '3.Сдаться и выйти из игры\n')
        return user_input

    @staticmethod
    def location_information(something_in_location, mob_list, loc_list):
        """
        Вывод информации о локации
        """

        for i in something_in_location:
            if type(i) == str:
                mob = i
                cprint(f'Монстр {mob}', color='red')
                mob_list.append(mob)
            else:
                for k, j in i.items():
                    cprint(f'Вход в локацию: {k}', color='blue')
                    loc_list.append(k)

    @staticmethod
    def experience_calculation(mob, score):
        """
        Подсчёт опыта
        """

        re_search_exp = re.search(r'exp\d+', mob)
        experience_for_mob = re_search_exp[0][3:]
        score = Decimal(score) + Decimal(experience_for_mob)
        return score

    @staticmethod
    def time_calculation(for_what, tm):
        """Подсчёт времени оставшегося до затопления"""

        if for_what.isdigit():
            tm = Decimal(tm) - Decimal(for_what)
        else:
            re_search_time = re.search(r'tm\d+', for_what)
            time_for_action = re_search_time[0][2:]
            tm = Decimal(tm) - Decimal(time_for_action)
        return tm

    @staticmethod
    def selecting_variant(list_data):
        """
        Метод для вывода на экран вариантов атакуемых монстров или вариантов локаций.
        """

        for num, value in enumerate(list_data):
            print(f'{num + 1} - {value}')
        return len(list_data)

    def recording_results_to_csv(self):
        """
        Запись информации об игре после успешного или не успешного прохождения
        """

        state = self.user_state['situation']
        value_list = [{'current_location': state.location, 'current_experience': state.experience,
                       'current_date': state.current_time}]
        with open('dungeon.csv', "w", newline='') as out_file:
            writer = csv.DictWriter(out_file, delimiter='|', fieldnames=field_names)
            writer.writeheader()
            writer.writerows(value_list)


game = MyRPG()
game.run_game(map_of_the_dungeon=game_map, rem_time=remaining_time, experience=exp, elapsed_time=elapsed)
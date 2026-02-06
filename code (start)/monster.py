import pygame
from game_data import MONSTER_DATA
from random import randint

class Monster:
    def __init__(self, name, level):
        self.name, self.level = name, level
        self.paused = False

        # stats
        self.element = MONSTER_DATA[name]['stats']['element']
        self.base_stats = MONSTER_DATA[name]['stats']
        self.health = self.base_stats['max_health'] * self.level
        self.energy = self.base_stats['max_energy'] * self.level
        self.initiative = 0
        self.health -= randint(0,200)
        self.energy -= randint(0,100)
        self.abilities = MONSTER_DATA[name]['abilities']

        # experience
        self.xp = randint(0,1000)
        self.max_xp = 1000
        self.level_up = self.level * 150

        self.xp_bar_width = 50
        self.xp_bar_height = 5

    def __repr__(self):
        return f'monster: {self.name}, lvl: {self.level}'

    def draw_xp_bar(self, surface, x, y):
        # background
        bg_rect = pygame.Rect(x, y, self.xp_bar_width, self.xp_bar_height)
        pygame.draw.rect(surface, (0, 0, 0), bg_rect)

        # foreground (white) proportion
        ratio = 0.0
        if self.max_xp > 0:
            ratio = max(0, 0, min(1.0, float(self.xp) / float(self.max_xp)))

        fill_width = int(self.xp_bar_width * ratio)
        if fill_width > 0:
            fg_rect = pygame.Rect(x, y, fill_width, self.xp_bar_height)
            pygame.draw.rect(surface, (255, 255, 255), fg_rect)

        # optional border for visibility 
        pygame.draw.rect(surface, (30, 30, 30), bg_rect, 1)

    def get_stat(self, stat):
        return self.base_stats[stat] * self.level

    def get_stats(self):
        return {
            'health': self.get_stat('max_health'),
            'energy': self.get_stat('max_energy'),
            'attack': self.get_stat('attack'),
            'defense': self.get_stat('defense'),
            'speed': self.get_stat('speed'),
            'recovery': self.get_stat('recovery'),
        }

    def get_abilities(self):
        return [ability for lvl, ability in self.abilities.items() if self.level >= lvl]

    def get_info(self):
        return (
            (self.health, self.get_stat('max_health')),
            (self.energy, self.get_stat('max_energy')),
            (self.initiative, 100)
            )

    def update(self, dt):
        if not self.paused:
            self.initiative += self.get_stat('speed') * dt
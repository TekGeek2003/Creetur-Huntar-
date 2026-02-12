from settings import *
from timer import Timer

class Evolution:
    def __init__(self, frames, start_monster, end_monster, font, end_evolution):
        self.display_surface = pygame.display.get_surface()
        self.start_monster_surf = pygame.transform.scale2x(frames[start_monster]['idle'][0])
        self.end_monster_surf = pygame.transform.scale2x(frames[end_monster]['idle'][0])
        self.timers = {
            'start': Timer(800, autostart = True),
            'end': Timer(1800, func = end_evolution)
        }

        # screen tint
        self.tint_surf = pygame.Surface(self.display_surface.get_size())
        self.tint_surf.set_alpha(200)

    def update(self, dt):
        for timer in self.timers.values():
            timer.update()

        if not self.timers['start'].active:
            self.display_surface.blit(self.tint_surf, (0,0))
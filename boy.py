from pico2d import load_image, get_time, load_font
from sdl2 import SDL_KEYDOWN, SDLK_SPACE, SDLK_RIGHT, SDL_KEYUP, SDLK_LEFT

import game_world
import game_framework
from ball import Ball
from state_machine import StateMachine


def space_down(e): # e is space down ?
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_SPACE

time_out = lambda e: e[0] == 'TIMEOUT'

def right_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_RIGHT


def right_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_RIGHT


def left_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_LEFT


def left_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_LEFT



# Boy의 Run Speed 계산

PIXEL_PER_METER = (10.0 / 0.3)
RUN_SPEED_KMPH = 36.0
RUN_SPEED_MPH = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPH / 60.0)
RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER)
# Boy Run Speed
# 여기를 채우시오.


TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 8
FRAMES_PER_SEC = FRAMES_PER_ACTION * ACTION_PER_TIME

# 새 크기 : 181 x 167 (pixel) -> 543 x 501 (cm)
# 새 속도 : 36km/h -> 10m/s -> 333.33 pixel/s




class Idle:

    def __init__(self, boy):
        self.boy = boy

    def enter(self, e):
        self.boy.wait_time = get_time()
        self.boy.dir = 0


    def exit(self, e):
        if space_down(e):
            self.boy.fire_ball()


    def do(self):
        if int(self.boy.frame) == 4:
            if self.boy.image_y > 0:
                self.boy.image_y -= 1
                self.boy.frame = 0
            else:
                self.boy.image_y = 2
                self.boy.frame = 0
        self.boy.frame = (self.boy.frame + FRAMES_PER_SEC * game_framework.frame_time) % 5
        self.boy.x += self.boy.dir * RUN_SPEED_PPS * game_framework.frame_time

    def draw(self):
        if self.boy.face_dir == 1: # right
            self.boy.image.clip_draw(int(self.boy.frame) * 181, 167 * self.boy.image_y, 181, 167, self.boy.x, self.boy.y)
        else: # face_dir == -1: # left
            self.boy.image.clip_composite_draw(int(self.boy.frame) * 181, 167 * self.boy.image_y, 181, 167, 0.0, 'h', self.boy.x, self.boy.y, 181, 160)


class Sleep:

    def __init__(self, boy):
        self.boy = boy

    def enter(self, e):
        pass

    def exit(self, e):
        pass

    def do(self):
        self.boy.frame = (self.boy.frame + FRAMES_PER_SEC * game_framework.frame_time) % 8


    def handle_event(self, event):
        pass

    def draw(self):
        if self.boy.face_dir == 1:
            self.boy.image.clip_composite_draw(int(self.boy.frame)* 100, 300, 100, 100, 3.141592/2, '', self.boy.x - 25, self.boy.y - 25, 100, 100)
        else:
            self.boy.image.clip_composite_draw(int(self.boy.frame) * 100, 200, 100, 100, -3.141592/2, '', self.boy.x + 25, self.boy.y - 25, 100, 100)



class Run:
    def __init__(self, boy):
        self.boy = boy

    def enter(self, e):
        if right_down(e) or left_up(e):
            self.boy.dir = self.boy.face_dir = 1
        elif left_down(e) or right_up(e):
            self.boy.dir = self.boy.face_dir = -1

    def exit(self, e):
        if space_down(e):
            self.boy.fire_ball()

    def do(self):
        if int(self.boy.frame) == 4:
            if self.boy.image_y > 0:
                self.boy.image_y -= 1
                self.boy.frame = 0
            else:
                self.boy.image_y = 2
                self.boy.frame = 0
        self.boy.frame = (self.boy.frame + FRAMES_PER_SEC * game_framework.frame_time) % 5
        self.boy.x += self.boy.dir * RUN_SPEED_PPS * game_framework.frame_time

    def draw(self):
        if self.boy.face_dir == 1: # right
            self.boy.image.clip_draw(int(self.boy.frame) * 181, 167 * self.boy.image_y, 181, 167, self.boy.x, self.boy.y)
        else: # face_dir == -1: # left
            self.boy.image.clip_composite_draw(int(self.boy.frame) * 181, 167 * self.boy.image_y, 181, 167, 0.0, 'h', self.boy.x, self.boy.y, 181, 160)







class Boy:
    def __init__(self):

        self.font = load_font('ENCR10B.TTF', 16)

        self.item = None

        self.x, self.y = 400, 90
        self.frame = 0
        self.face_dir = 1
        self.dir = 0
        self.image = load_image('bird_animation.png')
        self.image_y = 2

        self.IDLE = Idle(self)
        self.SLEEP = Sleep(self)
        self.RUN = Run(self)
        self.state_machine = StateMachine(
            self.IDLE,
            {
                self.IDLE : {space_down: self.IDLE, right_down: self.RUN, left_down: self.RUN, right_up: self.RUN, left_up: self.RUN},
                self.RUN : {space_down: self.RUN, right_up: self.IDLE, left_up: self.IDLE, right_down: self.IDLE, left_down: self.IDLE}
            }
        )



    def update(self):
        self.state_machine.update()


    def handle_event(self, event):
        self.state_machine.handle_state_event(('INPUT', event))


    def draw(self):
        self.state_machine.draw()
        self.font.draw(self.x - 60, self.y + 50, f'{get_time():.2f}', (255, 255, 0))


    def fire_ball(self):
        ball = Ball(self.x, self.y, self.face_dir * 10)
        game_world.add_object(ball)




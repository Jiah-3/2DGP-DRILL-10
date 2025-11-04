from pico2d import get_time

import game_framework

PIXEL_PER_METER = (10.0 / 0.3)
RUN_SPEED_KMPH = 36.0
RUN_SPEED_MPH = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPH / 60.0)
RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER)


TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 8
FRAMES_PER_SEC = FRAMES_PER_ACTION * ACTION_PER_TIME

class AutoRun:
    def __init__(self, boy):
        self.boy = boy
        self.start_time = 0.0

    def enter(self, e):
        self.boy.dir = self.boy.face_dir
        self.start_time = get_time()

    def exit(self, e):
        pass

    def do(self):
        self.boy.frame = (self.boy.frame + FRAMES_PER_SEC * game_framework.frame_time) % 5
        self.boy.x += self.boy.dir * RUN_SPEED_PPS * game_framework.frame_time
        if self.boy.x < 0:
            self.boy.x = 0
            self.boy.dir = self.boy.face_dir = 1
        elif self.boy.x > 1600:
            self.boy.x = 1600
            self.boy.dir = self.boy.face_dir = -1

        if get_time() - self.start_time > 5.0:
            self.boy.state_machine.handle_state_event(('TIME_OUT', None))

    def draw(self):
        if self.boy.face_dir == 1: # right
            self.boy.image.clip_draw(int(self.boy.frame) * 181, 167 * self.boy.image_y, 181, 167, self.boy.x, self.boy.y)
        else: # face_dir == -1: # left
            self.boy.image.clip_composite_draw(int(self.boy.frame) * 181, 167 * self.boy.image_y, 181, 167, 0.0, 'h', self.boy.x, self.boy.y, 181, 160)

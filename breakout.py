
import itertools
import time
import random
import math

import numpy as np

DSP_W = 128
DSP_H = 64

BR_W = 13

class Game:
    def __init__(self):
        self.init_game()

    def start_game(self):
        while True:
            game.update()
            game.render()
            time.sleep(0.1)

    def init_game(self):
        self.display = np.zeros(shape=(DSP_W, DSP_H), dtype=np.int16)
        self.player = Player()
        self.ball = Ball()
        self.wall = Wall()
        self.lives = 3

        self.bricks = []
        for rowpos in range(5):
            for colpos in range(8):
                self.bricks.append(Brick((colpos * (BR_W+3) + 1 + BR_W/2, 2 + rowpos * 4)))

    def game_over(self):
        self.lives -= 1
        if self.lives <= 0:
            self.init_game()
        else:
            self.ball = Ball()
            self.player = Player()

    def update(self):
        self.ball.pos = self.ball.calc_new_pos()
        if self.ball.pos[1] >= DSP_H:
            self.game_over()
        for entity in itertools.chain((self.player,), (self.wall,), self.bricks):
            result = self.ball.collide(entity.displayed)
            if np.any(result):
                slice = result[self.ball.x_min:self.ball.x_max + 1, self.ball.y_min:self.ball.y_max + 1]
                self.ball.bounce(slice)
                try:
                    self.bricks.remove(entity)
                except ValueError:
                    continue

    def render(self):
        new_display = np.zeros(shape=(DSP_W, DSP_H), dtype=np.int16)
        self.wall.render(new_display)
        self.player.render(new_display)
        self.ball.render(new_display)
        for brick in self.bricks:
            brick.render(new_display)
        self.display = new_display
        self.print_display()

    def print_display(self):
        str = '\n'*60
        str += "-" * 128 + "\n"
        for row in self.display.T:
            str += "|"
            for pixel in row:
                if pixel == 0:
                    str += " "
                else:
                    str += "X"
            str += "|\n"
        str += "-" * 128 + "\n"
        print(str)


class Entity:
    def __init__(self, pos, width):
        self.pos = pos
        self.width = width
        self.height = 3

    @property
    def displayed(self):
        disp = np.zeros(shape=(DSP_W, DSP_H))
        self.render(disp)
        return disp

    @property
    def x_min(self):
        return int(self.pos[0] - (self.width - 1) / 2)

    @property
    def x_max(self):
        return int(self.pos[0] + (self.width - 1) / 2)

    @property
    def y_min(self):
        return int(self.pos[1] - (self.height - 1) / 2)

    @property
    def y_max(self):
        return int(self.pos[1] + (self.height - 1) / 2)

    def render(self, display):
        for y in range(self.y_min, self.y_max + 1):
            for x in range(self.x_min, self.x_max + 1):
                try:
                    display[x][y] = 1
                except IndexError:
                    continue

    def collide(self, displayed_entity):
        result = np.logical_and(self.displayed, displayed_entity)
        return result



class Player(Entity):
    def __init__(self):
        super().__init__((64, 60), 31)


class Ball(Entity):
    def __init__(self):
        super().__init__((64, 25), 5)
        self.height = self.width
        self.direction = (rotate((0, 1), random.randint(-45, 45)))

    def calc_new_pos(self):
        return self.pos[0] + self.direction[0], self.pos[1] + self.direction[1]

    def bounce(self, slice):
        hits = []
        for x, row in enumerate(slice):
            for y, pixel in enumerate(row):
                if pixel:
                    hits.append((x - int(self.width/2), y - int(self.width / 2)))
        reflect_vec = cut_to_length(-np.sum(np.array(hits), axis=0), 1)
        self.direction = self.direction - 2 * np.dot(self.direction, reflect_vec) * reflect_vec
        pass

class Brick(Entity):
    def __init__(self, pos):
        super().__init__(pos, BR_W)


class Wall:
    def __init__(self):
        self.wall = np.zeros(shape=(DSP_W, DSP_H), dtype=np.int16)
        for y in range(DSP_H):
            self.wall[0, y] = 1
            self.wall[DSP_W - 1, y] = 1
        for x in range(DSP_W):
            self.wall[x, 0] = 1

    @property
    def displayed(self):
        return self.wall

    def render(self, display):
        display += self.wall

def rotate(vector, degrees):
    a = np.radians(degrees)
    ca, sa = math.cos(a), math.sin(a)
    rotation_matrix = np.array(
        [[ca, -sa],
         [sa, ca]])
    result = rotation_matrix.dot(vector)
    return result

def cut_to_length(vector, length):
    return length * (vector / np.linalg.norm(vector))


def angle(vector_a, vector_b):
    if np.linalg.norm(vector_a) == 0 or np.linalg.norm(vector_b) == 0:
        return 0
    else:
        return (vector_a * vector_b) / (np.linalg.norm(vector_a) * np.linalg.norm(vector_b))


if __name__ == '__main__':
    game = Game()
    game.start_game()

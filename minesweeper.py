import os
import random
import sys


class GameLogic:
    def __init__(self, size: tuple, mines: int):
        self.size = size
        self.mines = mines
        self.fields = [[0] * size[0] for i in range(size[1])]

    def generate_field(self, seed: int = random.random()):
        def get_rand_pos():
            random.seed(seed)
            while True:
                yield random.randrange(self.size[1]), random.randrange(self.size[0])

        mines = self.mines
        for x, y in get_rand_pos():
            if self.fields[x][y] != -1:
                for line in self.fields[max(0, x-1):x+2]:
                    for n in range(max(0, y-1), min(y+2, self.size[0])):
                        if line[n] != -1:
                            line[n] += 1

                self.fields[x][y] = -1
                mines -= 1
                if not mines:
                    break


def pretty_print(trans):
    for line in trans:
        for e in line:
            sys.stdout.write(str(e) if e != -1 else '*')
        sys.stdout.write(os.linesep)
    sys.stdout.write(os.linesep)


if __name__ == '__main__':
    gl = GameLogic((9, 9), 12)
    gl.generate_field()
    pretty_print(gl.fields)

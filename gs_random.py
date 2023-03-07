from random import randint
from threading import Thread


class LocusRandomizer(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.pos = []
        for i in range(8):
            x = randint(-550, 550)
            y = randint(-550, 550)
            z = randint(0, 400)
            yaw = randint(0, int(2*3.14))
            self.pos.append((x, y, z, yaw))
        self.main()

    def main(self):
        for i in range(8):
            x, y, z, yaw = self.pos[i][0], self.pos[i][1], self.pos[i][2], self.pos[i][3]
            x += randint(-5, 5)
            y += randint(-5, 5)
            while True:
                z += randint(-2, 2)
                if z > 0:
                    break
                else:
                    z = 0
            yaw += randint(-1, 1)
            self.pos[i] = (x, y, z, yaw)

    def get_pos(self):
        if len(self.pos) > 3:
            return self.pos
        else:
            return None

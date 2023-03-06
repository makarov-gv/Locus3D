# moderngl? vpython? panda3d? vispy?
import gs_lps
from random import randint

blue_drone = pygame.image.load("images/blue_drone.png")
blue_robot = pygame.image.load("images/blue_robot.png")
red_drone = pygame.image.load("images/red_drone.png")
red_robot = pygame.image.load("images/red_robot.png")
FPS = 60
WIDTH = HEIGHT = 1100
pi = 3.14


def _parse():
    pure_xy = 1


class LocusVisualization(pygame.sprite.Sprite):
    def __init__(self, names):
        pygame.init()
        pygame.sprite.Sprite.__init__(self)
        self.screen = pygame.display.set_mode(size=(WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("Locus Visualization")
        pygame.display.set_icon(pygame.image.load("images/icon.png"))

        self.surfs = []
        for name in names:
            if name == "blue_drone":
                self.surfs.append(blue_drone)
            elif name == "blue_robot":
                self.surfs.append(blue_robot)
            elif name == "red_drone":
                self.surfs.append(red_drone)
            elif name == "red_robot":
                self.surfs.append(red_robot)
        self._main()

    def _main(self):
        # uart = gs_lps.us_nav(serial_port="/dev/ttyUSB0")
        # uart.start()
        running = True

        pos = []
        for i in range(len(self.surfs)):
            x = randint(-350, 350)
            y = randint(-350, 350)
            yaw = randint(0, int(2 * pi))
            pos.append((x, y, yaw))

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            # pos = _parse(self, uart)
            # positions and angles extraction to be implemented... pos_list[i] = (x, y, yaw)
            if len(pos) != len(self.surfs):
                print("{} drones lack coordinates, script may run incorrectly".format(len(self.surfs)-len(pos)))

            # ...
            self.screen.fill((0, 0, 0))
            for i in range(len(self.surfs)):
                x, y, yaw = pos[i][0], pos[i][1], pos[i][2]
                x += randint(-5, 5)
                y += randint(-5, 5)
                yaw += randint(-2, 2)
                pos[i] = (x, y, yaw)

                # x, y, yaw = pos[i][0], pos[i][1], pos[i][2]
                rot_surf = pygame.transform.rotate(self.surfs[i], yaw * 2 * pi)
                print(550+x, 550+y, yaw)
                self.screen.blit(rot_surf, rot_surf.get_rect(center=(WIDTH/2+x, HEIGHT/2+y)))
            pygame.display.update()
            self.clock.tick(FPS)


if __name__ == "__main__":
    name_list = ["blue_drone", "blue_robot", "red_drone", "red_robot", "blue_drone", "blue_robot", "red_drone", "red_robot"]  # bd stands for blue_drone, etc...
    gui = LocusVisualization(name_list)

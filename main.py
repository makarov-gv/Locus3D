import sys
from direct.showbase.ShowBase import ShowBase
from direct.actor.Actor import Actor
from panda3d.core import *
from randomizer import Randomizer

QUANTITY = 16
# TODO: окошко с координатами каждого дрона, дрон - сфера изменяемого цвета d/r 10 см, функция записи шоу,
# TODO: привязка функций записи и запуска логгера к клавишам и вывести табличку с управлением в окно
# 11x11x4, drone diameter = 0.1


def draw_axis(render):
    x_axis = LineSegs("lines")
    x_axis.moveTo(0, 0, 0)
    x_axis.drawTo(1, 0, 0)
    x_axis.setThickness(1)
    x_node = NodePath(x_axis.create())
    x_node.reparentTo(render)
    x_node.setColor((1.0, 0.0, 0.0, 1), 1)

    y_axis = LineSegs("lines")
    y_axis.moveTo(0, 0, 0)
    y_axis.drawTo(0, 1, 0)
    y_axis.setThickness(1)
    y_node = NodePath(y_axis.create())
    y_node.reparentTo(render)
    y_node.setColor((0.0, 1.0, 0.0, 1), 1)

    z_axis = LineSegs("lines")
    z_axis.moveTo(0, 0, 0)
    z_axis.drawTo(0, 0, 1)
    z_axis.setThickness(1)
    z_node = NodePath(z_axis.create())
    z_node.reparentTo(render)
    z_node.setColor((0.0, 0.0, 1.0, 1), 1)


def draw_grid(render):
    grid = LineSegs("lines")
    grid.moveTo(-5.5, -5.5, 0)
    for i in range(11):
        grid.moveTo(-5.5+i, -5.5, 0)
        grid.drawTo(-5.5+i, 5.5, 0)
    grid.moveTo(-5.5, -5.5, 0)
    for i in range(11):
        grid.moveTo(-5.5, -5.5+i, 0)
        grid.drawTo(5.5, -5.5+i, 0)

    grid.moveTo(-5.5, -5.5, 0)
    grid.drawTo(5.5, -5.5, 0)
    grid.drawTo(5.5, 5.5, 0)
    grid.drawTo(-5.5, 5.5, 0)
    grid.drawTo(-5.5, -5.5, 0)
    grid.drawTo(-5.5, -5.5, 4)
    grid.drawTo(5.5, -5.5, 4)
    grid.drawTo(5.5, 5.5, 4)
    grid.drawTo(-5.5, 5.5, 4)
    grid.drawTo(-5.5, -5.5, 4)
    grid.moveTo(5.5, -5.5, 0)
    grid.drawTo(5.5, -5.5, 4)
    grid.moveTo(5.5, 5.5, 0)
    grid.drawTo(5.5, 5.5, 4)
    grid.moveTo(-5.5, 5.5, 0)
    grid.drawTo(-5.5, 5.5, 4)
    grid.setThickness(1)
    grid_node = NodePath(grid.create())
    grid_node.reparentTo(render)
    grid_node.setColor((0.2, 0.2, 0.2, 1), 1)


class Locus3D(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.gs = Randomizer()

        draw_axis(self.render)
        draw_grid(self.render)
        base.setBackgroundColor(0, 0, 0)

        self.drones = []
        for i in range(QUANTITY):
            drone = Actor("models/jack")
            drone.setScale(0.1, 0.1, 0.1)
            drone.reparentTo(self.render)
            self.drones.append(drone)

        self.accept("escape", sys.exit)
        taskMgr.add(self.move, 'moveTask')

    def move(self, task):
        pos = self.gs.get_pos()
        print(pos)
        if pos is not None:
            for i in range(QUANTITY):
                self.drones[i].setX(pos[i][0]/100)
                self.drones[i].setY(pos[i][1]/100)
                self.drones[i].setZ(pos[i][2]/100)
        return task.cont


if __name__ == '__main__':
    visualization = Locus3D()
    visualization.run()

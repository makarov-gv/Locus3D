import sys
import time
from math import pi, sin, cos
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Sequence
from panda3d.core import *
from gs_random import LocusRandomizer


def drawStartPoint(render):
    x_axis = LineSegs("lines")
    x_axis.moveTo(0, 0, 0)
    x_axis.drawTo(2, 0, 0)
    x_axis.setThickness(2)
    x_node = NodePath(x_axis.create())
    x_node.reparentTo(render)
    x_node.setColor((2.0, 0.0, 0.0, 0.5), 1)

    y_axis = LineSegs("lines")
    y_axis.moveTo(0, 0, 0)
    y_axis.drawTo(0, 2, 0)
    y_axis.setThickness(2)
    y_node = NodePath(y_axis.create())
    y_node.reparentTo(render)
    y_node.setColor((0.0, 2.0, 0.0, 0.5), 1)

    z_axis = LineSegs("lines")
    z_axis.moveTo(0, 0, 0)
    z_axis.drawTo(0, 0, 2)
    z_axis.setThickness(2)
    z_node = NodePath(z_axis.create())
    z_node.reparentTo(render)
    z_node.setColor((0.0, 0.0, 2.0, 0.5), 1)


def drawGrid(render):
    grid = LineSegs("lines")
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

class Locus3D(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)
        self.gs = LocusRandomizer()
        drawStartPoint(self.render)
        drawGrid(self.render)
        base.setBackgroundColor(0, 0, 0)

        # self.scene = self.loader.loadModel("models/environment")
        #
        # # Reparent the model to render.
        #
        # self.scene.reparentTo(self.render)
        #
        # # Apply scale and position transforms on the model.
        #
        # self.scene.setScale(0.25, 0.25, 0.25)
        #
        # self.scene.setPos(-8, 42, 0)

        self.drones = []
        for i in range(8):
            drone = Actor("models/jack")
            drone.setScale(0.1, 0.1, 0.1)
            drone.reparentTo(self.render)
            self.drones.append(drone)
        print(self.drones[1])
        # Load and transform the panda actor

        self.accept("escape", sys.exit)

        taskMgr.add(self.move, 'moveTask')

    def move(self, task):
        self.gs.main()
        pos = self.gs.get_pos()
        print(pos)
        drones = []
        if pos is not None: #11x11x4, drone diameter = 0.1
            for i in range(len(pos)):
                self.drones[i].setX(pos[i][0]/100)
                self.drones[i].setY(pos[i][1]/100)
                self.drones[i].setZ(pos[i][2]/100)
                self.drones[i].setH(pos[i][3])
        return task.cont


if __name__ == '__main__':
    visualization = Locus3D()
    visualization.run()

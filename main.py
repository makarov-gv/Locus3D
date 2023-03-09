from datetime import date
import os, timeit, json
import pandas as pd
import _temp.randomizer  # to change with lps
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.ShowBase import ShowBase
from direct.actor.Actor import Actor
from panda3d.core import *


def displayText(pos, msg, parent, align):
    return OnscreenText(text=msg, style=1, fg=(1, 1, 1, 1), scale=.05,
                        shadow=(0, 0, 0, 1), parent=parent,
                        pos=pos, align=align)


def drawAxis(render):
    x_axis = y_axis = z_axis = LineSegs("lines")

    x_axis.moveTo(0, 0, 0)
    x_axis.drawTo(1, 0, 0)
    x_axis.setThickness(1)
    x_node = NodePath(x_axis.create())
    x_node.reparentTo(render)
    x_node.setColor((1.0, 0.0, 0.0, 1), 1)

    y_axis.moveTo(0, 0, 0)
    y_axis.drawTo(0, 1, 0)
    y_axis.setThickness(1)
    y_node = NodePath(y_axis.create())
    y_node.reparentTo(render)
    y_node.setColor((0.0, 1.0, 0.0, 1), 1)

    z_axis.moveTo(0, 0, 0)
    z_axis.drawTo(0, 0, 1)
    z_axis.setThickness(1)
    z_node = NodePath(z_axis.create())
    z_node.reparentTo(render)
    z_node.setColor((0.0, 0.0, 1.0, 1), 1)


def drawGrid(render):
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
    def __init__(self, quantity):
        ShowBase.__init__(self)

        self.lps = _temp.randomizer.Randomizer()
        self.logging = False
        self.timer = timeit.default_timer()
        self.date = date.today()
        self.df0 = pd.DataFrame()

        window = WindowProperties()
        window.setTitle("Locus 3D visualization")
        base.win.requestProperties(window)
        displayText((0.08, -0.04 - 0.04), "[F1]: Start logger", base.a2dTopLeft, TextNode.ALeft)
        displayText((0.08, -0.11 - 0.04), "[F2]: Stop logger", base.a2dTopLeft, TextNode.ALeft)
        self.lg_text = displayText((0.08, 0.09), "", base.a2dBottomLeft, TextNode.ALeft)
        drawAxis(self.render)
        drawGrid(self.render)
        base.setBackgroundColor(0, 0, 0)

        self.drones = []
        for i in range(quantity):
            drone = Actor("colorable_sphere")
            drone.setScale(0.22, 0.22, 0.22)
            drone.setColor(0.4, 0.05*i, 0.05*i, 1)  # can be recolored
            drone.reparentTo(self.render)
            self.drones.append(drone)

        self.accept("f1", self._startLogger)
        self.accept("f2", self._stopLogger)
        taskMgr.add(self.__main, 'mainTask')

    def __main(self, task):
        pos = self.lps.get_pos()
        if pos is not None:
            for i in range(len(pos)):
                self.drones[i].setX(pos[i][0]/100)
                self.drones[i].setY(pos[i][1]/100)
                self.drones[i].setZ(pos[i][2]/100)
            if self.logging:
                data = [pos, timeit.default_timer() - self.timer]
                df = pd.DataFrame(
                    [data], columns=['Positions, meters', 'Time passed, seconds']
                )
                self.df0 = pd.concat([self.df0, df])
        return task.cont

    def _startLogger(self):
        if not self.logging:
            self.lg_text.appendText("Logging...")
            self.logging = True

    def _stopLogger(self):
        if self.logging:
            self.lg_text.clearText()
            self.logging = False
            result = self.df0.to_json(orient="records")
            parsed = json.loads(result)
            os.chdir('logs')
            with open(str(self.date)+'.json', 'w') as f:
                json.dump(parsed, f, indent=2)
                print('Log has been saved as {}.json'.format(self.date))
            os.chdir('..')


if __name__ == '__main__':
    visualization = Locus3D(16)
    visualization.run()

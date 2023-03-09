import os
from datetime import date
import timeit
import pandas as pd
# import lps
import json
import randomizer
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.ShowBase import ShowBase
from direct.actor.Actor import Actor
from panda3d.core import *
from screen_recorder_sdk import screen_recorder

QUANTITY = 16
# TODO: окошко с координатами каждого дрона, дрон - сфера изменяемого цвета d/r 10 см, функция записи шоу,
# TODO: привязка функций записи и запуска логгера к клавишам
# 11x11x4, drone diameter = 0.1


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
    def __init__(self):
        ShowBase.__init__(self)
        self.lps = randomizer.Randomizer()
        self.logging = False
        self.capturing = False

        window = WindowProperties()
        window.setTitle("Locus 3D visualization")
        base.win.requestProperties(window)
        displayText((0.08, -0.04 - 0.04), "[F1]: Start/stop logger", base.a2dTopLeft, TextNode.ALeft)
        displayText((0.08, -0.11 - 0.04), "[F2]: Start/stop video capturer", base.a2dTopLeft, TextNode.ALeft)
        self.lg_text = displayText((0.08, 0.16), "", base.a2dBottomLeft, TextNode.ALeft)
        self.cp_text = displayText((0.08, 0.09), "", base.a2dBottomLeft, TextNode.ALeft)
        drawAxis(self.render)
        drawGrid(self.render)
        base.setBackgroundColor(0, 0, 0)

        self.drones = []
        for i in range(QUANTITY):
            drone = Actor("models/jack")
            drone.setScale(0.1, 0.1, 0.1)
            drone.reparentTo(self.render)
            self.drones.append(drone)

        self.accept("f1", self.logger)
        self.accept("f2", self.capturer)

        self.timer = timeit.default_timer()
        self.df0 = pd.DataFrame()
        self.date = date.today()
        taskMgr.add(self._main, 'mainTask')

    def _main(self, task):

        pos = self.lps.get_pos()
        if pos is not None:
            pos_compressed = ''
            for i in range(QUANTITY):
                self.drones[i].setX(pos[i][0]/100)
                self.drones[i].setY(pos[i][1]/100)
                self.drones[i].setZ(pos[i][2]/100)
                pos_compressed += str(pos[i])
            if self.logging:
                data = [pos_compressed, timeit.default_timer() - self.timer]
                df = pd.DataFrame(
                    [data], columns=['Positions, meters', 'Time passed, seconds']
                )
                self.df0 = pd.concat([self.df0, df])
        return task.cont

    def logger(self):
        if not self.logging:
            self.lg_text.appendText("Logging...")
            self.logging = True
        else:
            self.lg_text.clearText()
            self.logging = False
            result = self.df0.to_json(orient='records')
            parsed = json.loads(result)
            os.chdir('logs')
            with open(str(self.date)+'.json', 'w') as f:
                json.dump(parsed, f, indent=2)
                print('saved')
            os.chdir('..')

    def capturer(self):
        if not self.capturing:
            try:
                screen_recorder.start_video_recording('test.mp4', 30, 800000, True)
                self.cp_text.appendText("Capturing...")
                self.capturing = True
            except:
                print('For now only Windows is supported for capturing')
        else:
            screen_recorder.stop_video_recording()
            self.cp_text.clearText()
            self.capturing = False


if __name__ == '__main__':
    visualization = Locus3D()
    visualization.run()

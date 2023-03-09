from direct.gui.OnscreenText import OnscreenText
from direct.showbase.ShowBase import ShowBase
from panda3d.core import *
import tkinter as tk
from tkinter.filedialog import askopenfilename
import _temp.randomizer  # to change with lps
import pandas as pd

def displayText(pos, msg, parent, align):
    return OnscreenText(text=msg, style=1, fg=(1, 1, 1, 1), scale=.05,
                        shadow=(0, 0, 0, 1), parent=parent,
                        pos=pos, align=align)


def drawAxis(render):
    x_axis = y_axis = z_axis = LineSegs('lines')

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
    grid = LineSegs('lines')

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


class LogPlayer(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        window = WindowProperties()
        window.setTitle('Locus 3D log player')
        base.win.requestProperties(window)
        self.accept('f1', self._interact)
        self.accept('f2', self._restart)
        taskMgr.add(self.__main, 'mainTask')

        tk.Tk().withdraw()
        fn = askopenfilename()
        log = pd.read_json(fn)
        log.head()
        self.iterator = 0
        self.positions = list(log['Positions, meters'])
        self.playing = False

        displayText((0.08, -0.04 - 0.04), 'Log {} is ready to be played'.format(fn), base.a2dTopLeft, TextNode.ALeft)
        displayText((0.08, -0.11 - 0.04), '[F1]: Play/pause player', base.a2dTopLeft, TextNode.ALeft)
        displayText((0.08, -0.18 - 0.04), '[F2]: Restart player', base.a2dTopLeft, TextNode.ALeft)
        self.text = displayText((0.08, 0.09), '', base.a2dBottomLeft, TextNode.ALeft)
        base.setBackgroundColor(0, 0, 0)
        drawAxis(self.render)
        drawGrid(self.render)

        self.lps = _temp.randomizer.Randomizer()
        self.drones = []
        for i in range(len(self.positions[0])):
            drone = loader.loadModel('colorable_sphere')
            drone.setScale(0.22, 0.22, 0.22)
            drone.setColor(0.9, 0.035*i, 0.085*i, 1)  # can be recolored
            drone.reparentTo(self.render)
            self.drones.append(drone)

    def __main(self, task):
        if self.iterator >= len(self.positions):
            self.text.setText('Finished')
        if self.iterator < len(self.positions):
            if self.playing:
                pos = self.positions[self.iterator]
                for i in range(len(pos)):
                    self.drones[i].setX(pos[i][0]/100)
                    self.drones[i].setY(pos[i][1]/100)
                    self.drones[i].setZ(pos[i][2]/100)
                self.iterator += 1
            return task.cont

    def _interact(self):
        if not self.playing:
            self.playing = True
            self.text.setText('Playing...')
        else:
            self.playing = False
            self.text.setText('Paused')

    def _restart(self):
        self.playing = True
        self.iterator = 0
        taskMgr.add(self.__main, 'mainTask')
        self.text.setText('Restarted, playing...')


if __name__ == '__main__':
    player = LogPlayer()
    player.run()

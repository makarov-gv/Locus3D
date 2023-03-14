from direct.gui.OnscreenText import OnscreenText
from direct.showbase.ShowBase import ShowBase
from panda3d.core import *
import tkinter as tk
from tkinter.filedialog import askopenfilename
import _temp.randomizer  # to be replaced with lps
import pandas as pd


def displayText(pos, msg, parent, align):
    """
        Display text label in given position containing given message with alignment parameters
        :param pos: label position
        :param msg: text to be displayed
        :param parent: alignment parent
        :param align: alignment state
        :return: OnscreenText class object (text label itself)
        """
    return OnscreenText(text=msg, style=1, fg=(1, 1, 1, 1), scale=.05,
                        shadow=(0, 0, 0, 1), parent=parent,
                        pos=pos, align=align)


def drawAxis(render):
    """
    Create axis lines at the center of the environment. X-axis is red, Y-axis is green and Z-axis is blue
    :param render: ShowBase class method to display lines
    """
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
    """
    Create grid lines at the center of the environment. Grid is 11x11x4 meters. Floor contains 1x1 meter squares for
    proper visualization understanding
    :param render: ShowBase class method to display lines
    """
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
        self.accept('f1', self._interact)  # assign _interact method to F1 keyboard button
        self.accept('f2', self._restart)  # assign _restart method to F2 keyboard button
        self.accept('f3', self._debugger)  # assign _debugger method to F3 keyboard button
        taskMgr.add(self.__main, 'mainTask')  # start looped task (__main function)

        # tkinter is used to get log filename, but other functions are locked by withdraw method
        tk.Tk().withdraw()
        fn = askopenfilename()
        log = pd.read_json(fn)
        log.head()
        self.iterator = 0  # to define log iteration order
        self.positions = list(log['Positions, meters'])
        self.times = list(log['Time passed, seconds'])
        self.playing = False
        self.debugging = False

        displayText((0.08, -0.04 - 0.04), 'Log {} loaded'.format(fn), base.a2dTopLeft, TextNode.ALeft)
        displayText((0.08, -0.11 - 0.04), '[F1]: Play/pause player', base.a2dTopLeft, TextNode.ALeft)
        displayText((0.08, -0.18 - 0.04), '[F2]: Restart player', base.a2dTopLeft, TextNode.ALeft)
        displayText((0.08, -0.25 - 0.04), '[F3]: Show/hide debug labels', base.a2dTopLeft, TextNode.ALeft)
        self.status_text = displayText((0.08, 0.09), '', base.a2dBottomLeft, TextNode.ALeft)
        self.timer_text = displayText((0.08, 0.09), '', base.a2dBottomCenter, TextNode.ACenter)
        base.setBackgroundColor(0, 0, 0)
        drawAxis(self.render)
        drawGrid(self.render)

        self.lps = _temp.randomizer.Randomizer()  # to be replaced with lps
        self.drones = []  # list of drones objects containing model, color and position parameters
        self.dronesText = []

        for i in range(len(self.positions[0])):
            drone = loader.loadModel('colorable_sphere')  # using colorable_sphere model for each drone
            drone.setScale(0.22, 0.22, 0.22)  # scale it to 0,1 diameter size (approximately)
            drone.setColor(0.9, 0.035*i, 0.085*i, 1)  # temporary, to display colors
            drone.reparentTo(self.render)
            self.drones.append(drone)

            node = TextNode('xyz')
            node.setText('')
            droneText = self.aspect2d.attachNewNode(node)
            droneText.setScale(0.2)
            droneText.reparentTo(self.render)
            self.dronesText.append(droneText)

    def __main(self, task):
        if self.iterator >= len(self.positions):
            self.status_text.setText('Finished')
        if self.iterator < len(self.positions):
            if self.playing:
                pos = self.positions[self.iterator]
                for i in range(len(pos)):
                    # for each position in pos list move drones from drones list
                    self.drones[i].setX(pos[i][0]/100)
                    self.drones[i].setY(pos[i][1]/100)
                    self.drones[i].setZ(pos[i][2]/100)

                    if self.debugging:
                        node = self.dronesText[i].node()
                        node.setText('#{}: '.format(i)+str(pos[i][0]/100)+', '+str(pos[i][1]/100)+', '+str(pos[i][2]/100))
                        self.dronesText[i].setX(pos[i][0] / 100 + 0.2)
                        self.dronesText[i].setY(pos[i][1] / 100)
                        self.dronesText[i].setZ(pos[i][2] / 100 + 0.2)
                        self.dronesText[i].setBillboardPointEye()
                time = 'Time passed: '+str(round(self.times[self.iterator], 4))+" seconds"
                self.timer_text.setText(time)
                self.iterator += 1
            return task.cont

    def _interact(self):
        if not self.playing:
            self.playing = True
            self.status_text.setText('Playing...')
        else:
            self.playing = False
            self.status_text.setText('Paused')

    def _restart(self):
        self.playing = True
        self.iterator = 0
        taskMgr.add(self.__main, 'mainTask')
        self.status_text.setText('Restarted, playing...')

    def _debugger(self):
        if not self.debugging:
            self.debugging = True
        else:
            for i in range(len(self.dronesText)):
                node = self.dronesText[i].node()
                node.setText('')
            self.debugging = False


if __name__ == '__main__':
    player = LogPlayer()
    player.run()

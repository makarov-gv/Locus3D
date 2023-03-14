from direct.gui.OnscreenText import OnscreenText
from direct.showbase.ShowBase import ShowBase
from panda3d.core import *
from datetime import datetime
import pandas as pd
import timeit
import json
import _temp.randomizer  # to be replaced with lps


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


class Locus3D(ShowBase):
    def __init__(self, quantity):
        ShowBase.__init__(self)
        window = WindowProperties()
        window.setTitle('Locus 3D visualization')
        base.win.requestProperties(window)
        self.accept('f1', self._startLogger)  # assign _startLogger method to F1 keyboard button
        self.accept('f2', self._stopLogger)  # assign _stopLogger method to F2 keyboard button
        self.accept('f3', self._debugger)  # assign debugger method to F3 keyboard button
        taskMgr.add(self.__main, 'mainTask')  # start looped task (__main function)

        displayText((0.08, -0.04 - 0.04), '[F1]: Start logger', base.a2dTopLeft, TextNode.ALeft)
        displayText((0.08, -0.11 - 0.04), '[F2]: Stop logger, save log', base.a2dTopLeft, TextNode.ALeft)
        displayText((0.08, -0.18 - 0.04), '[F3]: Show/hide debug labels', base.a2dTopLeft, TextNode.ALeft)
        self.loggerText = displayText((0.08, 0.09), "", base.a2dBottomLeft, TextNode.ALeft)
        self.timerText = displayText((0.08, 0.09), '', base.a2dBottomCenter, TextNode.ACenter)
        base.setBackgroundColor(0, 0, 0)
        drawAxis(self.render)
        drawGrid(self.render)

        self.logging = False
        self.debugging = False
        self.df0 = pd.DataFrame()  # dataframe to store positions and time during logging
        self.lps = _temp.randomizer.Randomizer()  # to be replaced with lps
        self.drones = []  # list of drones objects containing model, color and position parameters
        self.dronesText = []

        for i in range(quantity):
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
        pos = self.lps.get_pos()
        if pos is not None:
            for i in range(len(pos)):
                # for each position in pos list move drones from drones list
                self.drones[i].setX(pos[i][0]/100)
                self.drones[i].setY(pos[i][1]/100)
                self.drones[i].setZ(pos[i][2]/100)

                if self.debugging:
                    node = self.dronesText[i].node()
                    node.setText('#{}: '.format(i)+str(pos[i][0]/100)+', '+str(pos[i][1]/100)+', '+str(pos[i][2]/100))
                    self.dronesText[i].setX(pos[i][0]/100+0.2)
                    self.dronesText[i].setY(pos[i][1]/100)
                    self.dronesText[i].setZ(pos[i][2]/100+0.2)
                    self.dronesText[i].setBillboardPointEye()
            if self.logging:
                # if logging is True, log positions and amount of time passed
                data = [list(pos), timeit.default_timer() - self.timer]
                time = 'Time passed: '+str(round(data[1], 4))+" seconds"
                self.timerText.setText(time)
                df = pd.DataFrame(
                    [data], columns=['Positions, meters', 'Time passed, seconds']
                )
                self.df0 = pd.concat([self.df0, df])  # concatenate positions and time to the main dataframe
        return task.cont

    def _startLogger(self):
        if not self.logging:
            self.loggerText.setText('Logging...')
            self.timer = timeit.default_timer()  # timer initialization
            self.logging = True

    def _stopLogger(self):
        if self.logging:
            self.logging = False
            result = self.df0.to_json(orient='records')
            parsed = json.loads(result)
            current_time = datetime.now().strftime('%d-%m-%Y_%H-%M')  # e.g. filename will be 13-03-2023_18-48.json
            with open('logs/'+str(current_time)+'.json', 'w') as f:
                json.dump(parsed, f, indent=2)  # save .json log file
            self.loggerText.setText('Saved as {}.json'.format(current_time))

    def _debugger(self):
        if not self.debugging:
            self.debugging = True
        else:
            for i in range(len(self.dronesText)):
                node = self.dronesText[i].node()
                node.setText('')
            self.debugging = False


if __name__ == '__main__':
    visualization = Locus3D(16)  # 16 drones used in the example, should be predefined
    visualization.run()

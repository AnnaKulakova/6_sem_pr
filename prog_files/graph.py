from PyQt5 import QtWidgets, QtCore
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys  # We need sys so that we can pass argv to QApplication

from influxdb import InfluxDBClient
import prog_files.vars as CN
import random


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self._var_list = {}
        self._client_db = InfluxDBClient(CN.DB_ADDRESS, database=CN.DB_NAME)
        self.graphWidget = pg.PlotWidget()
        self.setCentralWidget(self.graphWidget)
        self.graphWidget.setBackground('w')
        self.graphWidget.addLegend()
        # plot data: x, y value
        self.graphWidget.showGrid(x=True, y=True)
        self.timer = QtCore.QTimer()
        self.timer.setInterval(1000) # 1s
        self.timer.timeout.connect(self._update_plot_data)
        self.timer.start()
        self._last_time_measure = 0

    def _update_plot_data(self):
        res = self._client_db.query("SELECT * FROM "+CN.MEASURE_NAME+" WHERE \"time\" > " + str(self._last_time_measure)
                                    + " GROUP BY \"time()\"",
                                    epoch="ns")
        time = self._last_time_measure
        for pts in res.get_points():
            time = pts.get("time")
            for variable in pts:
                if variable == "time":
                    continue
                if pts[variable] is None:
                    continue
                if self._var_list.get(variable, None) is None:
                    self._var_list[variable] = {
                        "time": [],
                        "value": [],
                        "data":  self.graphWidget.plot([], [], variable, pen=pg.mkPen(color=(
                            random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
                        )))
                    }
                self._var_list[variable]["time"].append(time)
                self._var_list[variable]["value"].append(pts[variable])
        self._last_time_measure = time

        for variables in self._var_list:
            self._var_list[variables]["data"].setData(self._var_list[variables]["time"],
                                                       self._var_list[variables]["value"])


def main():
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
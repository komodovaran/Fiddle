from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from PyQt5.QtWidgets import *


class MatplotlibCanvas(FigureCanvas):
    """
    This is the matplotlib plot_trace_and_preds inside that controls all the visuals.
    Subplots are placed in a grid of nrows, ncols, and a position
    e.g. (131) means 1 row, 3 columns, position 1 (going from top left).
    """

    def __init__(self, parent=None, ax_setup=None, ax_window=None, width=6, height=2, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi, tight_layout=False)

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        self.defaultImageName = "Blank"  # Set default image name
        self.get_window_title()

        self.ax_setup = ax_setup
        self.ax_window = ax_window

    def setupSinglePlotLayout(self):
        """
        Setup for a single panel plot_trace_and_preds.
        """
        self.ax = self.fig.add_subplot(111, aspect="equal")
        self.fig.subplots_adjust(
            left=0.08, right=0.92, top=1.00, bottom=0.08
        )  # Increase to add space between plot_trace_and_preds and GUI

    def setupDoubleAxesPlotLayout(self):
        """
        Setup for correction factors plots.
        """
        self.ax_top = self.fig.add_subplot(211)
        self.ax_btm = self.fig.add_subplot(212)

        self.axes = self.ax_top, self.ax_btm

        self.fig.subplots_adjust(hspace=0.30, wspace=0, left=0.02, right=0.98, bottom=0.09, top=0.98)

    def setupJointGridLayout(self):
        """
        Sets up a 2D-histogram layout similar to a seaborn JointGrid, but manually through matplotlib for compatibility reasons.
        """
        space_between = 0  # 0.01
        left, right = 0.08, 0.7
        bottom, height = 0.08, 0.7
        bottom_h = left_h = left + right + space_between

        rect_center = left, bottom, right, height
        rect_hist_top = left, bottom_h, right, 0.2
        rect_hist_right = left_h, bottom, 0.2, height

        self.ax_ctr = self.fig.add_axes(rect_center)
        self.ax_top = self.fig.add_axes(rect_hist_top)
        self.ax_rgt = self.fig.add_axes(rect_hist_right)

        self.axes = self.ax_ctr, self.ax_top, self.ax_rgt
        self.axes_marg = self.ax_top, self.ax_rgt

    def traceOutlineColor(self):
        """
        Updates the box outline and ticks for the traces displayer.
        """
        for ax in self.axes:
            ax.tick_params(axis="x", which="both", bottom=False, labelbottom=False)
            ax.yaxis.label.set_color(gvars.color_gui_text)

        if self.ax_setup != "bypass":
            self.ax_stoi.tick_params(axis="x", which="both", bottom=True, labelbottom=True)
            self.ax_stoi.set_xlabel("Frames")  # Assuming this is the bottom newTrace

    def get_window_title(self):  # overwrite class method for default image name
        return self.defaultImageName


class PlotWidget(QWidget):
    """
    Creates a wrapper around the canvas to add the matplotlib toolbar.
    The toolbar is hidden by default, and is only used for the save dialog.
    """

    def __init__(self, **kwargs):
        QWidget.__init__(self)
        self.setLayout(QVBoxLayout())
        self.canvas = MatplotlibCanvas(parent=self, **kwargs)

        # Visible set to False. Only using this to use the save file dialog from MPL
        self.toolbar = NavigationToolbar(self.canvas, self, coordinates=True)
        self.toolbar.setVisible(False)

        self.layout().addWidget(self.toolbar)
        self.layout().addWidget(self.canvas)

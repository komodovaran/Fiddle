import sys
from typing import List, Tuple, Union
import os
import time

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PyQt5.QtWidgets import *
from fbs_runtime.application_context.PyQt5 import ApplicationContext
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure, SubplotParams
from matplotlib.gridspec import GridSpec, GridSpecFromSubplotSpec

import lib.algorithms
import lib.utils
from ui._MainWindow import Ui_MainWindow


class Inputs:
    """
    Holds all the inputs from the GUI
    """

    n_examples: int
    n_traces: int
    trace_len: int
    max_random_states: int
    donor_lifetime: int
    acceptor_lifetime: int
    max_aggregate_size: int
    aggregate_prob: float
    scramble_prob: float
    blinking_prob: float

    transition_prob: Union[float, Tuple[float]]
    scaling_factor: Union[float, Tuple[float]]
    aa_mismatch: Union[float, Tuple[float]]
    bleed_through: Union[float, Tuple[float]]
    noise: Union[float, Tuple[float]]
    fret_means = Union[float, List[float]]


class ExportDialog(QFileDialog):
    """
    Custom export dialog to change labels on the accept button.
    Cancel button doesn't work for whatever reason on MacOS (Qt bug?).
    """

    def __init__(self, init_dir, accept_label="Accept"):
        super().__init__()
        self.setFileMode(self.DirectoryOnly)
        self.setLabelText(self.Accept, accept_label)
        self.setDirectory(init_dir)


class SheetInspector(QDialog):
    """
    Addon class for modal dialogs. Must be placed AFTER the actual PyQt superclass
    that the window inherits from.
    """

    def __init__(self, parent):
        super().__init__()
        self.setParent(parent)
        self.parent = parent
        self.setModal(True)
        self.setWindowFlag(5)  # Qt.Sheet

    def setInspectorConfigs(self, params):
        """
        Writes defaults for the Ui, by passing the params tuple from parent window
        """
        for key, new_val in zip(self.keys, params):
            self.setConfig(key, new_val)

    def connectUi(self, parent):
        """
        Connect Ui to parent functions. Override in parent
        """
        pass

    def setUi(self):
        """
        Setup UI according to last saved preferences. Override in parent
        """
        pass

    def returnInspectorValues(self):
        """
        Returns values from inspector window to be used in parent window
        """
        pass


class ProgressBar(QProgressDialog, SheetInspector):
    """
    Displays a progressbar, using known length of a loop.
    """

    def __init__(self, parent, loop_len=0):
        super().__init__(parent=parent)
        self.minimumSizeHint()
        self.setValue(0)
        self.setMinimum(0)
        # Corrected because iterations start from zero, but minimum length is 1
        self.setMaximum(loop_len)
        self.show()

    def increment(self):
        """
        Increments progress by 1
        """
        self.setValue(self.value() + 1)


class MainWindow(QMainWindow):
    """
    The main window that does everything
    """

    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.inputs = Inputs()
        self.canvas = PlotCanvas()
        self.ui.mpl_LayoutBox.addWidget(self.canvas)

        self.connect_ui()

        self.traces = pd.DataFrame()
        self.values_from_gui()

        self.show()

    def connect_ui(self):
        """Connectnumber interface"""
        # Connect all checkboxes dynamically
        [
            getattr(self.ui, c).clicked.connect(self.refresh_ui)
            for c in dir(self.ui)
            if c.startswith("checkBox")
        ]
        self.ui.pushButtonRefresh.clicked.connect(self.refresh_plots)
        self.ui.pushButtonExport.clicked.connect(self.export_traces_to_ascii)

    def refresh_ui(self):
        """Refreshes UI to e.g. disable some input boxes"""
        for inputBox, checkBox in (
            (self.ui.inputDonorMeanLifetime, self.ui.checkBoxDlifetime),
            (self.ui.inputAcceptorMeanLifetime, self.ui.checkBoxALifetime),
            (
                self.ui.inputTransitionProbabilityHi,
                self.ui.checkBoxTransitionProbability,
            ),
            (self.ui.inputFretStateMeans, self.ui.checkBoxRandomState),
            (self.ui.inputNoiseHi, self.ui.checkBoxNoise),
            (self.ui.inputMismatchHi, self.ui.checkBoxMismatch),
            (self.ui.inputScalerHi, self.ui.checkBoxScaler),
            (self.ui.inputBleedthroughHi, self.ui.checkBoxBleedthrough),
        ):
            inputBox.setDisabled(checkBox.isChecked())

        self.ui.inputMaxRandomStates.setEnabled(
            self.ui.checkBoxRandomState.isChecked()
        )

    def values_from_gui(self):
        """
        Fetch values from GUI
        """
        # Number of examples
        self.inputs.n_examples = int(
            self.ui.examplesComboBox.currentText().split("x")[0]
        )
        self.inputs.n_examples **= 2

        # Number of traces to export
        self.inputs.n_traces = int(self.ui.inputNumberOfTraces.value())

        # Trace length
        self.inputs.trace_len = int(self.ui.inputTraceLength.value())

        # Scramble probability
        self.inputs.scramble_prob = float(
            self.ui.inputScrambleProbability.value()
        )

        # Aggregation probability
        self.inputs.aggregate_prob = float(
            self.ui.inputAggregateProbability.value()
        )

        # Max aggregate size
        self.inputs.max_aggregate_size = int(
            self.ui.inputMaxAggregateSize.value()
        )

        # FRET state means
        if self.ui.checkBoxRandomState.isChecked():
            self.inputs.fret_means = "random"
        else:
            self.inputs.fret_means = lib.utils.numstring_to_ls(
                self.ui.inputFretStateMeans.text()
            )

        # Max number of random states
        self.inputs.max_random_states = int(
            self.ui.inputMaxRandomStates.value()
        )

        # Donor mean lifetime
        if self.ui.checkBoxDlifetime.isChecked():
            self.inputs.donor_lifetime = None
        else:
            self.inputs.donor_lifetime = int(
                self.ui.inputDonorMeanLifetime.value()
            )

        # Acceptor mean lifetime
        if self.ui.checkBoxALifetime.isChecked():
            self.inputs.acceptor_lifetime = None
        else:
            self.inputs.acceptor_lifetime = int(
                self.ui.inputAcceptorMeanLifetime.value()
            )

        # Blinking probability
        self.inputs.blinking_prob = float(
            self.ui.inputBlinkingProbability.value()
        )

        # Transition Probability
        if self.ui.checkBoxTransitionProbability.isChecked():
            self.inputs.transition_prob = float(
                self.ui.inputTransitionProbabilityLo.value()
            )
        else:
            self.inputs.transition_prob = (
                float(self.ui.inputTransitionProbabilityLo.value()),
                float(self.ui.inputTransitionProbabilityHi.value()),
            )

        # Noise
        if self.ui.checkBoxNoise.isChecked():
            self.inputs.noise = float(self.ui.inputNoiseLo.value())
        else:
            self.inputs.noise = (
                float(self.ui.inputNoiseLo.value()),
                float(self.ui.inputNoiseHi.value()),
            )

        # Acceptor-only mismatch
        if self.ui.checkBoxMismatch.isChecked():
            self.inputs.aa_mismatch = float(self.ui.inputMismatchLo.value())
        else:
            self.inputs.aa_mismatch = (
                float(self.ui.inputMismatchLo.value()),
                float(self.ui.inputMismatchHi.value()),
            )

        # Donor Bleedthrough
        if self.ui.checkBoxBleedthrough.isChecked():
            self.inputs.bleed_through = float(
                self.ui.inputBleedthroughLo.value()
            )
        else:
            self.inputs.bleed_through = (
                float(self.ui.inputBleedthroughLo.value()),
                float(self.ui.inputBleedthroughHi.value()),
            )

        # Scaler
        if self.ui.checkBoxScaler.isChecked():
            self.inputs.scaling_factor = float(self.ui.inputScalerLo.value())
        else:
            self.inputs.scaling_factor = (
                float(self.ui.inputScalerLo.value()),
                float(self.ui.inputScalerHi.value()),
            )

    def set_traces(self, n_traces):
        """Generate traces to show in the GUI or export"""
        if n_traces > 50:
            update_freq = 5
            progressbar = ProgressBar(
                parent=self, loop_len=n_traces / update_freq
            )
        else:
            update_freq = None
            progressbar = None

        self.traces = lib.algorithms.generate_traces(
            n_traces=n_traces,
            aa_mismatch=self.inputs.aa_mismatch,
            state_means=self.inputs.fret_means,
            random_k_states_max=self.inputs.max_random_states,
            max_aggregate_size=self.inputs.max_aggregate_size,
            aggregation_prob=self.inputs.aggregate_prob,
            scramble_prob=self.inputs.scramble_prob,
            trace_length=self.inputs.trace_len,
            trans_prob=self.inputs.transition_prob,
            blink_prob=self.inputs.blinking_prob,
            bleed_through=self.inputs.bleed_through,
            noise=self.inputs.noise,
            D_lifetime=self.inputs.donor_lifetime,
            A_lifetime=self.inputs.acceptor_lifetime,
            au_scaling_factor=self.inputs.scaling_factor,
            discard_unbleached=False,
            null_fret_value=-1,
            min_state_diff=0.2,
            acceptable_noise=0.25,
            progressbar_callback=progressbar,
            callback_every=update_freq,
        )

        if progressbar is not None:
            progressbar.close()

    def refresh_plots(self):
        """Refreshes preview plots"""
        self.values_from_gui()

        # generate at least enough traces to show required number of examples
        if self.inputs.n_traces < self.inputs.n_examples:
            self.inputs.n_traces = self.inputs.n_examples

        self.set_traces(self.inputs.n_examples)

        self.canvas.flush_events()
        self.canvas.fig.clear()

        n_subplots = self.inputs.n_examples
        nrows = int(self.inputs.n_examples ** (1 / 2))
        ncols = nrows
        outer_grid = GridSpec(nrows, ncols, wspace=0.1, hspace=0.1)  # 2x2 grid

        for i in range(n_subplots):
            trace = self.traces[self.traces["name"] == i]
            inner_subplot = GridSpecFromSubplotSpec(
                nrows=5,
                ncols=1,
                subplot_spec=outer_grid[i],
                wspace=0,
                hspace=0,
                height_ratios=[3, 3, 3, 3, 1],
            )
            axes = [
                plt.Subplot(self.canvas.fig, inner_subplot[n]) for n in range(5)
            ]
            ax_g_r, ax_red, ax_frt, ax_sto, ax_lbl = axes
            bleach = trace["_bleaches_at"].values[0]
            tmax = trace["frame"].max()
            fret_states = np.unique(trace["E_true"])
            fret_states = fret_states[fret_states != -1]

            ax_g_r.plot(trace["DD"], color="seagreen")
            ax_g_r.plot(trace["DA"], color="salmon")
            ax_red.plot(trace["AA"], color="red")
            ax_frt.plot(trace["E"], color="orange")
            ax_frt.plot(trace["E_true"], color="black", ls="-", alpha=0.3)

            for state in fret_states:
                ax_frt.plot([0, bleach], [state, state], color="red", alpha=0.2)

            ax_sto.plot(trace["S"], color="purple")

            lib.utils.plot_category(y=trace["label"], ax=ax_lbl, alpha=0.4)

            for ax in ax_frt, ax_sto:
                ax.set_ylim(-0.15, 1.15)

            for ax, s in zip((ax_g_r, ax_red), (trace["DD"], trace["AA"])):
                ax.set_ylim(s.max() * -0.15)
                ax.plot([0] * len(s), color="black", ls="--", alpha=0.5)

            for ax in axes:
                for spine in ax.spines.values():
                    spine.set_edgecolor("darkgrey")

                if bleach is not None:
                    ax.axvspan(bleach, tmax, color="black", alpha=0.1)

                ax.set_xticks(())
                ax.set_yticks(())
                ax.set_xlim(0, tmax)
                self.canvas.fig.add_subplot(ax)

        self.canvas.draw()

    def export_traces_to_ascii(self):
        """
        Opens a folder dialog to save traces to ASCII .txt files
        """
        self.set_traces(n_traces=int(self.ui.inputNumberOfTraces.value()))
        df = self.traces

        diag = ExportDialog(init_dir="~/Desktop/", accept_label="Export")

        if diag.exec():
            outdir = diag.selectedFiles()[0]
            appctxt.app.processEvents()
        else:
            outdir = None

        df.index = np.arange(0, len(df), 1) // int(
            self.ui.inputTraceLength.value()
        )

        if outdir is not None:
            for idx, trace in df.groupby(df.index):
                bg = np.zeros(len(trace))
                path = os.path.join(
                    outdir,
                    "trace_{}_{}.txt".format(idx, time.strftime("%Y%m%d_%H%M")),
                )

                df = pd.DataFrame(
                    {
                        "D-Dexc-bg": bg,
                        "A-Dexc-bg": bg,
                        "A-Aexc-bg": bg,
                        "D-Dexc-rw": trace["DD"],
                        "A-Dexc-rw": trace["DA"],
                        "A-Aexc-rw": trace["AA"],
                        "S": trace["S"],
                        "E": trace["E"],
                    }
                ).round(4)

                date_txt = "Date: {}".format(time.strftime("%Y-%m-%d, %H:%M"))
                mov_txt = "Movie filename: {}".format(None)
                id_txt = "FRET pair #{}".format(idx)
                bl_txt = "Bleaches at {}".format(trace["fb"].values[0])

                with open(path, "w") as f:
                    exp_txt = "Simulated trace exported by Fiddler"
                    f.write(
                        "{0}\n"
                        "{1}\n"
                        "{2}\n"
                        "{3}\n"
                        "{4}\n\n"
                        "{5}".format(
                            exp_txt,
                            date_txt,
                            mov_txt,
                            id_txt,
                            bl_txt,
                            df.to_csv(index=False, sep="\t"),
                        )
                    )


class PlotCanvas(FigureCanvas):
    """
    Instantiates the canvas and default layout and coloring
    """

    def __init__(self, parent=None, width=3, height=4, dpi=100):
        self.setup_canvas(parent=parent, width=width, height=height, dpi=dpi)
        self.default_layout()

    def setup_canvas(self, width, height, parent, dpi):
        """Setup canvas"""
        margin = 0.03
        subplotpars = SubplotParams(
            top=1 - margin,
            bottom=margin,
            left=margin,
            right=1 - margin,
            hspace=0,
            wspace=0,
        )

        self.fig = Figure(
            figsize=(width, height), dpi=dpi, subplotpars=subplotpars
        )
        self.fig.set_facecolor("#ECECEC")
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(
            self, QSizePolicy.Expanding, QSizePolicy.Expanding
        )
        FigureCanvas.updateGeometry(self)

    def default_layout(self):
        """Sets up the default layout before any examples are generated"""
        self.axes = [self.fig.add_subplot(111)]
        self.init_ax = self.axes[0]
        self.init_ax.set_xticks([])
        self.init_ax.set_yticks([])

        left, width = 0.25, 0.5
        bottom, height = 0.25, 0.5
        right = left + width
        top = bottom + height

        self.init_ax.text(
            x=0.5 * (left + right),
            y=0.5 * (bottom + top),
            s="Hit 'Refresh' to generate examples",
            horizontalalignment="center",
            verticalalignment="center",
            fontsize=14,
            color="darkgrey",
            transform=self.init_ax.transAxes,
        )

        for spine in self.init_ax.spines.values():
            spine.set_edgecolor("lightgrey")

        self.draw()


if __name__ == "__main__":
    appctxt = ApplicationContext()
    MainWindow_ = MainWindow()

    exit_code = appctxt.app.exec_()
    sys.exit(exit_code)

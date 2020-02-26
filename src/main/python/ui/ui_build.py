import os
import glob

def generatePyFromUi(verbose=True):
    """Add Qt .ui files in the same directory to convert to .py"""
    ui_files = glob.glob("*.ui")

    for filename in ui_files:
        if os.path.exists(filename):
            if verbose:
                print("{} was converted".format(filename))
            os.system("exec python3 -m PyQt5.uic.pyuic {0}.ui -o {0}.py -x".format(filename.rstrip(".ui")))

if __name__ == "__main__":
    generatePyFromUi()

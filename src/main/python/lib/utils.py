import re
import time
import os
import numpy as np
import itertools

def numstring_to_ls(s):
    """Transforms any string of numbers into a list of floats, regardless of separators"""
    num_s = re.findall(r'\d+(\.\d+)?\s*', s)
    return [float(s) for s in num_s]

def random_seed_mp(verbose=False):
    """Initializes a pseudo-random seed for multiprocessing use"""
    seed_val = int.from_bytes(os.urandom(4), byteorder="little")
    np.random.seed(seed_val)
    if verbose:
        print("Random seed value: {}".format(seed_val))


def timeit(method):
    """Decorator to time functions and methods for optimization"""
    def timed(*args, **kwargs):
        ts = time.time()
        result = method(*args, **kwargs)
        te = time.time()
        print("'{}' {:.2f} ms".format(method.__name__, (te - ts) * 1e3))
        return result
    return timed


def count_adjacent_values(arr):
    """
    Returns start index and length of segments of equal values.

    Example for plotting several axvspans:
    --------------------------------------
    adjs, lns = lib.count_adjacent_true(score)
    t = np.arange(1, len(score) + 1)

    for ax in axes:
        for starts, ln in zip(adjs, lns):
            alpha = (1 - np.mean(score[starts:starts + ln])) * 0.15
            ax.axvspan(xmin = t[starts], xmax = t[starts] + (ln - 1), alpha = alpha, color = "red", zorder = -1)
    """
    arr = arr.ravel()

    n = 0
    same = [(g, len(list(l))) for g, l in itertools.groupby(arr)]
    starts = []
    lengths = []
    for v, l in same:
        _len = len(arr[n : n + l])
        _idx = n
        n += l
        lengths.append(_len)
        starts.append(_idx)
    return starts, lengths


def plot_category(y, ax, alpha=0.2):
    """
    Plots a color for every class segment in a timeseries

    Parameters
    ----------
    y_:
        One-hot coded or categorical labels
    ax:
        Ax for plotting
    colors:
        Colors to cycle through
    """
    cls = {
        0: "bleached",
        1: "aggregate",
        2: "noisy",
        3: "scramble",
        4: "1-state",
        5: "2-state",
        6: "3-state",
        7: "4-state",
        8: "5-state",
    }

    colors = {0: "darkgrey",
              1: "red",
              2: "blue",
              3: "purple",
              4: "orange",
              5: "lightgreen",
              6: "green",
              7: "mediumseagreen",
              8: "darkolivegreen"}

    y_ = y.argmax(axis=1) if len(y.shape) != 1 else y
    y_ = y_.astype(int)  # type conversion to avoid float type labels
    if len(colors) < len(set(y_)):
        raise ValueError("Must have at least a color for each class")

    adjs, lns = count_adjacent_values(y_)
    position = range(len(y_))
    for idx, ln in zip(adjs, lns):
        label = y_[idx]
        ax.axvspan(
            xmin=position[idx],
            xmax=position[idx] + ln,
            alpha=alpha,
            facecolor=colors[label],
        )
    ax.plot([], label = cls[y_[0]], color = colors[y_[0]])
    ax.legend(loc = "upper right")


def min_none(ls):
    """Returns minimum value of list, and None if all elements are None"""
    try:
        return min(ls)
    except TypeError:
        return None
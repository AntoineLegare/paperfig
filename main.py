import matplotlib.pyplot as plt
from colorsys import hsv_to_rgb
from random import uniform
import numpy as np
import sys
from matplotlib.colors import LinearSegmentedColormap
import matplotlib as mpl
import matplotlib.gridspec as gridspec
from IPython.display import display


"""
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
Utilities
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""


def hex2rgb(hex_color):
    h = hex_color.lstrip('#')
    return np.array(tuple(int(h[i:i+2], 16) for i in (0, 2, 4))) / 255


def color_gradient(color1, color2, n_colors):
    colors = []
    for i in range(n_colors):
        alpha = i / (n_colors - 1)
        colors.append((1 - alpha) * np.array(color1) + alpha * np.array(color2))
    return colors


def generate_n_colors(nColors, saturation=80, value=90, randomness=0):
    h = np.linspace(0, 320, nColors)
    s = np.array([saturation + uniform(-randomness, randomness)] * nColors)
    v = np.array([value] * nColors)
    palette = []
    for i in range(nColors):
        palette.append(hsv_to_rgb(h[i] / 360, s[i] / 100, v[i] / 100))
    return palette


def set_boxplot_color(bp, color, linewidth=2, facecolor='none', markersize=5, marker='o'):
    for whisker in bp['whiskers']:
        whisker.set(color=color, linewidth=linewidth)
    for cap in bp['caps']:
        cap.set(color=color, linewidth=linewidth)
    for flier in bp['fliers']:
        flier.set(marker='.', color=color, alpha=1)
    for median in bp['medians']:
        median.set(color=color, linewidth=linewidth)
    for box in bp['boxes']:
        box.set(color=color, linewidth=linewidth)
        box.set(facecolor=facecolor)
    for flier in bp['fliers']:
        flier.set_marker(marker)
        flier.set_markerfacecolor(color)
        flier.set_markeredgecolor(color)
        flier.set_markersize(markersize)


def make_cmap(colors, position=None, bit=False):
    '''
    make_cmap takes a list of tuples which contain RGB values. The RGB
    values may either be in 8-bit [0 to 255] (in which bit must be set to
    True when called) or arithmetic [0 to 1] (default). make_cmap returns
    a cmap with equally spaced colors.
    Arrange your tuples so that the first color is the lowest value for the
    colorbar and the last is the highest.
    position contains values from 0 to 1 to dictate the location of each color.
    '''
    bit_rgb = np.linspace(0,1,256)
    if position == None:
        position = np.linspace(0,1,len(colors))
    else:
        if len(position) != len(colors):
            sys.exit("position length must be the same as colors")
        elif position[0] != 0 or position[-1] != 1:
            sys.exit("position must start with 0 and end with 1")
    if bit:
        for i in range(len(colors)):
            colors[i] = (bit_rgb[colors[i][0]],
                         bit_rgb[colors[i][1]],
                         bit_rgb[colors[i][2]])
    cdict = {'red':[], 'green':[], 'blue':[]}
    for pos, color in zip(position, colors):
        cdict['red'].append((pos, color[0], color[0]))
        cdict['green'].append((pos, color[1], color[1]))
        cdict['blue'].append((pos, color[2], color[2]))

    cmap = LinearSegmentedColormap('my_colormap', cdict, 256)
    return cmap


"""
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
Figure class
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""


class PaperFigure:

    def __init__(self, figsize=(7, 7), dpi=600):
        """
        Class to make multi-panel figures. Notebooks which use this class should run this import
        statement before: 'from IPython.display import display'.

        Arguments:
            figsize (tuple): Size of the figure (width followed by height, in inches). Recommended width: 7.
            dpi (integer): Resolution of the figure.
        """
        plt.ioff()
        plt.close('all')
        plt.ioff()
        self.set_tick_length()
        self.set_tick_pad()
        self.fig = plt.figure(figsize=figsize, dpi=dpi)
        self.ratio = figsize[1] / figsize[0]  # Height / Width
        self.dims = figsize
        self.grid_dims = (10000, int(10000 * self.ratio))
        self.xscale = self.grid_dims[0] / figsize[0]
        self.yscale = self.grid_dims[1] / figsize[1]
        self.gridspec = gridspec.GridSpec(self.grid_dims[1], self.grid_dims[0], figure=self.fig)
        self.axes = {}

    @property
    def keys(self):
        keys = list(self.axes.keys())
        if 'background' in keys:
            keys.remove('background')
        return keys

    def set_font_size(self, fontsize):
        plt.rcParams['font.size'] = fontsize

    def add_axes(self, label, position, width, height):
        """label: 1 character string (a, b, c, ...) to label the panel
           position: top left corner coordinates (fractional, between 0 and 1)
           width: width of the panel (fractional, between 0 and 1)
           height: height of the panel (fractional, between 0 and 1)"""
        x0, y0 = int(position[0] * self.xscale), int(position[1] * self.yscale)
        x1, y1 = x0 + int(width * self.xscale), y0 + int(height * self.yscale)
        self.axes[label] = self.fig.add_subplot(self.gridspec[y0:y1, x0:x1])

    def add_background(self):
        """Positions empty array as a white background. Useful when first figuring out the layout to get full figure output,
        but should be removed when saving the figure."""
        self.add_axes('background', (0, 0), self.dims[0], self.dims[1])
        self.axes['background'].axis('off')

    def remove_all_ticks(self):
        for key in self.keys:
            ax = self.axes[key]
            ax.set_xticks([])
            ax.set_yticks([])

    def set_tick_length(self, length=1.5):
        plt.rcParams['xtick.major.size'] = length
        plt.rcParams['xtick.minor.size'] = length
        plt.rcParams['ytick.major.size'] = length
        plt.rcParams['ytick.minor.size'] = length

    def set_tick_pad(self, pad=3):
        plt.rcParams['xtick.major.pad'] = pad
        plt.rcParams['ytick.major.pad'] = pad

    def set_line_thickness(self, thickness):
        for key in self.axes.keys():
            ax = self.axes[key]
            for spine in ax.spines.values():
                spine.set_linewidth(thickness)
            ax.tick_params(axis='both', which='major', width=thickness)
            ax.tick_params(axis='both', which='minor', width=thickness)

    def add_labels(self, ha='right', va='top', fontsize=14, weight='bold', padx=0.03, pady=0.01, labels=None):
        if labels is None:
            keys = self.keys
        else:
            keys = labels
        for key in keys:
            ax = self.axes[key]
            bbox = ax.get_position()
            x, y = bbox.x0, bbox.y1
            if len(key) == 1:
                self.fig.text(x - padx, y + pady, key, fontsize=fontsize, weight=weight, ha=ha, va=va)

    def show(self):
        display(self.fig)

    def save(self, path, pad=0):
        self.fig.savefig(path, bbox_inches='tight', pad_inches=pad)

    def close(self):
        self.fig.close()

    @staticmethod
    def get_cmap_color(cmap, value):
        """cmap: colormap string, value: number in range [0, 1]"""
        cmap = plt.cm.get_cmap(cmap)
        middle_color = cmap(value)
        color = mpl.colors.to_rgb(middle_color)
        return color
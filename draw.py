import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import style

from utils import *

# Paper specific settings
STANDARD_WIDTH = 17.8
SINGLE_COL_WIDTH = STANDARD_WIDTH / 2
DOUBLE_COL_WIDTH = STANDARD_WIDTH  # 一个图片里面放两个图


def cm_to_inch(value):
    return value / 2.54


# matplotlib style settings
matplotlib.rcParams['text.usetex'] = False
style.use('seaborn-white')
plt.rcParams["axes.grid"] = True
plt.rcParams["axes.grid.axis"] = "both"
plt.rcParams["grid.linewidth"] = 0.8
plt.rcParams['hatch.linewidth'] = 0.5
# plt.rcParams["font.family"] = "Nimbus Roman"
FONTSIZE = 8


# pd.options.display.max_columns = None
# pd.options.display.max_rows = None

def drawBar(dataMatrix, kindList, groupList):
    """
    竖着的小型柱状图
    :param dataMatrix: 二维数组，label数量 * 柱子组数
    :param kindList: 种类名列表 放在图例处
    :param groupList: 柱子组名列表 放在x轴处
    """
    if len(dataMatrix) != len(kindList):
        raise ValueError("dataMatrix and kindList should have the same length")
    if len(dataMatrix[0]) != len(groupList):
        raise ValueError("dataMatrix[0] and groupList should have the same length")

    fig = plt.figure(dpi=300, figsize=(cm_to_inch(SINGLE_COL_WIDTH), cm_to_inch(4.5)))
    # Reference: https://designbro.com/blog/inspiration/color-combinations/
    colors = ["#364F6B", "#3FC1C9", "#F5F5F5", "#FC5185"]
    # bar_width = 0.2
    barWidth = 1 / (len(kindList) + 1)
    patterns = ['///', '\\\\\\', '', 'XXX']

    xLabels = groupList
    xRange = list(range(1, len(xLabels) + 1))
    tot = len(kindList) * barWidth  # 一组柱子的总宽度

    for idx, fs in enumerate(kindList):
        points = []
        for pivot in xRange:
            barGroupStart = pivot - tot / 2 + barWidth / 2
            point = barGroupStart + idx * barWidth
            points.append(point)

        height = dataMatrix[idx]
        plt.bar(points, height, width=barWidth, hatch=patterns[idx], edgecolor='black', color=colors[idx])
    plt.yticks(np.arange(0, 4.1, 1))
    plt.ylim((0, 4.1))
    plt.xticks(xRange, labels=xLabels)

    plt.ylabel("Amplification", fontsize=FONTSIZE)
    plt.legend(kindList, loc='center', bbox_to_anchor=(0.5, 1.05), ncol=4, fontsize=6, columnspacing=0.8,
               handletextpad=0.1)
    # plt.xlabel(title_a, fontsize = 8, labelpad = 8)

    plt.tight_layout()
    plt.show()
    plt.savefig("./data/FIG-Filebench.pdf", bbox_inches='tight', pad_inches=0)


def drawTrace():
    lruRatio = 10
    labelList = ['DedupFS IO', 'SmartDedup IO', 'DedupFS GC', 'SmartDedup GC']
    dataMatrix = np.zeros((len(labelList), len(traceNameList)), dtype=float)
    print(dataMatrix.shape)

    for i, fs in enumerate(fsList):
        for j, trace in enumerate(traceNameList):
            amp = matchAmplification(f"{DATA_PATH}{fs}_{trace}.txt", 8 * GB >> 12)
            dataMatrix[i][j] = amp

    for i, fs in enumerate(fsList):
        for j, trace in enumerate(traceNameList):
            amp = matchGcAmplification(f"{DATA_PATH}{fs}_{trace}.txt")
            dataMatrix[i + 2][j] = amp
    drawBar(dataMatrix, labelList, list(map(lambda x: x.split('_')[0], traceNameList)))

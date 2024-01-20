import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import style
from config import IMG_PATH, PLT_SHOW

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
plt.rcParams["grid.color"] = "lightgray"
plt.rcParams["hatch.color"] = "black"
# plt.rcParams["font.family"] = "Nimbus Roman"

FONTSIZE = 8

colors1 = ['#8DD3C7', '#FFFFB3', '#BEBADA', '#FB8072']
patterns1 = ['///', '\\\\\\', '', 'XXX']


def setYTicks(dataMatrix, rangeCnt=3, setYTick=True, setYLim=True):
    """
    自动设置y轴刻度(从0开始), 如果不希望出现某种倍数的刻度, 可以调整函数中的基础刻度值
    :param dataMatrix: 数据矩阵
    :param rangeCnt: y轴刻度数量(不包括0)
    :param setYTick: 是否设置y轴刻度
    :param setYLim: 是否设置y轴范围
    :return: y轴刻度列表yTicks, y轴范围yLim
    """
    # 计算基础数据
    maxData = np.max(dataMatrix)
    baseTicks = np.array([1, 2, 3, 4, 5, 6, 8], dtype=float)  # 基础刻度
    ticks = []
    for i in range(-1, 3):
        ticks.extend(baseTicks * 10 ** i)
    ticks = np.array(ticks)
    diff = np.abs(ticks - maxData / rangeCnt)
    bestTick = ticks[np.argmin(diff)]

    # 计算y轴刻度
    yTicks = [i * bestTick for i in range(rangeCnt + 1)]
    if yTicks[-1] < maxData:
        yLim = bestTick * (rangeCnt + 1)
        yTicks.append(yLim)
    else:
        yLim = bestTick * rangeCnt
    yLim *= 1.1  # 留出一点空间

    # 设置y轴刻度
    if setYTick:
        plt.yticks(yTicks, fontsize=FONTSIZE)
    if setYLim:
        plt.ylim((0, yLim))

    return yTicks, yLim


def showPlt(pltName: str):
    """
    显示或保存图表
    :param pltName: 图表名 将会保存在IMG_PATH下
    """
    if PLT_SHOW:
        plt.show()
    else:
        plt.savefig(f"{IMG_PATH}{pltName}.pdf", bbox_inches='tight', pad_inches=0.1)


def getPointsMatrix(nGroup, nLabel):
    """
    获取每组label柱子的位置
    :param nGroup: 柱子组数
    :param nLabel: 每组柱子有几根, 即label数量
    :return: pointsMatrix, barWidth, xRange
    """
    barWidth = 1 / (nLabel + 1)
    xRange = list(range(1, nGroup + 1))
    tot = nLabel * barWidth  # 一组柱子的总宽度

    pointsMatrix = []
    for idx in range(nLabel):
        points = []
        for pivot in xRange:
            barGroupStart = pivot - tot / 2 + barWidth / 2
            point = barGroupStart + idx * barWidth
            points.append(point)
        pointsMatrix.append(points)

    return pointsMatrix, barWidth, xRange


# TODO: 解析文件的函数

def drawBar(dataMatrix, kindList, groupList, colors=None, patterns=None,
            xTicks=True, yTicks=True, xLabel=None, yLabel=None, legend=True):
    """
    竖着的小型柱状图
    :param dataMatrix: 二维数组，label数量 * 柱子组数
    :param kindList: 种类名列表 放在图例处
    :param groupList: 柱子组名列表 放在x轴处
    :param colors: 柱子颜色列表
    :param patterns: 柱子填充图案列表
    :param xTicks: 是否需要x轴刻度
    :param yTicks: 是否需要y轴刻度
    :param xLabel: x轴标签
    :param yLabel: y轴标签
    :param legend: 是否需要图例
    """
    shape = dataMatrix.shape
    if len(shape) != 2:
        raise ValueError("dataMatrix should be 2D")
    if shape != (len(kindList), len(groupList)):
        raise ValueError(f"shape{shape} != (len(kindList), len(groupList)){(len(kindList), len(groupList))}")

    # Reference: https://designbro.com/blog/inspiration/color-combinations/
    if colors is None:
        # colors = ["#364F6B", "#3FC1C9", "#AFFFFF", "#FC5185"]
        colors = colors1
    if patterns is None:
        # patterns = ['///', '\\\\\\', '', 'XXX']
        patterns = patterns1

    pointsMatrix, barWidth, xRange = getPointsMatrix(len(groupList), len(kindList))
    for idx in range(len(kindList)):
        plt.bar(pointsMatrix[idx], dataMatrix[idx], width=barWidth, color=colors[idx], hatch=patterns[idx],
                edgecolor='black', linewidth=0.5)

    # 设置x轴刻度和图例
    if xTicks:
        plt.xticks(xRange, labels=groupList, fontsize=FONTSIZE)
    if yTicks:
        setYTicks(dataMatrix)
    if xLabel is not None:
        plt.xlabel(xLabel, fontsize=FONTSIZE)
    if yLabel is not None:
        plt.ylabel(yLabel, fontsize=FONTSIZE)
    if legend:
        plt.legend(kindList, loc='center', bbox_to_anchor=(0.5, 1.05), ncol=4, fontsize=6, columnspacing=0.8,
                   handletextpad=0.1)
    # 设置边框宽度
    ax = plt.gca()
    lw = 0.5
    for axis in ['top', 'bottom', 'left', 'right']:
        ax.spines[axis].set_linewidth(lw)


class drawMultiChart:
    """
    绘制多个图表
    """
    nLine: int  # 行数
    nCol: int  # 列数
    lineCnt: int  # 当前画到第几行

    # kindList: list[str]
    # groupList: list[str]

    def __init__(self, nLine, nCol):
        self.nLine = nLine
        self.nCol = nCol
        self.lineCnt = 0

    def drawBarLine(self, dataMatrix, kindList, groupList, colors=None, patterns=None,
                    xTicks=True, yTicks=True, xLabel=None, yLabel=None, legend=False):
        """
        纵向的柱状图, 画一行多个图
        :param dataMatrix: 三维数组 图的数量 * label数量 * 柱子组数
        :param kindList: 种类名列表 放在图例处
        :param groupList: 柱子组名列表 放在x轴处
        :param colors: 柱子颜色列表
        :param patterns: 柱子填充图案列表
        :param xTicks: 是否需要x轴刻度
        :param yTicks: 是否需要y轴刻度
        :param xLabel: x轴标签, 可以是字符串或者列表
        :param yLabel: y轴标签
        :param legend: 是否需要图例
        """
        # https://github.com/Light-Dedup/tests/blob/4e2c27df7948d9cf8024b0226905fde89797d238/FIG7_FIO/plot.ipynb#L28
        shape = dataMatrix.shape
        if len(shape) != 3:
            raise ValueError("dataMatrix should be 3D")
        if shape != (self.nCol, len(kindList), len(groupList)):
            raise ValueError(f"shape{shape} !="
                             f"(self.nCol, kindList, groupList){(self.nCol, len(kindList), len(groupList))}")
        for i in range(shape[0]):
            plt.subplot(self.nLine, self.nCol, i + 1 + self.lineCnt * self.nCol)

            xStr = xLabel
            if i != 0:
                xStr = None
                yLabel = None
            if hasattr(xLabel, '__getitem__'):
                xStr = xLabel[i]

            drawBar(dataMatrix[i], kindList, groupList, colors=colors, patterns=patterns,
                    xTicks=xTicks, yTicks=yTicks, xLabel=xStr, yLabel=yLabel, legend=legend)

        self.lineCnt += 1

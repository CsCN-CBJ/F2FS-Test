import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import style

# draw settings
DATA_PATH = "./data/"
IMG_PATH = "./data/0pics/"

# Paper specific settings
STANDARD_WIDTH = 17.8
SINGLE_COL_WIDTH = STANDARD_WIDTH / 2
DOUBLE_COL_WIDTH = STANDARD_WIDTH  # 一个图片里面放两个图


def cm_to_inch(value):
    return value / 2.54


matplotlib.use('TkAgg')
# matplotlib style settings
matplotlib.rcParams['text.usetex'] = False
# style.use('seaborn-white')
style.use('bmh')
plt.rcParams["axes.grid"] = True
plt.rcParams["axes.grid.axis"] = "both"
plt.rcParams["grid.linewidth"] = 0.8
plt.rcParams['hatch.linewidth'] = 0.5
plt.rcParams["grid.color"] = "lightgray"
plt.rcParams["hatch.color"] = "black"
plt.rcParams["font.family"] = "Times New Roman"
# matplotlib.rc("font", family='MicroSoft YaHei')

FONTSIZE = 8
plt.rcParams.update({"font.size": FONTSIZE})  # 默认字号

# Reference: https://coolors.co/palettes/popular/6%20colors
# colors1 = ['#8DD3C7', '#FFFFB3', '#BEBADA', '#FB8072', '#80B1D3']
colors1 = list(plt.get_cmap('tab10').colors)
patterns1 = ['///', '\\\\\\', '', 'XXX', 'OOO', '---', '+++', '***', '...', '+++']
line_styles = ['-', '--', '-.', ':', '-', '--']
markers = [">", "x", "o", "s", "D", "+", "v", "<", "d", "^", "p", "h", "H", "X", "*", "|", "_"]


def setYTicks(dataMatrix, setYTick=True, setYLim=True, tickCntList=None):
    """
    自动设置y轴刻度(从0开始), 如果不希望出现某种倍数的刻度, 可以调整函数中的基础刻度值
    :param dataMatrix: 数据矩阵
    :param setYTick: 是否设置y轴刻度
    :param setYLim: 是否设置y轴范围
    :param tickCntList: y轴刻度数量可选值(不包括0) 默认为[3, 4]
    :return: y轴刻度列表yTicks, y轴范围yLim
    """
    # 计算基础数据
    maxData = np.max(dataMatrix)
    tickCntList = [3, 4] if tickCntList is None else tickCntList
    tickList = np.array([1, 2, 3, 5], dtype=float)  # 基础刻度
    rangeList = list(range(-1, 5))
    ticks = []
    for i in rangeList:
        ticks.extend(tickList * 10 ** i)
    ticks = np.array(ticks)
    diff = np.concatenate(list(ticks - maxData / tickCnt for tickCnt in tickCntList))
    bestIndex = np.where(diff >= 0, diff, np.inf).argmin()  # 选出最小正数
    bestTick = ticks[bestIndex % len(ticks)]
    tickCnt = tickCntList[bestIndex // len(ticks)]

    # 计算y轴刻度
    yTicks = [i * bestTick for i in range(tickCnt + 1)]
    yLim = bestTick * tickCnt
    yLim *= 1.1  # 留出一点空间

    # 设置y轴刻度
    if setYTick:
        plt.yticks(yTicks, fontsize=FONTSIZE)
    if setYLim:
        plt.ylim((0, yLim))

    return yTicks, yLim


def showPlt(pltName: str, show=False, pathPrefix=IMG_PATH):
    """
    显示或保存图表
    :param pltName: 图表名, 自动加上.pdf后缀和前缀路径
    :param show: 是否显示图表
    :param pathPrefix: 保存路径前缀
    """
    if show:
        plt.show()
    else:
        path = f"{pathPrefix}{pltName}.pdf"
        print(f"save to {path}")
        plt.savefig(path, bbox_inches='tight', pad_inches=0.1)


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


def defaultLegend(fig, ncol, height=1.15):
    fig.legend(loc='upper center', ncol=ncol, fontsize=FONTSIZE, bbox_to_anchor=(0.5, height),
               columnspacing=0.8, handletextpad=0.1, labelspacing=0.1, handlelength=1.5)


def setAxisWidth(lw=0.5):
    """
    设置坐标轴边框宽度
    :param lw: 宽度
    :return: None
    """
    ax = plt.gca()
    for axis in ['top', 'bottom', 'left', 'right']:
        ax.spines[axis].set_linewidth(lw)


# TODO: 解析文件的函数

def drawBar(dataMatrix, kindList, groupList, colors=None, patterns=None,
            xTicks=True, yTicks=True, xLabel=None, yLabel=None, legend=True, noLegend=False):
    """
    竖着的小型柱状图
    :param dataMatrix: 二维数组，label数量 * 柱子组数
    :param kindList: 种类名列表 放在图例处
    :param groupList: 柱子组名列表 放在x轴处
    :param colors: 柱子颜色列表
    :param patterns: 柱子填充图案列表
    :param xTicks: 是否需要x轴刻度
    :param yTicks: 是否需要y轴刻度, 可以传入True自动生成, 也可以传入列表
    :param xLabel: x轴标签
    :param yLabel: y轴标签
    :param legend: 是否需要图例
    :param noLegend: 是否需要在图例中忽略当前线条 注意在调用plt.legend时不要再传入kindList
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
        rects = plt.bar(pointsMatrix[idx], dataMatrix[idx],
                        color=colors[idx], hatch=patterns[idx],
                        width=barWidth - 0.05, linewidth=0.5,
                        label="_noLegend_" if noLegend else kindList[idx],
                        alpha=.99  # for bug: https://stackoverflow.com/questions/5195466
                        )
        # 在柱子上面标数据
        # for i, rect in enumerate(rects):
        #     height = dataMatrix[idx][i]
        #     plt.text(rect.get_x() + rect.get_width() / 2, height + np.random.random(1) / 2,
        #              f"{height:.2f}", size=3, ha='center', va='bottom')

    # 设置x轴刻度和图例
    if xTicks:
        plt.xticks(xRange, labels=groupList, fontsize=FONTSIZE)
    if yTicks is True:
        setYTicks(dataMatrix)
    elif yTicks:
        plt.yticks(yTicks, fontsize=FONTSIZE)
    if xLabel is not None:
        plt.xlabel(xLabel, fontsize=FONTSIZE)
    if yLabel is not None:
        plt.ylabel(yLabel, fontsize=FONTSIZE)
    if legend:
        defaultLegend(plt, len(kindList))

    # 设置边框宽度
    setAxisWidth()


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
                    xTicks=True, yTicks=True, xLabel=None, yLabel=None, legend=False, noLegend=False):
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
        :param noLegend: 是否需要在图例中忽略当前线条 注意在调用plt.legend时不要再传入kindList
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
                    xTicks=xTicks, yTicks=yTicks, xLabel=xStr, yLabel=yLabel,
                    legend=legend, noLegend=(i != 0) or noLegend)

        self.lineCnt += 1

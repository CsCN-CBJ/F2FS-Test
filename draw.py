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
plt.rcParams["grid.color"] = "lightgray"
plt.rcParams["hatch.color"] = "black"
# plt.rcParams["font.family"] = "Nimbus Roman"
FONTSIZE = 8

colors1 = ['#8DD3C7', '#FFFFB3', '#BEBADA', '#FB8072']
patterns1 = ['///', '\\\\\\', '', 'XXX']


# pd.options.display.max_columns = None
# pd.options.display.max_rows = None

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


def drawTraceFixed():
    labelList = ['H2C-Dedup IO', 'SmartDedup IO', 'H2C-Dedup GC', 'SmartDedup GC']
    dataMatrix = np.zeros((len(labelList), len(traceList)), dtype=float)
    print(dataMatrix.shape)
    plt.rcParams["axes.grid.axis"] = "y"

    for i, fs in enumerate(fsList):
        for j, trace in enumerate(traceFileBaseNameList):
            fileName = f"{DATA_PATH}{fs}_{trace}_fixed{fixedLRU}.txt"
            amp = matchAmplification(fileName, traceSize >> 12)
            dataMatrix[i][j] = amp
            amp = matchGcAmplification(fileName)
            dataMatrix[i + 2][j] = amp

    # 画出草图
    plt.figure(dpi=300, figsize=(cm_to_inch(SINGLE_COL_WIDTH), cm_to_inch(4)))  # 纵向小一点 跟别的图对齐
    drawBar(dataMatrix, labelList, traceNameList,
            xLabel="Workloads", yLabel="Amplification", legend=False)
    plt.legend(labelList, loc='upper center', ncol=4, fontsize=6, bbox_to_anchor=(0.5, 1.25), columnspacing=0.8,
               handletextpad=0.1)
    plt.tight_layout()
    showPlt("TraceFixed")


def drawTraceLife():
    labelList = ['F2FS', 'smartdedup', 'DedupFS', 'ideal']
    dataMatrix = np.ones((len(traceList), len(labelList), len(lruRatios)), dtype=float)
    plt.rcParams["axes.grid.axis"] = "y"

    for i, trace in enumerate(traceFileBaseNameList):
        # F2FS默认为1 不需要计算

        # 理想情况
        dataMatrix[i][3] = 1 / (1 - dups[i])

        # 两种dedup的计算
        for j, fs in enumerate(labelList[1:-1]):
            for k, lruRatio in enumerate(lruRatios):
                fileName = f"{DATA_PATH}{fs}_{trace}_{lruRatio}.txt"
                amp = matchAmplification(fileName, traceSize >> 12)
                amp *= matchGcAmplification(fileName)
                t = 1 / ((1 - dups[i]) * amp)
                dataMatrix[i][j + 1][k] = t

    # 画图
    fig = plt.figure(dpi=300, figsize=(cm_to_inch(SINGLE_COL_WIDTH * 3), cm_to_inch(4.5)))
    draw = drawMultiChart(1, len(traceFileBaseNameList))
    xLabels = [f"Cache Ratio(%)\n\n({chr(ord('a') + i)}) {traceNameList[i]}" for i in range(len(traceNameList))]
    draw.drawBarLine(dataMatrix, labelList, list(map(str, lruRatios)),
                     xLabel=xLabels, yLabel="Normalized Life Span", legend=False)
    fig.legend(['F2FS', 'SmartDedup', 'H2C-Dedup', 'ideal'], loc='upper center', ncol=4, fontsize=8,
               bbox_to_anchor=(0.5, 1.05), columnspacing=0.8, handletextpad=0.4)
    plt.tight_layout()
    showPlt("TraceLife")


def drawFIOFixed():
    lruRatio = 5
    labelList = ['H2C-Dedup IO', 'SmartDedup IO', 'H2C-Dedup GC', 'SmartDedup GC']
    dataMatrix = np.zeros((len(labelList), len(dupRatios)), dtype=float)

    # 解析数据
    for i, fs in enumerate(fsList):
        for j, dupRatio in enumerate(dupRatios):
            fileName = f"{DATA_PATH}{fs}_{dupRatio}_fixed{lruRatio}.txt"
            amp = matchAmplification(fileName, TOTAL_WRITE >> 12)
            dataMatrix[i][j] = amp
            amp = matchGcAmplification(fileName)
            dataMatrix[i + 2][j] = amp

    # 画图
    plt.figure(dpi=300, figsize=(cm_to_inch(SINGLE_COL_WIDTH), cm_to_inch(4.5)))
    drawBar(dataMatrix, labelList, list(map(str, dupRatios)),
            xLabel="Duplication ratio (%)", yLabel="Amplification")
    plt.tight_layout()
    showPlt("FIOFixed")


def drawFIOAllDouble():
    labelList = ['H2C-Dedup IO', 'SmartDedup IO', 'H2C-Dedup GC', 'SmartDedup GC']
    dataMatrix = np.zeros((len(dupRatios), len(labelList), len(lruRatios)), dtype=float)

    # 解析数据
    for i, dupRatio in enumerate(dupRatios):
        for j, fs in enumerate(fsList):
            for k, lruRatio in enumerate(lruRatios):
                fileName = f"{DATA_PATH}{fs}_{dupRatio}_{lruRatio}.txt"
                amp = matchAmplification(fileName, TOTAL_WRITE >> 12)
                dataMatrix[i][j][k] = amp
                amp = matchGcAmplification(fileName)
                dataMatrix[i][j + 2][k] = amp

    fig = plt.figure(dpi=300, figsize=(cm_to_inch(SINGLE_COL_WIDTH * 3), cm_to_inch(6)))
    draw = drawMultiChart(2, len(dupRatios))
    xLabels = [f"Cache Ratio(%)\n\n({chr(ord('a') + i)}) duplication ratio: {dupRatios[i]}%"
               for i in range(len(dupRatios))]
    draw.drawBarLine(dataMatrix[:, :2], labelList[:2], lruRatios, colors=colors1[:2], patterns=patterns1[:2],
                     yLabel="IO Amp.")
    draw.drawBarLine(dataMatrix[:, 2:], labelList[2:], lruRatios, colors=colors1[2:], patterns=patterns1[2:],
                     yLabel="GC Amp.", xLabel=xLabels)
    fig.legend(labelList, loc='upper center', ncol=4, fontsize=8, bbox_to_anchor=(0.5, 1.05), columnspacing=0.8,
               handletextpad=0.1)
    plt.tight_layout()
    showPlt("FIOAll")


def drawTraceAllDouble():
    labelList = ['H2C-Dedup IO', 'SmartDedup IO', 'H2C-Dedup GC', 'SmartDedup GC']
    dataMatrix = np.zeros((len(traceFileBaseNameList), len(labelList), len(lruRatios)), dtype=float)
    # 解析数据
    for i, trace in enumerate(traceFileBaseNameList):
        for j, fs in enumerate(fsList):
            for k, lruRatio in enumerate(lruRatios):
                fileName = f"{DATA_PATH}{fs}_{trace}_{lruRatio}.txt"
                amp = matchAmplification(fileName, traceSize >> 12)
                dataMatrix[i][j][k] = amp
                amp = matchGcAmplification(fileName)
                dataMatrix[i][j + 2][k] = amp

    fig = plt.figure(dpi=300, figsize=(cm_to_inch(SINGLE_COL_WIDTH * 3), cm_to_inch(6)))
    draw = drawMultiChart(2, len(traceFileBaseNameList))
    xLabels = [f"Cache Ratio(%)\n\n({chr(ord('a') + i)}) {traceNameList[i]}" for i in range(len(traceNameList))]
    draw.drawBarLine(dataMatrix[:, :2], labelList[:2], lruRatios, colors=colors1[:2], patterns=patterns1[:2],
                     yLabel="IO Amp.")
    draw.drawBarLine(dataMatrix[:, 2:], labelList[2:], lruRatios, colors=colors1[2:], patterns=patterns1[2:],
                     yLabel="GC Amp.", xLabel=xLabels)
    fig.legend(labelList, loc='upper center', ncol=4, fontsize=8, bbox_to_anchor=(0.5, 1.05), columnspacing=0.8,
               handletextpad=0.1)
    plt.tight_layout()
    showPlt("TraceAll")


def drawCdf():
    fig = plt.figure(dpi=300, figsize=(6, 3))
    subfig = plt.subplot(1, 2, 1)
    global FONTSIZE  # 应该不用global吧
    FONTSIZE = 12
    for i in range(len(traceNameList)):
        baseName = traceFileBaseNameList[i].split('_')[0]
        with open(f"{DATA_PATH}hashCount/{baseName}.txt", 'r') as f:
            values = eval(f.read())
        pdf = np.zeros(max(values) + 1)  # 横轴为频数(1 到 最大频数), 0号位置就放一个0
        for value in values:
            pdf[value] += 1  # 该频数占总频数的比例, 确保pdf总和为sum(values), 即总的哈希值个数

        # 计算cdf
        cdf = np.cumsum(pdf) / sum(pdf)
        # 画图
        plt.plot(np.arange(len(cdf)), cdf, label=baseName)

    # subfig.text(18, -0.1, "repeated hash count", ha='center', va='center', fontsize=FONTSIZE-1)
    plt.xlabel("reference count\n(a) CDF of reference count values", fontsize=FONTSIZE, labelpad=8)
    plt.ylabel('Probability', fontsize=FONTSIZE)
    plt.ylim((0, 1.1))
    xMax = 200
    plt.xlim((-xMax // 20, xMax))
    plt.legend(traceNameList, fontsize=FONTSIZE)

    subfig = plt.subplot(1, 2, 2)
    for i in range(len(traceNameList)):
        baseName = traceFileBaseNameList[i].split('_')[0]
        with open(f"{DATA_PATH}refDistance/{baseName}.txt", 'r') as f:
            values = eval(f.read())
        pdf = np.zeros(max(values) + 1)  # 横轴为频数(1 到 最大频数), 0号位置就放一个0
        for value in values:
            pdf[value] += 1  # 该频数占总频数的比例, 确保pdf总和为sum(values), 即总的哈希值个数

        # 计算cdf
        cdf = np.cumsum(pdf) / sum(pdf)
        # 画图
        plt.plot(np.arange(len(cdf)), cdf, label=baseName)

    # subfig.text(40, -0.1, "distance", ha='center', va='center', fontsize=FONTSIZE-1)
    plt.xlabel("distance\n(b) CDF of modification distances", fontsize=FONTSIZE, labelpad=8)
    plt.ylabel('Probability', fontsize=FONTSIZE)
    plt.ylim((0, 1.1))
    xMax = 1000
    plt.xlim((-xMax // 20, xMax))

    plt.legend(traceNameList, fontsize=FONTSIZE)
    plt.tight_layout()
    showPlt("TraceAnalysis")


def drawBarh(wCnt, idealRef, dedupRef, idealMeta, dedupMeta, ssdCnt, gcCnt, origin):
    fig = plt.figure(dpi=300, figsize=(cm_to_inch(SINGLE_COL_WIDTH), cm_to_inch(3)))
    bar_width = 0.5
    # Reference: https://coolors.co/palettes/popular/6%20colors
    # colors = ["#74DBEF", "#2EB872", "#F9A828", "#5E88FC", "#F38181"]
    colors = colors1
    patterns = ['///', '\\\\\\', 'XXX', "OOO", "///"]
    fss = ['SmartDedup', 'Ideal Deduplication ', 'Non-deduplication']  # 柱子的类别
    labelList = ["data", "FP metadata", "ref metadata", "SSD GC"]

    dataMatrix = [
        [wCnt, dedupMeta, dedupRef, gcCnt, 0],
        [wCnt, idealMeta, idealRef, 0, 0],
        [origin, 0, 0, 0, 0],
    ]
    dataMatrix = np.array(dataMatrix) / 256 / 1024

    xRange = list(range(1, len(fss) + 1))
    for fsIdx, fs in enumerate(fss):
        left = 0
        pivot = xRange[fsIdx]
        for labelIdx in range(len(labelList)):
            width = dataMatrix[fsIdx][labelIdx]
            plt.barh(y=pivot, width=width, color=colors[labelIdx], edgecolor='black', left=left,
                     height=bar_width, hatch=patterns[labelIdx], linewidth=0.5)
            plt.ylim((0.3, 3.7))
            left = left + width

    plt.xlabel('Write to disk (GB)', fontsize=FONTSIZE)
    plt.yticks(xRange, labels=fss, fontsize=FONTSIZE)
    fig.legend(labelList, loc='upper center', bbox_to_anchor=(0.55, 1.1), ncol=len(labelList), frameon=False,
               columnspacing=1, handletextpad=0.2, labelspacing=1, fontsize=7)
    # plt.xlim((0, 6e6))
    ax = plt.gca()
    lw = 0.5
    for axis in ['top', 'bottom', 'left', 'right']:
        ax.spines[axis].set_linewidth(lw)
    plt.tight_layout()
    showPlt("2Amp")


def match_and_draw_barh(fmtPath, dupRatio):
    dedupFS = fmtPath.format("DedupFS")
    smartdedup = fmtPath.format("smartdedup")
    print(smartdedup)
    with open(dedupFS, "r") as f:
        dedup_content = f.read()
    with open(smartdedup, "r") as f:
        smart_content = f.read()

    origin = matchFirstInt(r"total_write_count (\d+)", dedup_content)
    wCnt = int(matchFirstInt(r"total_write_count (\d+)", dedup_content) * (1 - dupRatio))
    idealRef = matchFirstInt(r"global_ref_write_count (\d+)", dedup_content)
    idealMeta = matchFirstInt(r"change_to_disk_count (\d+)", dedup_content)
    dedupRef = matchFirstInt(r"total_num_enter_write_ref_file (\d+)", smart_content)
    dedupMeta = matchFirstInt(r"change_to_disk_count (\d+)", smart_content)
    dedupAll = matchFirstInt(r"total_num_enter_write_metadata_func (\d+)", smart_content)
    assert dedupAll == dedupRef + dedupMeta

    ssdCnt = int(re.findall(r"normal_wPage_count: (\d+)", smart_content)[-1])
    gcCnt = int(re.findall(r"gc_wPage_count: (\d+)", smart_content)[-1])

    drawBarh(wCnt, idealRef, dedupRef, idealMeta, dedupMeta, ssdCnt, gcCnt, origin)


def drawSpeed():
    rounds = 10  # 跑的轮数
    fsList = ["DedupFS", "smartdedup", "f2fs"]
    dataMatrix = np.zeros((len(fsList), len(dupRatios), rounds), dtype=float)
    for r in range(rounds):
        for dupIdx, dupRatio in enumerate(dupRatios):
            for fsIdx, fs in enumerate(fsList):
                fileName = f"{DATA_PATH}{fs}_{dupRatio}_t{r}.json"
                speed = matchSpeed(fileName)
                dataMatrix[fsIdx][dupIdx][r] = speed

    fig = plt.figure(dpi=300, figsize=(cm_to_inch(SINGLE_COL_WIDTH * 1.5), cm_to_inch(4.5)))
    plt.subplot(1, 2, 1)
    pointsMatrix, barWidth, xRange = getPointsMatrix(len(dupRatios), len(fsList))
    for idx in range(len(fsList)):
        error = np.std(dataMatrix[idx], axis=1)
        plt.bar(pointsMatrix[idx], np.mean(dataMatrix[idx], axis=1), width=barWidth, color=colors1[idx],
                edgecolor='black',
                hatch=patterns1[idx], linewidth=0.5, yerr=error[idx],
                error_kw={'elinewidth': 0.5, 'ecolor': 'black', 'capsize': 1.5, 'capthick': 0.5})
    ax = plt.gca()
    lw = 0.5
    for axis in ['top', 'bottom', 'left', 'right']:
        ax.spines[axis].set_linewidth(lw)
    plt.xticks(xRange, labels=dupRatios)
    # plt.ylim((0, 30000))
    # plt.yticks(np.arange(200, 450 + 1, 50), fontsize=FONTSIZE)
    plt.xlabel("Duplication ratio (%)\n\n(a)Write Throughput", fontsize=FONTSIZE)
    plt.ylabel("Throughput (MB/s)", fontsize=FONTSIZE)

    plt.subplot(1, 2, 2)
    dataMatrix = np.zeros((len(fsList), len(dupRatios), rounds), dtype=float)
    for r in range(rounds):
        for dupIdx, dupRatio in enumerate(dupRatios):
            for fsIdx, fs in enumerate(fsList):
                fileName = f"{DATA_PATH}{fs}_{dupRatio}_t{r}.json"
                speed = matchLatency99(fileName)
                dataMatrix[fsIdx][dupIdx][r] = speed
    dataMatrix /= 1000
    boxes = []

    pointsMatrix, barWidth, xRange = getPointsMatrix(len(dupRatios), len(fsList))
    for idx in range(len(fsList)):
        box = plt.boxplot(dataMatrix[idx].T,
                          positions=pointsMatrix[idx],
                          patch_artist=True,
                          showfliers=False,
                          widths=barWidth,
                          boxprops={'color': 'black', 'facecolor': colors1[idx], 'hatch': patterns1[idx],
                                    'linewidth': 0.5},
                          medianprops={'linewidth': 0.6, 'color': '#FB8072'},
                          whiskerprops={'linewidth': 0.5, 'color': 'black'},
                          capprops={'linewidth': 0.5, 'color': 'black'},
                          )
        boxes.append(box['boxes'][0])
    ax = plt.gca()
    lw = 0.5
    for axis in ['top', 'bottom', 'left', 'right']:
        ax.spines[axis].set_linewidth(lw)
    fig.legend(handles=boxes, labels=["H2C-Dedup", "SmartDedup", "F2FS"], loc='upper center', ncol=3, fontsize=FONTSIZE,
               bbox_to_anchor=(0.5, 1.05),
               columnspacing=0.8,
               handletextpad=0.1)
    plt.xticks(xRange, labels=dupRatios)
    # plt.ylim((0, 30000))
    # plt.yticks(np.arange(200, 450 + 1, 50), fontsize=FONTSIZE)
    plt.xlabel("Duplication ratio (%)\n\n(b)99% Write Latency", fontsize=FONTSIZE)
    plt.ylabel("Latency (us)", fontsize=FONTSIZE)
    plt.tight_layout()
    showPlt("Speed")


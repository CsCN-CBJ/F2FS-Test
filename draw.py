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

colors1 = ['#8DD3C7', '#FFFFB3', '#BEBADA', '#FB8072']
patterns1 = ['///', '\\\\\\', '', 'XXX']


# pd.options.display.max_columns = None
# pd.options.display.max_rows = None

def setYTicks(dataMatrix, rangeCnt=3, setYTick=True, setYLim=True):
    """
    自动设置y轴刻度
    :param dataMatrix: 数据矩阵
    :param rangeCnt: y轴刻度数量(不包括0)
    :param setYTick: 是否设置y轴刻度
    :param setYLim: 是否设置y轴范围
    :return:
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
    print(bestTick)

    # 计算y轴刻度
    yTicks = [i * bestTick for i in range(rangeCnt + 1)]
    if yTicks[-1] < maxData:
        yLim = bestTick * (rangeCnt + 1)
        yTicks.append(yLim)
    else:
        yLim = bestTick * rangeCnt
    yLim *= 1.1  # 留出一点空间
    print(yTicks, yLim)

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


def drawBar(dataMatrix, kindList, groupList, xticks=True, legend=True, colors=None, patterns=None):
    """
    竖着的小型柱状图
    :param dataMatrix: 二维数组，label数量 * 柱子组数
    :param kindList: 种类名列表 放在图例处
    :param groupList: 柱子组名列表 放在x轴处
    :param xticks: 是否需要x轴刻度
    :param legend: 是否需要图例
    :param colors: 柱子颜色列表
    :param patterns: 柱子填充图案列表
    :return: fig
    """
    if len(dataMatrix) != len(kindList):
        raise ValueError("dataMatrix and kindList should have the same length")
    if len(dataMatrix[0]) != len(groupList):
        raise ValueError("dataMatrix[0] and groupList should have the same length")

    # Reference: https://designbro.com/blog/inspiration/color-combinations/
    if colors is None:
        # colors = ["#364F6B", "#3FC1C9", "#AFFFFF", "#FC5185"]
        colors = colors1
    if patterns is None:
        # patterns = ['///', '\\\\\\', '', 'XXX']
        patterns = patterns1
    barWidth = 1 / (len(kindList) + 1)

    xLabels = groupList
    xRange = list(range(1, len(xLabels) + 1))
    tot = len(kindList) * barWidth  # 一组柱子的总宽度

    for idx, _ in enumerate(kindList):
        points = []
        for pivot in xRange:
            barGroupStart = pivot - tot / 2 + barWidth / 2
            point = barGroupStart + idx * barWidth
            points.append(point)

        height = dataMatrix[idx]
        plt.bar(points, height, width=barWidth, hatch=patterns[idx], edgecolor='black', color=colors[idx])

    if xticks:
        plt.xticks(xRange, labels=xLabels)
    if legend:
        plt.legend(kindList, loc='center', bbox_to_anchor=(0.5, 1.05), ncol=4, fontsize=6, columnspacing=0.8,
                   handletextpad=0.1)


def drawTraceFixed():
    labelList = ['DedupFS IO', 'SmartDedup IO', 'DedupFS GC', 'SmartDedup GC']
    dataMatrix = np.zeros((len(labelList), len(traceList)), dtype=float)
    print(dataMatrix.shape)
    plt.rcParams["axes.grid.axis"] = "y"

    for i, fs in enumerate(fsList):
        for j, trace in enumerate(traceFileBaseNameList):
            fileName = f"{DATA_PATH}{fs}_{trace}_fixed{fixedLRU}.txt"
            amp = matchAmplification(fileName, 16 * GB >> 12)
            dataMatrix[i][j] = amp
            amp = matchGcAmplification(fileName)
            dataMatrix[i + 2][j] = amp

    # 画出草图
    fig = plt.figure(dpi=300, figsize=(cm_to_inch(SINGLE_COL_WIDTH), cm_to_inch(4)))  # 纵向小一点 跟别的图对齐
    drawBar(dataMatrix, labelList, traceNameList, xticks=True, legend=True)

    # 进行具体的文字设置
    setYTicks(dataMatrix)
    plt.ylabel("Amplification", fontsize=FONTSIZE)

    plt.tight_layout()
    if PLT_SHOW:
        plt.show()
    else:
        plt.savefig(f"{IMG_PATH}TraceFixed.pdf", bbox_inches='tight', pad_inches=0.1)


def drawTraceLife():
    labelList = ['F2FS', 'smartdedup', 'DedupFS', 'ideal']
    lruRatios = [3, 5, 10, 20, 50, 75]
    dataMatrix = np.ones((len(traceList), len(labelList), len(lruRatios)), dtype=float)
    plt.rcParams["axes.grid.axis"] = "y"

    for i, trace in enumerate(traceFileBaseNameList):
        for j, fs in enumerate(labelList[1:-1]):
            for k, lruRatio in enumerate(lruRatios):
                fileName = f"{DATA_PATH}{fs}_{trace}_{lruRatio}.txt"
                amp = matchAmplification(fileName, 16 * GB >> 12)
                amp *= matchGcAmplification(fileName)
                t = 1 / ((1 - dups[i]) * amp)
                dataMatrix[i][j + 1][k] = t  # F2FS默认为1 不需要计算

    for i, trace in enumerate(traceFileBaseNameList):
        dataMatrix[i][3] = 1 / (1 - dups[i])  # F2FS默认为1 不需要计算
    # 画出草图
    fig = plt.figure(dpi=300, figsize=(cm_to_inch(SINGLE_COL_WIDTH * 3), cm_to_inch(4.5)))
    for i, trace in enumerate(traceFileBaseNameList):
        plt.subplot(1, len(traceFileBaseNameList), i + 1)
        drawBar(dataMatrix[i], labelList, list(map(str, lruRatios)), xticks=True, legend=False)
        plt.xlabel(f"({chr(ord('a') + i)}) {traceNameList[i]} dup: {dups[i] * 100:.2f}%", fontsize=FONTSIZE, labelpad=8)

    fig.legend(labelList, loc='upper center', ncol=4, fontsize=8, bbox_to_anchor=(0.5, 1.05), columnspacing=0.8,
               handletextpad=0.1)
    # 进行具体的文字设置
    # plt.yticks(np.arange(0, 2.1, 0.5))
    # plt.ylim((0, 3))
    # plt.ylabel("Life Span", fontsize=FONTSIZE)

    plt.tight_layout()
    if PLT_SHOW:
        plt.show()
    else:
        plt.savefig(f"{IMG_PATH}TraceLife.pdf", bbox_inches='tight', pad_inches=0.1)


def drawFIOFixed():
    dupRatios = [0, 25, 50, 75]
    lruRatio = 5
    fsList = ["DedupFS", "smartdedup"]
    labelList = ['DedupFS IO', 'SmartDedup IO', 'DedupFS GC', 'SmartDedup GC']
    dataMatrix = np.zeros((len(labelList), len(dupRatios)), dtype=float)

    # 解析数据
    for i, fs in enumerate(fsList):
        for j, dupRatio in enumerate(dupRatios):
            fileName = f"{DATA_PATH}{fs}_{dupRatio}_fixed{lruRatio}.txt"
            amp = matchAmplification(fileName, 16 * GB >> 12)
            dataMatrix[i][j] = amp
            amp = matchGcAmplification(fileName)
            dataMatrix[i + 2][j] = amp

    # 画出草图
    plt.figure(dpi=300, figsize=(cm_to_inch(SINGLE_COL_WIDTH), cm_to_inch(4.5)))
    drawBar(dataMatrix, labelList, list(map(str, dupRatios)))

    # 进行具体的文字设置
    setYTicks(dataMatrix)

    plt.xlabel("Dup ratio (%)", fontsize=FONTSIZE)
    plt.ylabel("Amplification", fontsize=FONTSIZE)
    plt.tight_layout()

    if PLT_SHOW:
        plt.show()
    else:
        plt.savefig(f"{IMG_PATH}FIOFixed.pdf", bbox_inches='tight', pad_inches=0.1)


def drawFIOAll():
    # https://github.com/Light-Dedup/tests/blob/4e2c27df7948d9cf8024b0226905fde89797d238/FIG7_FIO/plot.ipynb#L28
    dupRatios = [0, 25, 50, 75]
    lruRatios = [3, 5, 10, 20, 50, 75]
    labelList = ['DedupFS IO', 'SmartDedup IO', 'DedupFS GC', 'SmartDedup GC']
    dataMatrix = np.zeros((len(dupRatios), len(labelList), len(lruRatios)), dtype=float)

    # 解析数据
    for i, dupRatio in enumerate(dupRatios):
        for j, fs in enumerate(fsList):
            for k, lruRatio in enumerate(lruRatios):
                fileName = f"{DATA_PATH}{fs}_{dupRatio}_{lruRatio}.txt"
                amp = matchAmplification(fileName, 16 * GB >> 12)
                dataMatrix[i][j][k] = amp
                amp = matchGcAmplification(fileName)
                dataMatrix[i][j + 2][k] = amp

    kindList = labelList
    xLabels = lruRatios
    colors = ['#8DD3C7', '#FFFFB3', '#BEBADA', '#FB8072']
    barWidth = 1 / (len(kindList) + 1)
    patterns = ['///', '\\\\\\', '', 'XXX']
    xRange = list(range(1, len(xLabels) + 1))

    fig = plt.figure(dpi=300, figsize=(cm_to_inch(SINGLE_COL_WIDTH * 3), cm_to_inch(4.5)))
    for i, dupRatio in enumerate(dupRatios):
        plt.subplot(1, 4, i + 1)

        tot = len(kindList) * barWidth  # 一组柱子的总宽度
        for idx, _ in enumerate(kindList):
            points = []
            for pivot in xRange:
                barGroupStart = pivot - tot / 2 + barWidth / 2
                point = barGroupStart + idx * barWidth
                points.append(point)

            height = dataMatrix[i][idx]
            plt.bar(points, height, width=barWidth, hatch=patterns[idx], edgecolor='black', color=colors[idx])

        plt.xticks(xRange, labels=xLabels)
        plt.xlabel(f"({chr(ord('a') + i)}) duplication ratio: {dupRatio}%", fontsize=FONTSIZE, labelpad=8)

        yticks = list(np.arange(0, np.max(dataMatrix[i]) + 0.4, 0.5))
        yticks = yticks[::max(len(yticks) // 3, 1)]  # 限制y轴刻度数量
        plt.yticks(yticks, fontsize=FONTSIZE)
        if i == 0:
            plt.ylabel("Amplification", fontsize=FONTSIZE)

    fig.legend(kindList, loc='upper center', ncol=4, fontsize=8, bbox_to_anchor=(0.5, 1.05), columnspacing=0.8,
               handletextpad=0.1)
    textY = 0.18
    fig.text(0.16, textY, "LRU ratio (%)", ha='center', va='center', fontsize=FONTSIZE - 1)
    fig.text(0.40, textY, "LRU ratio (%)", ha='center', va='center', fontsize=FONTSIZE - 1)
    fig.text(0.644, textY, "LRU ratio (%)", ha='center', va='center', fontsize=FONTSIZE - 1)
    fig.text(0.886, textY, "LRU ratio (%)", ha='center', va='center', fontsize=FONTSIZE - 1)
    plt.tight_layout()

    if PLT_SHOW:
        plt.show()
    else:
        plt.savefig(f"{IMG_PATH}FIOAll.pdf", bbox_inches='tight', pad_inches=0.1)


def drawFIOAllDouble():
    # https://github.com/Light-Dedup/tests/blob/4e2c27df7948d9cf8024b0226905fde89797d238/FIG7_FIO/plot.ipynb#L28
    dupRatios = [0, 25, 50, 75]
    # dupRatios = traceFileBaseNameList
    lruRatios = [3, 5, 10, 20, 50, 75]
    labelList = ['DedupFS IO', 'SmartDedup IO', 'DedupFS GC', 'SmartDedup GC']
    dataMatrix = np.zeros((len(dupRatios), len(labelList), len(lruRatios)), dtype=float)

    # 解析数据
    for i, dupRatio in enumerate(dupRatios):
        for j, fs in enumerate(fsList):
            for k, lruRatio in enumerate(lruRatios):
                fileName = f"{DATA_PATH}{fs}_{dupRatio}_{lruRatio}.txt"
                amp = matchAmplification(fileName, 16 * GB >> 12)
                dataMatrix[i][j][k] = amp
                amp = matchGcAmplification(fileName)
                dataMatrix[i][j + 2][k] = amp
    print(dataMatrix)
    fig = plt.figure(dpi=300, figsize=(cm_to_inch(SINGLE_COL_WIDTH * 3), cm_to_inch(6)))
    for i, dupRatio in enumerate(dupRatios):

        def drawFIOAllDoubleSubplot(dataM, kindL, plotIdx, ylabel, colors=None, patterns=None):
            plt.subplot(2, len(dupRatios), plotIdx)
            drawBar(dataM, kindL, list(map(str, lruRatios)), xticks=True, legend=False, colors=colors,
                    patterns=patterns)
            yticks = list(np.arange(0, np.max(dataM) * 1.5, 0.5))
            yticks = yticks[::max(len(yticks) // 3, 1)]  # 限制y轴刻度数量
            plt.yticks(yticks, fontsize=FONTSIZE)
            if i == 0:
                plt.ylabel(ylabel, fontsize=FONTSIZE)

        drawFIOAllDoubleSubplot(dataMatrix[i][:2], labelList[:2], i + 1, "IO Amp.", colors1[:2], patterns1[:2])
        drawFIOAllDoubleSubplot(dataMatrix[i][2:], labelList[2:], i + 1 + len(dupRatios), "GC Amp.", colors1[2:],
                                patterns1[2:])
        plt.xlabel(f"LRU Ratio(%)\n\n({chr(ord('a') + i)}) duplication ratio: {dupRatio}%", fontsize=FONTSIZE,
                   labelpad=8)

    fig.legend(labelList, loc='upper center', ncol=4, fontsize=8, bbox_to_anchor=(0.5, 1.05), columnspacing=0.8,
               handletextpad=0.1)
    # textY = 0.18
    # fig.text(0.16, textY, "LRU ratio (%)", ha='center', va='center', fontsize=FONTSIZE - 1)
    # fig.text(0.40, textY, "LRU ratio (%)", ha='center', va='center', fontsize=FONTSIZE - 1)
    # fig.text(0.644, textY, "LRU ratio (%)", ha='center', va='center', fontsize=FONTSIZE - 1)
    # fig.text(0.886, textY, "LRU ratio (%)", ha='center', va='center', fontsize=FONTSIZE - 1)
    plt.tight_layout()

    if PLT_SHOW:
        plt.show()
    else:
        plt.savefig(f"{IMG_PATH}FIOAll.pdf", bbox_inches='tight', pad_inches=0.1)


def drawTraceAllDouble():
    # https://github.com/Light-Dedup/tests/blob/4e2c27df7948d9cf8024b0226905fde89797d238/FIG7_FIO/plot.ipynb#L28
    # traceFileBaseNameList = [0, 25, 50, 75]
    lruRatios = [3, 5, 10, 20, 50, 75]
    labelList = ['DedupFS IO', 'SmartDedup IO', 'DedupFS GC', 'SmartDedup GC']
    dataMatrix = np.zeros((len(traceFileBaseNameList), len(labelList), len(lruRatios)), dtype=float)
    # 解析数据
    for i, trace in enumerate(traceFileBaseNameList):
        for j, fs in enumerate(fsList):
            for k, lruRatio in enumerate(lruRatios):
                # print(trace, fs, lruRatio)
                fileName = f"{DATA_PATH}{fs}_{trace}_{lruRatio}.txt"
                amp = matchAmplification(fileName, 16 * GB >> 12)
                dataMatrix[i][j][k] = amp
                amp = matchGcAmplification(fileName)
                dataMatrix[i][j + 2][k] = amp

    fig = plt.figure(dpi=300, figsize=(cm_to_inch(SINGLE_COL_WIDTH * 3), cm_to_inch(6)))
    for i, trace in enumerate(traceFileBaseNameList):

        def drawFIOAllDoubleSubplot(dataM, kindL, plotIdx, ylabel, colors=None, patterns=None):
            plt.subplot(2, 5, plotIdx)
            drawBar(dataM, kindL, list(map(str, lruRatios)), xticks=True, legend=False, colors=colors,
                    patterns=patterns)
            yticks = list(np.arange(0, np.max(dataM) * 1.5, 0.5))
            yticks = yticks[::max(len(yticks) // 3, 1)]  # 限制y轴刻度数量
            plt.yticks(yticks, fontsize=FONTSIZE)
            if i == 0:
                plt.ylabel(ylabel, fontsize=FONTSIZE)

        drawFIOAllDoubleSubplot(dataMatrix[i][:2], labelList[:2], i + 1, "IO Amp.", colors1[:2], patterns1[:2])
        drawFIOAllDoubleSubplot(dataMatrix[i][2:], labelList[2:], i + 6, "GC Amp.", colors1[2:], patterns1[2:])
        plt.xlabel(f"LRU Ratio(%)\n\n({chr(ord('a') + i)}) {trace}", fontsize=FONTSIZE, labelpad=8)

    fig.legend(labelList, loc='upper center', ncol=4, fontsize=8, bbox_to_anchor=(0.5, 1.05), columnspacing=0.8,
               handletextpad=0.1)
    # textY = 0.18
    # fig.text(0.16, textY, "LRU ratio (%)", ha='center', va='center', fontsize=FONTSIZE - 1)
    # fig.text(0.40, textY, "LRU ratio (%)", ha='center', va='center', fontsize=FONTSIZE - 1)
    # fig.text(0.644, textY, "LRU ratio (%)", ha='center', va='center', fontsize=FONTSIZE - 1)
    # fig.text(0.886, textY, "LRU ratio (%)", ha='center', va='center', fontsize=FONTSIZE - 1)
    plt.tight_layout()

    if PLT_SHOW:
        plt.show()
    else:
        plt.savefig(f"{IMG_PATH}TraceAll.pdf", bbox_inches='tight', pad_inches=0.1)


def drawCdf():
    fig = plt.figure(dpi=300, figsize=(6, 3))
    subfig = plt.subplot(1, 2, 1)
    global FONTSIZE  # 应该不用global吧
    FONTSIZE = 12
    for name in traceNameList:
        with open(f"{DATA_PATH}hashCount/{name}.txt", 'r') as f:
            values = eval(f.read())
        pdf = np.zeros(max(values) + 1)  # 横轴为频数(1 到 最大频数), 0号位置就放一个0
        for value in values:
            pdf[value] += 1  # 该频数占总频数的比例, 确保pdf总和为sum(values), 即总的哈希值个数

        # 计算cdf
        cdf = np.cumsum(pdf) / sum(pdf)
        # 画图
        plt.plot(np.arange(len(cdf)), cdf, label=name)

    # subfig.text(18, -0.1, "repeated hash count", ha='center', va='center', fontsize=FONTSIZE-1)
    plt.xlabel("repeated hash count", fontsize=FONTSIZE, labelpad=8)
    plt.ylabel('Probability', fontsize=FONTSIZE)
    plt.ylim((0, 1.1))
    xMax = 200
    plt.xlim((-xMax // 20, xMax))
    plt.legend(fontsize=FONTSIZE)

    subfig = plt.subplot(1, 2, 2)
    for name in traceNameList:
        with open(f"{DATA_PATH}refDistance/{name}.txt", 'r') as f:
            values = eval(f.read())
        pdf = np.zeros(max(values) + 1)  # 横轴为频数(1 到 最大频数), 0号位置就放一个0
        for value in values:
            pdf[value] += 1  # 该频数占总频数的比例, 确保pdf总和为sum(values), 即总的哈希值个数

        # 计算cdf
        cdf = np.cumsum(pdf) / sum(pdf)
        # 画图
        plt.plot(np.arange(len(cdf)), cdf, label=name)

    # subfig.text(40, -0.1, "distance", ha='center', va='center', fontsize=FONTSIZE-1)
    plt.xlabel("distance", fontsize=FONTSIZE, labelpad=8)
    plt.ylabel('Probability', fontsize=FONTSIZE)
    plt.ylim((0, 1.1))
    xMax = 1000
    plt.xlim((-xMax // 20, xMax))

    plt.legend(fontsize=FONTSIZE)
    plt.tight_layout()
    if PLT_SHOW:
        plt.show()
    else:
        plt.savefig(f"{IMG_PATH}TraceAnalysis.pdf", bbox_inches='tight', pad_inches=0.1)


def drawBarh(wCnt, idealRef, dedupRef, idealMeta, dedupMeta, ssdCnt, gcCnt):
    fig = plt.figure(dpi=300, figsize=(cm_to_inch(SINGLE_COL_WIDTH), cm_to_inch(4)))
    bar_width = 0.5
    inner_width = 0.1
    # Reference: https://coolors.co/palettes/popular/6%20colors
    # colors = ["#093baa", "#0f67e8", "#0078e0", "#0087ff", "#99cfff", "#ffffff"]
    colors = ["#74DBEF", "#2EB872", "#F9A828", "#5E88FC", "#F38181"]
    patterns = ['/', '\\', 'XXX', "OOO", "///", "\\\\\\", "xxx"]
    # patterns = ['' for _ in range(5)]
    scales = [4, 1]
    fss = ['SSD', 'smartdedup', 'ideal\n(DedupFS)']  # 柱子的类别
    labelList = ["data", "FP metadata", "ref metadata", "SSD write", "SSD GC"]

    dataMatrix = [
        [0, 0, 0, ssdCnt, gcCnt],
        [wCnt, dedupMeta, dedupRef, 0, 0],
        [wCnt, idealMeta, idealRef, 0, 0]
    ]

    xRange = list(range(1, len(fss) + 1))
    for fsIdx, fs in enumerate(fss):
        left = 0
        pivot = xRange[fsIdx]
        for labelIdx in range(len(labelList)):
            width = dataMatrix[fsIdx][labelIdx]
            plt.barh(y=pivot, width=width, color=colors[labelIdx], edgecolor='black', left=left,
                     height=bar_width, hatch=patterns[labelIdx], linewidth=0.5)
            left = left + width

    plt.xlabel('Page count (4KB)', fontsize=FONTSIZE)
    plt.yticks(xRange, labels=fss, fontsize=8)
    fig.legend(labelList, loc=(0, 0.9), ncol=6, frameon=False, columnspacing=1,
               handletextpad=0.2, labelspacing=1, fontsize=7)
    plt.xlim((0, 6e6))
    plt.tight_layout()
    # plt.show()
    plt.savefig(f"{IMG_PATH}2Amp.pdf", bbox_inches='tight', pad_inches=0)


def match_and_draw_barh(fmtPath, dupRatio):
    dedupFS = fmtPath.format("DedupFS")
    smartdedup = fmtPath.format("smartdedup")
    print(smartdedup)
    with open(dedupFS, "r") as f:
        dedup_content = f.read()
    with open(smartdedup, "r") as f:
        smart_content = f.read()

    wCnt = int(matchFirstInt(r"total_write_count (\d+)", dedup_content) * (1 - dupRatio))
    idealRef = matchFirstInt(r"global_ref_write_count (\d+)", dedup_content)
    idealMeta = matchFirstInt(r"change_to_disk_count (\d+)", dedup_content)
    dedupRef = matchFirstInt(r"total_num_enter_write_ref_file (\d+)", smart_content)
    dedupMeta = matchFirstInt(r"change_to_disk_count (\d+)", smart_content)
    dedupAll = matchFirstInt(r"total_num_enter_write_metadata_func (\d+)", smart_content)
    assert dedupAll == dedupRef + dedupMeta

    ssdCnt = int(re.findall(r"normal_wPage_count: (\d+)", smart_content)[-1])
    gcCnt = int(re.findall(r"gc_wPage_count: (\d+)", smart_content)[-1])

    print(wCnt, idealRef, dedupRef, idealMeta, dedupMeta, ssdCnt, gcCnt)
    drawBarh(wCnt, idealRef, dedupRef, idealMeta, dedupMeta, ssdCnt, gcCnt)


def drawSpeed():
    rounds = 3  # 跑的轮数
    dupRatios = [0, 25, 50, 75]
    fsList = ["DedupFS", "smartdedup", "f2fs"]
    dataMatrix = np.zeros((len(dupRatios), len(fsList)), dtype=float)
    for dupIdx, dupRatio in enumerate(dupRatios):
        for fsIdx, fs in enumerate(fsList):
            for r in range(rounds):
                fileName = f"{DATA_PATH}{fs}_{dupRatio}_t{r}.json"
                speed = matchSpeed(fileName)
                print(f"{dupRatio} {fs} {r} {speed}")
                dataMatrix[dupIdx][fsIdx] += speed

    dataMatrix /= rounds

    plt.figure(dpi=300, figsize=(cm_to_inch(SINGLE_COL_WIDTH), cm_to_inch(4.5)))
    drawBar(dataMatrix.T, fsList, list(map(str, dupRatios)))
    plt.xlabel("Dup ratio (%)", fontsize=FONTSIZE)
    plt.ylabel("Speed (MB/s)", fontsize=FONTSIZE)
    plt.tight_layout()
    if PLT_SHOW:
        plt.show()
    else:
        plt.savefig(f"{IMG_PATH}Speed.pdf", bbox_inches='tight', pad_inches=0.1)

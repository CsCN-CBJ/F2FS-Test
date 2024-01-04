import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import style
from brokenaxes import brokenaxes

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
    :return: fig
    """
    if len(dataMatrix) != len(kindList):
        raise ValueError("dataMatrix and kindList should have the same length")
    if len(dataMatrix[0]) != len(groupList):
        raise ValueError("dataMatrix[0] and groupList should have the same length")

    fig = plt.figure(dpi=300, figsize=(cm_to_inch(SINGLE_COL_WIDTH), cm_to_inch(4.5)))
    # Reference: https://designbro.com/blog/inspiration/color-combinations/
    colors = ["#364F6B", "#3FC1C9", "#AFFFFF", "#FC5185"]
    barWidth = 1 / (len(kindList) + 1)
    patterns = ['///', '\\\\\\', '', 'XXX']

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

    plt.xticks(xRange, labels=xLabels)
    plt.legend(kindList, loc='center', bbox_to_anchor=(0.5, 1.05), ncol=4, fontsize=6, columnspacing=0.8,
               handletextpad=0.1)
    return fig


def drawTrace():
    labelList = ['DedupFS IO', 'SmartDedup IO', 'DedupFS GC', 'SmartDedup GC']
    dataMatrix = np.zeros((len(labelList), len(traceList)), dtype=float)
    print(dataMatrix.shape)
    plt.rcParams["axes.grid.axis"] = "y"

    for i, fs in enumerate(fsList):
        for j, trace in enumerate(traceFileBaseNameList):
            fileName = f"{DATA_PATH}{fs}_{trace}.txt"
            amp = matchAmplification(fileName, 8 * GB >> 12)
            dataMatrix[i][j] = amp
            amp = matchGcAmplification(f"{DATA_PATH}{fs}_{trace}.txt")
            dataMatrix[i + 2][j] = amp

    # 画出草图
    fig = plt.figure(dpi=300, figsize=(cm_to_inch(SINGLE_COL_WIDTH), cm_to_inch(4.5)))
    # Reference: https://designbro.com/blog/inspiration/color-combinations/
    colors = ["#364F6B", "#3FC1C9", "#AFFFFF", "#FC5185"]
    barWidth = 1 / (len(labelList) + 1)
    patterns = ['///', '\\\\\\', '', 'XXX']

    xLabels = traceNameList
    xRange = list(range(1, len(xLabels) + 1))
    tot = len(labelList) * barWidth  # 一组柱子的总宽度

    for idx, _ in enumerate(labelList):
        points = []
        for pivot in xRange:
            barGroupStart = pivot - tot / 2 + barWidth / 2
            point = barGroupStart + idx * barWidth
            points.append(point)

        height = dataMatrix[idx]
        height = list(map(lambda x: x if x < 2.5 else 2.5, height))
        bars = plt.bar(points, height, width=barWidth, hatch=patterns[idx], edgecolor='black', color=colors[idx])
        if idx == 1:
            for barIdx in [0, 2]:
                bar = bars[barIdx]
                height = dataMatrix[idx][barIdx]
                plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.05, '%.1fX' % height, ha='center',
                         va='bottom', fontsize=6)

    plt.xticks(xRange, labels=xLabels)
    plt.legend(labelList, loc='center', bbox_to_anchor=(0.5, 1.25), ncol=4, fontsize=6, columnspacing=0.8,
               handletextpad=0.1)

    # 进行具体的文字设置
    plt.yticks(np.arange(0, 2.1, 0.5))
    plt.ylim((0, 3))

    plt.xlabel("16GB FIO Amplification of 15% LRU cache", fontsize=FONTSIZE, labelpad=8)
    plt.ylabel("Amplification", fontsize=FONTSIZE)
    fig.text(0.5, 0.18, "Dup ratio (%)", ha='center', va='center', fontsize=FONTSIZE - 1)  # , transform=fig.transAxes)
    plt.tight_layout()
    if PLT_SHOW:
        plt.show()
    else:
        plt.savefig("./data/0Trace.pdf", bbox_inches='tight', pad_inches=0.1)
        print("saved")


def drawFIOFixed():
    dupRatios = [0, 25, 50, 75]
    labelList = ['DedupFS IO', 'SmartDedup IO', 'DedupFS GC', 'SmartDedup GC']
    dataMatrix = np.zeros((len(labelList), len(dupRatios)), dtype=float)

    # 解析数据
    for i, fs in enumerate(fsList):
        for j, dupRatio in enumerate(dupRatios):
            fileName = f"{DATA_PATH}{fs}_{dupRatio}_fixed.txt"
            amp = matchAmplification(fileName, 16 * GB >> 12)
            dataMatrix[i][j] = amp
            amp = matchGcAmplification(fileName)
            dataMatrix[i + 2][j] = amp

    # 画出草图
    fig = drawBar(dataMatrix, labelList, list(map(str, dupRatios)))

    # 进行具体的文字设置
    plt.yticks(np.arange(0, np.max(dataMatrix) + 0.1))
    # plt.ylim((0, 4.1))

    plt.xlabel("16GB FIO Amplification of fixed 15% LRU cache", fontsize=FONTSIZE, labelpad=8)
    plt.ylabel("Amplification", fontsize=FONTSIZE)
    fig.text(0.5, 0.18, "Dup ratio (%)", ha='center', va='center', fontsize=FONTSIZE - 1)  # , transform=fig.transAxes)
    plt.tight_layout()

    if PLT_SHOW:
        plt.show()
    else:
        plt.savefig("./data/0FIOFixed.pdf", bbox_inches='tight', pad_inches=0)


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
        plt.savefig("./data/0FIOAll.pdf", bbox_inches='tight', pad_inches=0.1)


def drawCdf():
    fig = plt.figure(dpi=300, figsize=(6, 3))
    subfig = plt.subplot(1, 2, 1)
    for name in traceNameList:
        with open(f"./data/hashCount/{name}.txt", 'r') as f:
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
        with open(f"./data/refDistance/{name}.txt", 'r') as f:
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
        plt.savefig(f"./data/0TraceAnalysis.pdf", bbox_inches='tight', pad_inches=0.1)


def drawBarh(wCnt, idealRef, dedupRef, idealMeta, dedupMeta, ssdCnt, gcCnt):
    fig = plt.figure(dpi=300, figsize=(cm_to_inch(SINGLE_COL_WIDTH), cm_to_inch(4)))
    bar_width = 0.5
    inner_width = 0.1
    num_job = 1
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
    plt.savefig("./data/2Amp.pdf".format(num_job), bbox_inches='tight', pad_inches=0)


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


# match_and_draw_barh("./data/13 改过smartdedup之后的16GFIO/{}_25_10.txt", 0.25)

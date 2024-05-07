from drawUtils import *


def drawSimple():
    legendList = ["H2C-Dedup", "SmartDedup", "HFDedup", "Dmdedup"]  # 图例中的名字
    xTickList = ["Homes", "HomesF", "MailF", "WebF", "Smart"]  # x轴的名字

    dataMatrix = np.zeros((len(legendList), len(xTickList)), dtype=float)
    for i, kind in enumerate(legendList):
        for j, trace in enumerate(xTickList):
            fileName = f"{kind}_{trace}.txt"
            num = len(fileName) + j  # 读取数据
            dataMatrix[i][j] = num

    plt.figure(dpi=300, figsize=(cm_to_inch(SINGLE_COL_WIDTH), cm_to_inch(4.5)))  # 宽度和高度
    drawBar(dataMatrix, legendList, xTickList, xLabel="Workloads", yLabel="Length", legend=False)
    defaultLegend(plt, len(legendList), 1.3)
    plt.tight_layout(pad=0.4)
    showPlt("simple")


# 一个柱子多个颜色
def drawStacks():
    legendList = ["Delta", "Meta"]  # 图例中的名字
    xTickList = ["Homes", "HomesF", "MailF", "WebF", "Smart"]  # x轴的名字

    dataMatrix = np.zeros((len(legendList), len(xTickList)), dtype=float)
    for i, kind in enumerate(legendList):
        for j, tick in enumerate(xTickList):
            fileName = f"{kind}_{tick}.txt"
            num = i + j + 1  # 读取数据
            dataMatrix[i][j] = num

    plt.figure(dpi=300, figsize=(cm_to_inch(SINGLE_COL_WIDTH), cm_to_inch(3)))  # 宽度和高度
    xRange = list(range(1, len(xTickList) + 1))
    for j, tick in enumerate(xTickList):
        base = 0
        pivot = xRange[j]
        for i, kind in enumerate(legendList):
            height = dataMatrix[i][j]
            plt.bar(pivot, height=height, width=0.5, bottom=base,
                    color=colors1[i], hatch=patterns1[i], edgecolor='black', linewidth=0, alpha=.99)
            # 横着就是把bar改成barh, width与height互换, bottom改成left
            # plt.barh(pivot, width=width, height=0.5, left=left,
            #          color=colors1[labelIdx], edgecolor='black', hatch=patterns1[labelIdx], linewidth=0, alpha=.99)
            base += height
    setYTicks(dataMatrix.sum(axis=0))

    plt.xticks(xRange, labels=xTickList)
    plt.xlabel("Trace")
    plt.ylabel("Time (ms)")
    plt.legend(legendList, loc='upper center', bbox_to_anchor=(0.5, 1.35), ncol=len(legendList))
    showPlt("stack")


def drawMultiLine():
    dupRatios = [0, 25, 50, 75]
    lruRatios = [3, 5, 10, 20, 50, 75]
    fsList = ["DedupFS", "smartdedup", "HFDedup2", "Dmdedup"]
    labelList = ['H2C-Dedup', 'SmartDedup', 'HF-Dedupe', 'Dmdedup']
    xLabels = [f"Cache ratio (%)\n({chr(ord('a') + i)}) Duplication ratio: {dupRatios[i]}%"
               for i in range(len(dupRatios))]
    dataMatrixIO = np.zeros((len(dupRatios), len(labelList), len(lruRatios)), dtype=float)
    dataMatrixGC = np.zeros((len(dupRatios), len(labelList), len(lruRatios)), dtype=float)

    # 解析数据
    for i, dupRatio in enumerate(dupRatios):
        for j, fs in enumerate(fsList):
            for k, lruRatio in enumerate(lruRatios):
                fileName = f"{DATA_PATH}{fs}_{dupRatio:02d}_{lruRatio:02d}.txt"
                dataMatrixIO[i][j][k], dataMatrixGC[i][j][k] = len(fileName) + i + j + k, i + j + k

    fig = plt.figure(dpi=300, figsize=(cm_to_inch(DOUBLE_COL_WIDTH), cm_to_inch(5.6)))
    draw = drawMultiChart(2, len(dupRatios))
    # 需要保证只有一个小图纳入图例中, 否则会出现重复
    # drawBarLine只会在一行里面选出来一个图例, 所以这里需要设置noLegend=True, 保证只有一个子图纳入图例
    draw.drawBarLine(dataMatrixIO, labelList, lruRatios, yLabel="IO Amp.", noLegend=True)
    draw.drawBarLine(dataMatrixGC, labelList, lruRatios, yLabel="GC Amp.", xLabel=xLabels)
    defaultLegend(fig, len(labelList))

    plt.tight_layout(pad=0.4)
    showPlt("MultiLine")

drawMultiLine()

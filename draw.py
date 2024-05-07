from drawUtils import *
from utils import *
from config import *


def drawTraceLifeLine():
    # 与fsList反过来
    labelList = ['F2FS', 'Dmdedup', "HF-Dedupe", 'SmartDedup', 'H2C-Dedup', 'Ideal']
    dataMatrix = np.ones((len(traceList), len(labelList), len(lruRatios)), dtype=float)
    totalSize = [77.3860, 43.9153, 115.6106, 23.2718, 20.1186]

    for i, trace in enumerate(traceFileBaseNameList):
        # F2FS默认为1 不需要计算

        # 理想情况
        dataMatrix[i][-1] = totalSize[i] / (uniqueSize / GB)

        # 两种dedup的计算
        for j, fs in enumerate(fsList[::-1]):
            for k, lruRatio in enumerate(lruRatios):
                fileName = f"{DATA_PATH}{fs}_{trace}_{lruRatio}.txt"
                ampIO, ampGC = match2Amps(fileName, calcUniqueWPages(uniqueSize, 0))
                amp = ampIO * ampGC
                t = dataMatrix[i][-1][0] / amp if amp != 0 else 0
                dataMatrix[i][j + 1][k] = t

    # 画图
    fig = plt.figure(dpi=300, figsize=(cm_to_inch(DOUBLE_COL_WIDTH), cm_to_inch(3)))
    nCol = len(traceFileBaseNameList)
    xLabels = [f"Cache ratio (%)\n({chr(ord('a') + i)}) {traceNameList[i]}" for i in range(len(traceNameList))]
    colors = colors1[:len(labelList) - 1][::-1] + [colors1[len(labelList) - 1]]
    for i in range(nCol):
        plt.subplot(1, nCol, i + 1)
        for j in range(len(labelList)):
            plt.plot(list(map(str, lruRatios)), dataMatrix[i][j], label=labelList[j] if i == 0 else "_noLegend_",
                     color=colors[j],
                     linestyle=line_styles[j], linewidth=1, marker=markers[j], markersize=4, markeredgewidth=0.5)
            setYTicks(dataMatrix[i])
            plt.xticks(list(map(str, lruRatios)), list(map(str, lruRatios)))

        setAxisWidth()
        plt.xlabel(xLabels[i])
        if i == 0:
            plt.ylabel("Norm lifespan")

    defaultLegend(fig, len(labelList), 1.2)
    plt.tight_layout(pad=0.4)
    showPlt("TraceLife")


def drawFIOAllDouble():
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
                dataMatrixIO[i][j][k], dataMatrixGC[i][j][k] = match2Amps(fileName, calcUniqueWPages(uniqueSize, 0))

    fig = plt.figure(dpi=300, figsize=(cm_to_inch(DOUBLE_COL_WIDTH), cm_to_inch(5.6)))
    draw = drawMultiChart(2, len(dupRatios))
    draw.drawBarLine(dataMatrixIO, labelList, lruRatios, yLabel="IO Amp.", noLegend=True)
    draw.drawBarLine(dataMatrixGC, labelList, lruRatios, yLabel="GC Amp.", xLabel=xLabels)
    defaultLegend(fig, len(labelList))

    plt.tight_layout(pad=0.4)
    showPlt("FIOAll")


def drawTraceAllDouble():
    labelList = ['H2C-Dedup', 'SmartDedup', "HF-Dedupe", "Dmdedup"]
    xLabels = [f"Cache ratio (%)\n({chr(ord('a') + i)}) {traceNameList[i]}" for i in range(len(traceNameList))]
    dataMatrixIO = np.zeros((len(traceFileBaseNameList), len(labelList), len(lruRatios)), dtype=float)
    dataMatrixGC = np.zeros((len(traceFileBaseNameList), len(labelList), len(lruRatios)), dtype=float)

    # 解析数据
    for i, trace in enumerate(traceFileBaseNameList):
        for j, fs in enumerate(fsList):
            for k, lruRatio in enumerate(lruRatios):
                fileName = f"{DATA_PATH}{fs}_{trace}_{lruRatio}.txt"
                dataMatrixIO[i][j][k], dataMatrixGC[i][j][k] = match2Amps(fileName, calcUniqueWPages(uniqueSize, 0))

    # 画图
    fig = plt.figure(dpi=300, figsize=(cm_to_inch(DOUBLE_COL_WIDTH), cm_to_inch(5.6)))
    draw = drawMultiChart(2, len(traceFileBaseNameList))
    draw.drawBarLine(dataMatrixIO, labelList, lruRatios, yLabel="IO Amp.", noLegend=True)
    draw.drawBarLine(dataMatrixGC, labelList, lruRatios, yLabel="GC Amp.", xLabel=xLabels)
    defaultLegend(fig, len(labelList))

    plt.tight_layout(pad=0.4)
    showPlt("TraceAll")


def drawCdf():
    fig = plt.figure(dpi=300, figsize=(6, 3))
    subfig = plt.subplot(1, 2, 1)
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


def drawBarh(wCnt, idealRef, dedupRef, idealMeta, dedupMeta, gcCnt, origin):
    fig = plt.figure(dpi=300, figsize=(cm_to_inch(SINGLE_COL_WIDTH), cm_to_inch(3)))
    bar_width = 0.5
    # Reference: https://coolors.co/palettes/popular/6%20colors
    # colors = ["#74DBEF", "#2EB872", "#F9A828", "#5E88FC", "#F38181"]
    colors = colors1
    patterns = ['///', '\\\\\\', 'XXX', "OOO", "///"]
    fss = ['SmartDedup', 'IdealDedup', 'NonDedup']  # 柱子的类别
    labelList = ["Data", "FP Metadata", "Ref Metadata", "SSD GC"]

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
            plt.barh(pivot, width=width, color=colors[labelIdx], edgecolor='black', left=left,
                     height=bar_width, hatch=patterns[labelIdx], linewidth=0, alpha=.99)
            plt.ylim((0.3, 3.7))
            left = left + width

    plt.xlabel('Write to disk (GB)', fontsize=FONTSIZE)
    plt.yticks(xRange, labels=fss, fontsize=FONTSIZE - 1)
    fig.legend(labelList, loc='upper center', bbox_to_anchor=(0.55, 1.2), ncol=len(labelList), frameon=False,
               columnspacing=1, handletextpad=0.2, labelspacing=1)
    # plt.xlim((0, 6e6))
    ax = plt.gca()
    lw = 0.5
    for axis in ['top', 'bottom', 'left', 'right']:
        ax.spines[axis].set_linewidth(lw)
    plt.tight_layout(pad=0.4)
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

    drawBarh(wCnt, idealRef, dedupRef, idealMeta, dedupMeta, gcCnt, origin)


def drawSpeed_boxplot():
    rounds = 5  # 跑的轮数
    fsList = ["DedupFS", "smartdedup", "HFDedup2", "Dmdedup", "f2fs"]
    labelList = ["H2C-Dedup", "SmartDedup", "HF-Dedupe", "Dmdedup", "F2FS"]
    dataMatrix = np.zeros((len(fsList), len(dupRatios), rounds), dtype=float)
    for r in range(rounds):
        for dupIdx, dupRatio in enumerate(dupRatios):
            for fsIdx, fs in enumerate(fsList):
                fileName = f"{DATA_PATH}{fs}_{dupRatio}_t{r}.json"
                speed = matchSpeed(fileName)
                dataMatrix[fsIdx][dupIdx][r] = speed

    fig = plt.figure(dpi=300, figsize=(cm_to_inch(SINGLE_COL_WIDTH * 1.5), cm_to_inch(4)))
    plt.subplot(1, 2, 1)
    pointsMatrix, barWidth, xRange = getPointsMatrix(len(dupRatios), len(fsList))
    for idx in range(len(fsList)):
        error = np.std(dataMatrix[idx], axis=1)
        plt.bar(pointsMatrix[idx], np.mean(dataMatrix[idx], axis=1), width=barWidth, color=colors1[idx],
                edgecolor='black',
                hatch=patterns1[idx], linewidth=0.5, yerr=error,
                error_kw={'elinewidth': 0.5, 'ecolor': 'black', 'capsize': 1.5, 'capthick': 0.5})
    setAxisWidth()
    plt.xticks(xRange, labels=dupRatios)
    plt.xlabel("Duplication ratio (%)\n(a)Write Throughput")
    plt.ylabel("Throughput (MB/s)")

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
    setAxisWidth()
    fig.legend(handles=boxes, labels=labelList, loc='upper center', ncol=len(labelList),
               fontsize=FONTSIZE,
               bbox_to_anchor=(0.5, 1.1),
               columnspacing=0.8,
               handletextpad=0.1)
    plt.xticks(xRange, labels=dupRatios)
    # plt.ylim((0, 30000))
    # plt.yticks(np.arange(200, 450 + 1, 50), fontsize=FONTSIZE)
    plt.xlabel("Duplication ratio (%)\n(b)99% Write Latency")
    plt.ylabel("Latency (us)")
    plt.tight_layout(pad=0.4)
    showPlt("Speed")


def drawSpeed2():
    rounds = 5  # 跑的轮数
    fsList = ["DedupFS", "smartdedup", "HFDedup2", "Dmdedup", "f2fs"]
    labelList = ["H2C-Dedup", "SmartDedup", "HF-Dedupe", "Dmdedup", "F2FS"]
    dataMatrix = np.zeros((len(fsList), len(dupRatios), rounds), dtype=float)
    for r in range(rounds):
        for dupIdx, dupRatio in enumerate(dupRatios):
            for fsIdx, fs in enumerate(fsList):
                fileName = f"{DATA_PATH}{fs}_{dupRatio}_t{r}.json"
                speed = matchSpeed(fileName)
                dataMatrix[fsIdx][dupIdx][r] = speed

    fig = plt.figure(dpi=300, figsize=(cm_to_inch(SINGLE_COL_WIDTH), cm_to_inch(3)))
    plt.subplot(1, 2, 1)
    pointsMatrix, barWidth, xRange = getPointsMatrix(len(dupRatios), len(fsList))
    for idx in range(len(fsList)):
        error = np.std(dataMatrix[idx], axis=1)
        plt.bar(pointsMatrix[idx], np.mean(dataMatrix[idx], axis=1), width=barWidth - 0.05, color=colors1[idx],
                label=labelList[idx], alpha=.99,
                hatch=patterns1[idx], linewidth=0.5, yerr=error,
                error_kw={'elinewidth': 0.5, 'ecolor': 'black', 'capsize': 1.5, 'capthick': 0.5})

    setAxisWidth()
    plt.xticks(xRange, labels=dupRatios)
    plt.yticks([0, 100, 200, 300, 400])
    plt.xlabel("Duplication ratio (%)\n(a)Write throughput")
    plt.ylabel("Tput (MB/s)")

    plt.subplot(1, 2, 2)
    dataMatrix = np.zeros((len(fsList), len(dupRatios), rounds), dtype=float)
    for r in range(rounds):
        for dupIdx, dupRatio in enumerate(dupRatios):
            for fsIdx, fs in enumerate(fsList):
                fileName = f"{DATA_PATH}{fs}_{dupRatio}_t{r}.json"
                speed = matchLatency99(fileName)
                dataMatrix[fsIdx][dupIdx][r] = speed

    dataMatrix /= 1000
    # dataMatrix[np.where(dataMatrix > 48)] = 48

    pointsMatrix, barWidth, xRange = getPointsMatrix(len(dupRatios), len(fsList))
    for idx in range(len(fsList)):
        error = np.std(dataMatrix[idx], axis=1)
        data = np.mean(dataMatrix[idx], axis=1)
        if fsList[idx] == 'Dmdedup':
            data[np.where(data > 48)] = 48
            error *= 0
        rects = plt.bar(pointsMatrix[idx], data, width=barWidth - 0.05, color=colors1[idx],
                        hatch=patterns1[idx], linewidth=0.5, yerr=error, alpha=.99,
                        error_kw={'elinewidth': 0.5, 'ecolor': 'black', 'capsize': 1.5, 'capthick': 0.5})
        if fsList[idx] == 'Dmdedup':
            heights = np.mean(dataMatrix[idx], axis=1)
            for i, rect in enumerate(rects):
                # height = np.mean(dataMatrix[idx], axis=1)
                height = heights[i]
                plt.text(rect.get_x() + rect.get_width() / 2, 44, f"{height:.1f}", size=6, ha='center', va='bottom')

    setAxisWidth()
    plt.xticks(xRange, labels=dupRatios)
    plt.yticks([0, 10, 20, 30, 40])
    plt.ylim((0, 44))
    plt.xlabel("Duplication ratio (%)\n(b)Write latency")
    plt.ylabel("Latency (us)")

    defaultLegend(fig, len(labelList), 1.2)
    plt.tight_layout(pad=0.4)
    showPlt("Speed")


def drawSpeedMulti():
    rounds = 1  # 跑的轮数
    # configList = [("DedupFS", 0), ("DedupFS", 25), ("f2fs", 0), ("f2fs", 25)]
    configList = [("DedupFS", 0), ("f2fs", 0)]
    labelList = ["H2C-Dedup", "F2FS"]
    # labelList = ["H2C-Dedup 0%", "H2C-Dedup 25%", "F2FS 0%", "F2FS 25%"]
    threads = list(map(str, [1, 2, 3, 4]))

    dataMatrix = np.zeros((len(labelList), len(threads)), dtype=float)
    for thrIdx, thread in enumerate(threads):
        for idx, (fs, dupRatio) in enumerate(configList):
            for r in range(rounds):
                fileName = f"{DATA_PATH}{fs}_{dupRatio}_{thread}_t{r}.json"
                dataMatrix[idx][thrIdx] += matchSpeed(fileName)
    dataMatrix /= rounds
    dataMatrix /= dataMatrix[1][0]

    # plt.figure(dpi=300, figsize=(cm_to_inch(SINGLE_COL_WIDTH / 2), cm_to_inch(4)))
    drawBar(dataMatrix, labelList, threads, xLabel="Threads", yLabel="Norm Tput",
            colors=[colors1[0], colors1[4]],
            patterns=[patterns1[0], patterns1[4]],
            noLegend=True, legend=False
            )

    # plt.legend(loc='upper center', ncol=2, fontsize=6, bbox_to_anchor=(0.5, 1.3), columnspacing=0.8,
    #            handletextpad=0.1)
    # plt.tight_layout(pad=0.4)
    # showPlt("SpeedMulti")


def drawCpu():
    rounds = 1  # 跑的轮数
    fsList = ["DedupFS", "smartdedup", "HFDedup2", 'f2fs']
    labelList = ["H2C-Dedup", "SmartDedup", "HF-Dedupe", "F2FS"]
    dataMatrix = np.zeros((len(fsList), len(dupRatios)), dtype=float)
    for dupIdx, dupRatio in enumerate(dupRatios):
        for fsIdx, fs in enumerate(fsList):
            for r in range(rounds):
                fileName = f"{DATA_PATH}{fs}_{dupRatio}_t{r}.txt"
                cpu = calcCpuUsageFile(fileName)
                dataMatrix[fsIdx][dupIdx] += cpu
    dataMatrix /= rounds

    # plt.figure(dpi=300, figsize=(cm_to_inch(SINGLE_COL_WIDTH/1.5), cm_to_inch(4)))
    drawBar(dataMatrix, labelList, dupRatios, xLabel="Duplication ratio (%)\n(a) CPU usage", yLabel="CPU usage (%)",
            legend=False, colors=[*colors1[0:3], colors1[4]],
            patterns=[*patterns1[0:3], patterns1[4]])
    # plt.legend(loc='upper center', ncol=len(labelList), fontsize=6, bbox_to_anchor=(0.5, 1.3), columnspacing=0.8,
    #            handletextpad=0.1)
    # plt.tight_layout(pad=0.4)
    # showPlt("CPU")


def drawCpuAndMultiSpeed():
    fig = plt.figure(dpi=300, figsize=(cm_to_inch(SINGLE_COL_WIDTH), cm_to_inch(3)))
    plt.subplot(1, 2, 1)
    drawCpu()
    plt.subplot(1, 2, 2)
    drawSpeedMulti()
    defaultLegend(fig, 4, 1.2)
    fig.tight_layout(pad=0.4)
    showPlt("CpuSpeed")


if __name__ == '__main__':
    PLT_SHOW = False
    DATA_PATH = "./data/66最终总数据/"
    # drawTraceAllDouble()
    # drawFIOAllDouble()
    # drawTraceLifeLine()
    # drawSpeed2()
    # drawCpu() 合并
    # drawSpeedMulti() 合并
    # drawCpuAndMultiSpeed()
    # drawCdf()
    # drawRecover()
    # idx = 4
    # match_and_draw_barh(f"{DATA_PATH}{{}}_{traceFileBaseNameList[idx]}_3.txt", dups[idx])
    # total = 4194304
    # drawBarh(total - 1346294, total / 4096 * 12, 233024, total / 4096 * 24, 909475, 1239216, total)

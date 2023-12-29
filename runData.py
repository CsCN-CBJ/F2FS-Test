import os
import matplotlib.pyplot as plt

from utils import *


def runTraceData():
    lruRatio = 10
    path = 'blkparse/'

    dups = [0.6909, 0.3350, 0.8800, 0.2002]

    for trace, dupRatio in zip(traceList, dups):
        for fs in fsList:
            lruLen = getLRUSize(traceSize, dupRatio * 100, lruRatio)
            os.system(f"runData.bat {lruLen} {path}{trace} {fs}")

            dstName = f"./data/{fs}_{trace.split('.')[0]}.txt"
            if os.path.exists(dstName):
                os.remove(dstName)
            os.rename(f"./data/result.txt", dstName)


def runTraceFixedData():
    """
    用于测试固定的LRU_LIST_LENGTH, 目前固定为总写入量的10%
    """
    lruRatio = 10
    path = 'blkparse/'

    dups = [0.6909, 0.3350, 0.8800, 0.2002]

    for trace, dupRatio in zip(traceList, dups):
        for fs in fsList:
            lruLen = getLRUSize(traceSize, 0, lruRatio)
            print(lruLen)
            exit(0)
            os.system(f"runData.bat {lruLen} {path}{trace} {fs}")

            dstName = f"./data/{fs}_{trace.split('.')[0]}.txt"
            if os.path.exists(dstName):
                os.remove(dstName)
            os.rename(f"./data/result.txt", dstName)


def runFioData():
    dupRatios = [0, 25, 50, 75]
    lruRatios = [3, 5, 10, 20, 50, 100]

    for dupRatio in dupRatios:
        for lruRatio in lruRatios:
            for fs in fsList:
                lruLen = getLRUSize(TOTAL_WRTIE, dupRatio, lruRatio)
                os.system(f"runData.bat {lruLen} {dupRatio} {fs}")

                dstName = f"./data/{fs}_{dupRatio}_{lruRatio}.txt"
                if os.path.exists(dstName):
                    os.remove(dstName)
                os.rename(f"./data/result.txt", f"./data/{fs}_{dupRatio}_{lruRatio}.txt")


def drawFioDup():
    lruRatio = 50
    dupRatios = [0, 25, 50, 75]
    xRange = range(len(dupRatios))

    for index, fs in enumerate(fsList):
        dataList = []
        for dupRatio in dupRatios:
            amp = matchAmplification(f"./data/{fs}_{dupRatio}_{lruRatio}.txt")
            dataList.append(amp)
            plt.bar([i + bar_width * index for i in xRange],
                    dataList, bar_width, color=colors[index], alpha=opacity, label=fs)

    # 设置横纵坐标的标签和标题
    plt.xlabel('dupRatios')
    plt.ylabel('Amplification')
    plt.title('Comparison of DedupFS and SmartDedup')
    plt.xticks([i + bar_width / 2 for i in xRange], dupRatios)

    # 显示图例
    plt.legend()
    # 显示图形
    plt.show()


def drawFioAll():
    dupRatios = [0, 25, 50, 75]
    lruRatios = [3, 5, 10, 20, 50, 100]
    xRange = range(len(lruRatios))

    plt.figure(figsize=(10, 10), dpi=100)
    for dupRatio in dupRatios:
        plt.subplot(2, 2, dupRatio // 25 + 1)
        for index, fs in enumerate(fsList):
            dataList = []
            for lruRatio in lruRatios:
                amp = matchAmplification(f"./data/{fs}_{dupRatio}_{lruRatio}.txt")
                dataList.append(amp)
            plt.bar([i + bar_width * index for i in xRange],
                    dataList, bar_width, color=colors[index], alpha=opacity, label=fs)

        # 设置横纵坐标的标签和标题
        plt.xlabel('lruRatios')
        plt.ylabel('Amplification')
        plt.title(f"dupRatio: {dupRatio}%")
        plt.xticks([i + bar_width / 2 for i in xRange], lruRatios)

    plt.suptitle('Fio Amplification All')
    # 显示图例
    plt.legend()
    # 显示图形
    plt.savefig("./data/0FioAll.png")
    plt.show()


def drawFioGcAll():
    dupRatios = [0, 25, 50, 75]
    lruRatios = [3, 5, 10, 20, 50, 100]
    xRange = range(len(lruRatios))

    plt.figure(figsize=(10, 10), dpi=100)
    for dupRatio in dupRatios:
        plt.subplot(2, 2, dupRatio // 25 + 1)
        for index, fs in enumerate(fsList):
            dataList = []
            for lruRatio in lruRatios:
                amp = matchGcAmplification(f"./data/{fs}_{dupRatio}_{lruRatio}.txt")
                dataList.append(amp)
            plt.bar([i + bar_width * index for i in xRange],
                    dataList, bar_width, color=colors[index], alpha=opacity, label=fs)

        # 设置横纵坐标的标签和标题
        plt.xlabel('lruRatios')
        plt.ylabel('GC Amplification')
        plt.title(f"dupRatio: {dupRatio}%")
        plt.xticks([i + bar_width / 2 for i in xRange], lruRatios)

    plt.suptitle('Fio GC All')
    # 显示图例
    plt.legend()
    # 显示图形
    plt.savefig("./data/0FioGcAll.png")
    plt.show()


def drawTrace():
    traceNameList = list(map(lambda x: x.split('.')[0], traceList))
    lruRatio = 10
    xRange = range(len(traceNameList))

    for index, fs in enumerate(fsList):
        dataList = []
        for trace in traceNameList:
            amp = matchAmplification(f"./data/{fs}_{trace}.txt", 8 * 1024 * 1024 * 1024 >> 12)
            dataList.append(amp)
        plt.bar([i + bar_width * index for i in xRange],
                dataList, bar_width, color=colors[index], alpha=opacity, label=fs)

    # 设置横纵坐标的标签和标题
    plt.xlabel('dupRatios')
    plt.ylabel('Amplification')
    plt.title('Trace Comparison')
    plt.xticks([i + bar_width / 2 for i in xRange], traceNameList)

    # 显示图例
    plt.legend()
    plt.savefig("./data/0Trace.png")
    # 显示图形
    plt.show()


def drawTraceGc():
    traceNameList = list(map(lambda x: x.split('.')[0], traceList))
    lruRatio = 10
    xRange = range(len(traceNameList))

    for index, fs in enumerate(fsList):
        dataList = []
        for trace in traceNameList:
            amp = matchGcAmplification(f"./data/{fs}_{trace}.txt")
            dataList.append(amp)
        plt.bar([i + bar_width * index for i in xRange],
                dataList, bar_width, color=colors[index], alpha=opacity, label=fs)

    # 设置横纵坐标的标签和标题
    plt.xlabel('dupRatios')
    plt.ylabel('GC Amplification')
    plt.title('Trace GC Comparison')
    plt.xticks([i + bar_width / 2 for i in xRange], traceNameList)

    # 显示图例
    plt.legend()
    plt.savefig("./data/0TraceGC.png")
    # 显示图形
    plt.show()

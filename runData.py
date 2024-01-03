import os
import matplotlib.pyplot as plt

from utils import *


def runTraceData():
    lruRatio = 10
    path = 'blkparse/'

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
    lruRatios = [3, 5, 10, 20, 50, 75]

    for dupRatio in dupRatios:
        for lruRatio in lruRatios:
            for fs in fsList:
                lruLen = getLRUSize(TOTAL_WRITE, dupRatio, lruRatio)
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
    plt.savefig("./data/0FioAll.pdf")
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


def draw_barh(wCnt, idealRef, dedupRef, idealMeta, dedupMeta, ssdCnt, gcCnt, LRURatio):
    # 数据
    categories = ['SSD', 'smartdedup', 'ideal\n(DedupFS)']  # 柱子的类别
    values1 = [0, wCnt, wCnt]  # 第一级数据
    values2 = [0, dedupRef, idealRef]  # 第二级数据
    values3 = [0, dedupMeta, idealMeta]  # 第三级数据

    # 设置图形大小
    fig, ax = plt.subplots(figsize=(8, 6))

    # 绘制柱状图
    barWidth = 0.2  # 每根柱子的宽度
    index = range(len(categories))  # x轴刻度位置

    plt.barh(index, values1, height=barWidth, label='Data')
    plt.barh(index, values2, height=barWidth, left=values1, label='Ref metadata')
    plt.barh(index, values3, height=barWidth, left=[i + j for i, j in zip(values1, values2)],
             label='FP metadata')
    plt.barh(index, [ssdCnt, 0, 0], height=barWidth, left=[0, 0, 0], label='SSD write')
    plt.barh(index, [gcCnt, 0, 0], height=barWidth, left=[ssdCnt, 0, 0], label='SSD GC')

    # 设置图例和标签
    plt.legend(loc=1)
    plt.xlabel('Page count')
    # plt.ylabel('Category')
    # plt.xlim(0, 2e6)
    plt.title(f"Different page count of SSD, smartdedup and ideal\n(DedupFS) under 25% dup ratio\nLRU cache {LRURatio}%")

    # 设置刻度标签
    plt.yticks(index, categories)

    # 显示图形
    plt.show()


def match_and_draw_barh(fmtPath, dupRatio, LRURatio):
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
    draw_barh(wCnt, idealRef, dedupRef, idealMeta, dedupMeta, ssdCnt, gcCnt, LRURatio)

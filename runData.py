import os
import re
import matplotlib.pyplot as plt

TOTAL_WRTIE = 5 * 1024 * 1024 * 1024  # 5GB
fsList = ["DedupFS", "smartdedup"]
ENTRIES_PER_BLOCK = 100
traceList = ['hitsz_8GB.hitsztrace', 'homes_8GB.blkparse', 'mail_8GB.blkparse', 'web_8GB.blkparse']
traceSize = 8 * 1024 * 1024 * 1024

colors = ['b', 'r', 'g', 'y', 'c', 'm']


def matchFirstInt(reStr: str, string: str):
    """
    返回匹配字符串的第一个组
    """
    pattern = re.compile(reStr)
    match = pattern.search(string)
    if match is None:
        # print(f"reStr: {reStr}, string: {string}")
        raise KeyError("match failed")
    return int(match.group(1))


def matchAmplification(filename: str, valid_wCnt=TOTAL_WRTIE >> 12):
    """
    :return: amplification
    """
    with open(filename, "r") as f:
        content = f.read()
        wCnt = matchFirstInt(r"total_write_count (\d+)", content)
        if wCnt != valid_wCnt:
            print(f"total_write_count: {wCnt}, filename: {filename}")
        wDedupCnt = matchFirstInt(r"total_dedup_count (\d+)", content)
        wMetaCnt = matchFirstInt(r"change_to_disk_count (\d+)", content)

        try:
            # 识别smartdedup的amplification
            wRefCnt = matchFirstInt(r"total_num_enter_write_ref_file (\d+)", content)
            wMetaAll = matchFirstInt(r"total_num_enter_write_metadata_func (\d+)", content)
            assert wMetaAll == wMetaCnt + wRefCnt
            wMetaAll = matchFirstInt(r"change_to_disk_count (\d+)", content)
        except KeyError:
            # 识别DysDedup的amplification
            wRefCnt = matchFirstInt(r"global_ref_write_count (\d+)", content)
            wMetaAll = wMetaCnt + wRefCnt

        amplification = wMetaAll / (wCnt - wDedupCnt) + 1
        return amplification


def getLRUSize(size, dupRatio, lruRatio):
    """
    获取LRU_LIST_LENGTH
    :param size: 总写入量 单位：B
    :param dupRatio: 重复率 [0, 100]
    :param lruRatio: LRU_LIST_LENGTH占非重复写入量的比例 [0, 100]
    :return: LRU_LIST_LENGTH: int
    """
    if 0 < dupRatio < 1 or 0 < lruRatio < 1:
        print(f"WARNING: dupRatio or lruRatio is too small (dupRatio: {dupRatio}, lruRatio: {lruRatio})")
    return int((size >> 12) * (100 - dupRatio) / 100 * lruRatio / 100)


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
    bar_width = 0.35
    opacity = 0.8
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
    bar_width = 0.35
    opacity = 0.8
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

    # 显示图例
    plt.legend()
    # 显示图形
    plt.savefig("./data/FioAll.png")
    plt.show()


def drawTrace():
    traceNameList = list(map(lambda x: x.split('.')[0], traceList))
    lruRatio = 10
    bar_width = 0.35
    opacity = 0.8
    xRange = range(len(traceNameList))

    for index, fs in enumerate(fsList):
        dataList = []
        for trace in traceNameList:
            amp = matchAmplification(f"./data/{fs}_{trace}.txt", 8 * 1024 * 1024 * 1024 >> 12)
            dataList.append(amp)
        print(dataList)
        plt.bar([i + bar_width * index for i in xRange],
                dataList, bar_width, color=colors[index], alpha=opacity, label=fs)

    # 设置横纵坐标的标签和标题
    plt.xlabel('dupRatios')
    plt.ylabel('Amplification')
    plt.title('Comparison of DedupFS and SmartDedup')
    plt.xticks([i + bar_width / 2 for i in xRange], traceNameList)

    # 显示图例
    plt.legend()
    plt.savefig("./data/Trace.png")
    # 显示图形
    plt.show()


if __name__ == "__main__":
    # draw()
    runTraceData()
    drawTrace()
    # runFioData()
    # drawFioAll()
    # drawFioDup()

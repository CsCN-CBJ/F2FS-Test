import os
import re
import matplotlib.pyplot as plt

TOTAL_WRTIE = 5 * 1024 * 1024 * 1024  # 5GB
fsList = ["DedupFS", "smartdedup"]
ENTRIES_PER_BLOCK = 100


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


def matchAmplification(filename: str):
    """
    :return: amplification
    """
    with open(filename, "r") as f:
        content = f.read()
        wCnt = matchFirstInt(r"total_write_count (\d+)", content)
        if wCnt != TOTAL_WRTIE >> 12:
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


def runTraceData():
    path = 'blkparse/'
    traceList = ['hitsz_4GB.blkparse', 'mail_4GB.blkparse', 'homes_4GB.hitsztrace']
    for trace in traceList:
        for fs in fsList:
            os.system(f"runData.bat 10000 {path}{trace} {fs}")

            dstName = f"./data/{fs}_{trace.split('.')[0]}.txt"
            if os.path.exists(dstName):
                os.remove(dstName)
            os.rename(f"./data/result.txt", dstName)
    return


def runFioData():
    dupRatios = [0, 25, 50, 75]
    lruRatios = [3, 5, 10, 20, 50, 100]

    for dupRatio in dupRatios:
        for lruRatio in lruRatios:
            for fs in fsList:
                lruLen = (TOTAL_WRTIE >> 12) * (100 - dupRatio) / 100 * lruRatio / 100
                lruLen = int(lruLen)
                os.system(f"runData.bat {lruLen} {dupRatio} {fs}")

                dstName = f"./data/{fs}_{dupRatio}_{lruRatio}.txt"
                if os.path.exists(dstName):
                    os.remove(dstName)
                os.rename(f"./data/result.txt", f"./data/{fs}_{dupRatio}_{lruRatio}.txt")


def drawFioDup():
    lruRatio = 50
    dupRatios = [0, 25, 50, 75]
    dataMatrix = []

    for fs in fsList:
        dataList = []
        for dupRatio in dupRatios:
            amp = matchAmplification(f"./data/{fs}_{dupRatio}_{lruRatio}.txt")
            dataList.append(amp)
        dataMatrix.append(dataList)

    # 绘制柱状图
    bar_width = 0.35
    opacity = 0.8
    index = range(len(dupRatios))

    plt.bar(index, dataMatrix[0], bar_width, alpha=opacity, color='b', label=fsList[0])
    plt.bar([i + bar_width for i in index], dataMatrix[1], bar_width, alpha=opacity, color='r', label=fsList[1])

    # 设置横纵坐标的标签和标题
    plt.xlabel('dupRatios')
    plt.ylabel('Amplification')
    plt.title('Comparison of DedupFS and SmartDedup')
    plt.xticks([i + bar_width / 2 for i in index], dupRatios)

    # 显示图例
    plt.legend()
    # 显示图形
    plt.show()


def drawFioAll():
    dupRatios = [0, 25, 50, 75]
    lruRatios = [3, 5, 10, 20, 50, 100]
    bar_width = 0.35
    opacity = 0.8
    colors = ['b', 'r', 'g', 'y', 'c', 'm']
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
        # plt.title('Comparison of DedupFS and SmartDedup')
        plt.title(f"dupRatio: {dupRatio}%")
        plt.xticks([i + bar_width / 2 for i in xRange], lruRatios)

    # 显示图例
    plt.legend()
    # 显示图形
    plt.savefig("./data/FioAll.png")
    plt.show()


def drawTrace():
    traceNameList = ['hitsz_4GB', 'mail_4GB', 'homes_4GB']

    fs = "DedupFS"
    dysData = []
    for dupRatio in traceNameList:
        amp = matchAmplification(f"./data/{fs}_{dupRatio}.txt")
        dysData.append(amp)

    fs = "smartdedup"
    smartData = []
    for dupRatio in traceNameList:
        amp = matchAmplification(f"./data/{fs}_{dupRatio}.txt")
        smartData.append(amp)

    # 绘制柱状图
    bar_width = 0.35
    opacity = 0.8
    index = range(len(traceNameList))
    plt.bar(index, dysData, bar_width, alpha=opacity, color='b', label="DedupFS")
    plt.bar([i + bar_width for i in index], smartData, bar_width, alpha=opacity, color='r', label="smartdedup")

    # 设置横纵坐标的标签和标题
    plt.xlabel('dupRatios')
    plt.ylabel('Amplification')
    plt.title('Comparison of DedupFS and SmartDedup')
    plt.xticks([i + bar_width / 2 for i in index], traceNameList)

    # 显示图例
    plt.legend()
    # 显示图形
    plt.show()


if __name__ == "__main__":
    # draw()
    # runTraceData()
    # runFioData()
    drawFioAll()
    # drawFioDup()
    # print(matchAmplification("./data/DedupFS_hitsztrace_4GB.txt"))
    # print(matchAmplification("./data/smartdedup_hitsztrace_4GB.txt"))

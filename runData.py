from utils import *
from config import *


def runTraceDataAll():
    path = 'blkparse/'

    for lruRatio in lruRatios:
        for trace in traceList:
            for fs in fsList:
                lruLen = getLRUSize(uniqueSize, 0, lruRatio)
                ratio = int(traceSize[traceList.index(trace)] * GB / uniqueSize * 100)
                os.system(f"runCbj.bat {lruLen} {path}{trace} {fs} 0 {ratio}")
                renameResult(f"./data/{fs}_{trace.split('.')[0]}_{lruRatio}")


def runTraceFixedData():
    """
    用于测试固定的LRU_LIST_LENGTH
    """
    path = 'blkparse/'

    for trace in traceList:
        for fs in fsList:
            lruLen = getLRUSize(uniqueSize, 0, fixedLRU)
            os.system(f"runData.bat {lruLen} {path}{trace} {fs}")
            renameResult(f"./data/{fs}_{trace.split('.')[0]}_fixed{fixedLRU}")


def runFioDataAll():
    for lruRatio in lruRatios:
        for dupRatio in dupRatios:
            for fs in fsList:
                lruLen = getLRUSize(uniqueSize, 0, lruRatio)
                total = int(uniqueSize / (1 - dupRatio / 100))
                ratio = int(100 / (100 - dupRatio) * 100)
                os.system(f"runCbj.bat {lruLen} {dupRatio} {fs} {total // 1024}K {ratio}")
                renameResult(f"./data/{fs}_{dupRatio:02d}_{lruRatio:02d}")


def runFioFixedData():
    for dupRatio in dupRatios:
        for fs in fsList:
            lruLen = getLRUSize(TOTAL_WRITE, 0, fixedLRU)
            os.system(f"runData.bat {lruLen} {dupRatio} {fs}")
            renameResult(f"./data/{fs}_{dupRatio}_fixed{fixedLRU}")


def runSpeed():
    rounds = 5  # 跑的轮数
    fsList.append("f2fs")

    for roundCnt in range(rounds):
        for fs in fsList:
            for dupRatio in dupRatios:
                lruLen = getLRUSize(10 * GB, dupRatio, 10)
                ratio = int(100 / (100 - dupRatio) * 100)
                os.system(f"runData.bat {lruLen} {dupRatio} {fs} 10G {ratio}")
                renameResult(f"./data/{fs}_{dupRatio}_t{roundCnt}")


def runMultiThread():
    rounds = 1  # 跑的轮数
    fsList = ['f2fs', 'DedupFS']
    for roundCnt in range(rounds):
        for fs in fsList:
            for dupRatio in dupRatios:
                for thread in [1, 2, 3, 4]:
                    totalsize = 10 * GB
                    lruLen = getLRUSize(totalsize, dupRatio, 10)
                    size = totalsize // MB // thread
                    os.system(f"runData.bat {lruLen} {dupRatio} {fs} {size}M 0 {thread}")
                    renameResult(f"./data/{fs}_{dupRatio}_{thread}_t{roundCnt}")
                    return

from utils import *


def runTraceDataAll():
    path = 'blkparse/'

    for trace, dupRatio in zip(traceList, dups):
        for lruRatio in lruRatios:
            for fs in fsList:
                lruLen = getLRUSize(traceSize, dupRatio * 100, lruRatio)
                os.system(f"runData.bat {lruLen} {path}{trace} {fs}")
                renameResult(f"./data/{fs}_{trace.split('.')[0]}_{lruRatio}")


def runTraceFixedData():
    """
    用于测试固定的LRU_LIST_LENGTH
    """
    path = 'blkparse/'

    for trace, dupRatio in zip(traceList, dups):
        for fs in fsList:
            lruLen = getLRUSize(traceSize, 0, fixedLRU)
            os.system(f"runData.bat {lruLen} {path}{trace} {fs}")
            renameResult(f"./data/{fs}_{trace.split('.')[0]}_fixed{fixedLRU}")


def runFioDataAll():
    for dupRatio in dupRatios:
        for lruRatio in lruRatios:
            for fs in fsList:
                lruLen = getLRUSize(TOTAL_WRITE, dupRatio, lruRatio)
                os.system(f"runData.bat {lruLen} {dupRatio} {fs}")
                renameResult(f"./data/{fs}_{dupRatio}_{lruRatio}")


def runFioFixedData():
    for dupRatio in dupRatios:
        for fs in fsList:
            lruLen = getLRUSize(TOTAL_WRITE, 0, fixedLRU)
            os.system(f"runData.bat {lruLen} {dupRatio} {fs}")
            renameResult(f"./data/{fs}_{dupRatio}_fixed{fixedLRU}")


def runSpeed():
    rounds = 10  # 跑的轮数
    fsList = ["DedupFS", "smartdedup", "f2fs"]

    for roundCnt in range(rounds):
        for fs in fsList:
            for dupRatio in dupRatios:
                lruLen = getLRUSize(TOTAL_WRITE, dupRatio, 10)
                os.system(f"runData.bat {lruLen} {dupRatio} {fs}")
                renameAndReplace(f"./data/fio.json", f"./data/{fs}_{dupRatio}_t{roundCnt}.json")

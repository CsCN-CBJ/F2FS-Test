import os
import matplotlib.pyplot as plt

from utils import *


def runTraceData():
    lruRatio = 15
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
    lruRatio = 15
    path = 'blkparse/'

    for trace, dupRatio in zip(traceList, dups):
        for fs in fsList:
            lruLen = getLRUSize(traceSize, 0, lruRatio)
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
                os.rename(f"./data/result.txt", dstName)


def runFioFixedData():
    dupRatios = [0, 25, 50, 75]

    for dupRatio in dupRatios:
        for fs in fsList:
            lruLen = getLRUSize(TOTAL_WRITE, 0, 15)  # 固定为总写入量的15%
            os.system(f"runData.bat {lruLen} {dupRatio} {fs}")

            dstName = f"./data/{fs}_{dupRatio}_fixed.txt"
            if os.path.exists(dstName):
                os.remove(dstName)
            os.rename(f"./data/result.txt", dstName)


def runSpeed():
    rounds = 3  # 跑的轮数
    dupRatios = [0, 25, 50, 75]
    for roundCnt in range(rounds):
        for fs in fsList:
            for dupRatio in dupRatios:
                lruLen = getLRUSize(TOTAL_WRITE, 0, 15)  # 固定为总写入量的15%
                os.system(f"runData.bat {lruLen} {dupRatio} {fs}")
                renameAndReplace(f"./data/fio.json", f"./data/{fs}_{dupRatio}_t{roundCnt}.txt")

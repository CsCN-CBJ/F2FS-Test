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


def matchSmartAmplification(filename: str):
    """
    识别smartdedup的amplification
    :return: amplification
    """
    with open(filename, "r") as f:
        content = f.read()
        wCnt = matchFirstInt(r"total_write_count (\d+)", content)
        wDedupCnt = matchFirstInt(r"total_dedup_count (\d+)", content)
        wMetaAll = matchFirstInt(r"total_num_enter_write_metadata_func (\d+)", content)

        wMetaCnt = matchFirstInt(r"change_to_disk_count (\d+)", content)
        wRefCnt = matchFirstInt(r"total_num_enter_write_ref_file (\d+)", content)
        assert wMetaAll == wMetaCnt + wRefCnt

        amplification = wMetaAll / (wCnt - wDedupCnt) + 1
        return amplification


def matchDysAmplification(filename: str):
    """
    识别DysDedup的amplification
    """
    with open(filename, "r") as f:
        content = f.read()
        wCnt = matchFirstInt(r"total_write_count (\d+)", content)
        wDedupCnt = matchFirstInt(r"total_dedup_count (\d+)", content)

        wMetaCnt = matchFirstInt(r"change_to_disk_count (\d+)", content)
        wRefCnt = matchFirstInt(r"global_ref_write_count (\d+)", content)
        wMetaAll = wMetaCnt + wRefCnt

        amplification = wMetaAll / (wCnt - wDedupCnt) + 1
        print(amplification)
        return amplification


def runData():
    fio = "sudo fio -filename=/home/femu/test/a -iodepth 1 -fallocate=none -thread -rw=write -bs=4K -size=5G " \
          "-numjobs=1 -group_reporting -name=dys-test --dedupe_percentage={} --dedupe_mode=working_set"
    replay = "sudo ./replay -d test/ -o w -m hitsz -v  -f blkparse/4GB.hitsztrace"
    fs = "DedupFS"
    for dupRatio in [0, 25, 50, 75]:
        for lruRatio in [3, 5]:
            lruLen = (TOTAL_WRTIE >> 12) * (100 - dupRatio) / 100 * lruRatio / 100
            lruLen = int(lruLen)
            os.system(f"runData.bat {lruLen} {dupRatio} {fs}")
            os.rename(f"./data/result.txt", f"./data/{fs}_{dupRatio}_{lruRatio}.txt")

    fs = "smartdedup"
    for dupRatio in [0, 25, 50, 75]:
        for lruRatio in [3, 5]:
            lruLen = (TOTAL_WRTIE >> 12) * (100 - dupRatio) / 100 * lruRatio / 100 / ENTRIES_PER_BLOCK
            lruLen = int(lruLen)
            os.system(f"runData.bat {lruLen} {dupRatio} {fs}")
            os.rename(f"./data/result.txt", f"./data/{fs}_{dupRatio}_{lruRatio}.txt")


def draw():
    lruRatio = 3
    dupRatios = [0, 25, 50, 75]

    fs = "DedupFS"
    dysData = []
    for dupRatio in dupRatios:
        amp = matchDysAmplification(f"./data/{fs}_{dupRatio}_{lruRatio}.txt")
        dysData.append(amp)

    fs = "smartdedup"
    smartData = []
    for dupRatio in dupRatios:
        amp = matchSmartAmplification(f"./data/{fs}_{dupRatio}_{lruRatio}.txt")
        smartData.append(amp)

    # 绘制柱状图
    bar_width = 0.35
    opacity = 0.8
    index = range(len(dupRatios))
    plt.bar(index, dysData, bar_width, alpha=opacity, color='b', label="DedupFS")
    plt.bar([i + bar_width for i in index], smartData, bar_width, alpha=opacity, color='r', label="smartdedup")

    # 设置横纵坐标的标签和标题
    plt.xlabel('dupRatios')
    plt.ylabel('Amplification')
    plt.title('Comparison of DedupFS and SmartDedup')
    plt.xticks([i + bar_width / 2 for i in index], dupRatios)

    # 显示图例
    plt.legend()
    # 显示图形
    plt.show()


if __name__ == "__main__":
    draw()
    # runData()

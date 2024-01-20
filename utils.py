import re
import os
import json
from config import TOTAL_WRITE, DATA_PATH
from cbjLibrary.utils.misc import listdir


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


def matchAmplification(filename: str, valid_wCnt=TOTAL_WRITE >> 12):
    """
    :return: amplification
    """
    try:
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
                # assert wMetaAll == wMetaCnt + wRefCnt
                if wMetaAll != wMetaCnt + wRefCnt:
                    print(f"AssertionError wMetaAll: {wMetaAll}, wMetaCnt: {wMetaCnt}, wRefCnt: {wRefCnt}, filename: {filename}")
                # wMetaAll = matchFirstInt(r"change_to_disk_count (\d+)", content)
            except KeyError:
                # 识别DysDedup的amplification
                wRefCnt = matchFirstInt(r"global_ref_write_count (\d+)", content)
                wMetaAll = wMetaCnt + wRefCnt

            amplification = wMetaAll / (wCnt - wDedupCnt) + 1
            return amplification
    except FileNotFoundError:
        return 0


def matchGcAmplification(filename: str):
    """
    :return: GC amplification
    """
    try:
        with open(filename, "r") as f:
            content = f.read()
            if re.search("now gc", content) is None:
                print(f"no gc: {filename}")
                return 0
            find = re.findall(
                r"normal_wCount: (\d+), normal_wPage_count: (\d+), "
                r"gc_count: (\d+), gc_wPage_count: (\d+), valid_gc_write_count: (\d+), invalid_gc_write_count: (\d+)",
                content)
            if find is None:
                print(f"no match: {filename}")
                return 0
            find = find[-1]
            wPageCnt, gcPageCnt, valid_gc_write_count = int(find[1]), int(find[3]), int(find[4])
            if gcPageCnt != valid_gc_write_count:
                print(f"gcPageCnt: {gcPageCnt}, valid_gc_write_count: {valid_gc_write_count}, filename: {filename}")
            return gcPageCnt / wPageCnt + 1
    except FileNotFoundError:
        print(f"no such file: {filename}")
        return 0


def getLRUSize(size, dupRatio, lruRatio):
    """
    获取LRU_LIST_LENGTH
    :param size: 总写入量 单位：B
    :param dupRatio: 重复率 [0, 100]
    :param lruRatio: LRU_LIST_LENGTH占非重复写入量的比例 [0, 100]
    :return: LRU_LIST_LENGTH: int
    """
    if 0 < dupRatio <= 1 or 0 < lruRatio <= 1:
        print(f"WARNING: dupRatio or lruRatio is too small (dupRatio: {dupRatio}, lruRatio: {lruRatio})")
    return int((size >> 12) * (100 - dupRatio) / 100 * lruRatio / 100)


def renameAndReplace(old, new):
    if os.path.exists(new):
        os.remove(new)
    os.rename(old, new)


def renameResult(fileName):
    """
    将测试结果全部重命名
    :param fileName: 命名后的文件名(不包括后缀)
    """
    renameAndReplace(f"./data/result.txt", f"{fileName}.txt")
    renameAndReplace(f"./data/fio.json", f"{fileName}.json")


def matchSpeed(filename: str):
    """
    :return: speed (MB/s)
    """
    try:
        with open(filename, "r") as f:
            content = f.read()
            iops = json.loads(content)["jobs"][0]["write"]["iops_mean"]
            return iops * 4 / 1024
    except FileNotFoundError:
        print(f"no such file: {filename}")
        return 0


def matchLatency99(filename: str):
    """
    :return: 99% latency (ns)
    """
    try:
        with open(filename, "r") as f:
            content = f.read()
            return json.loads(content)["jobs"][0]["write"]["clat_ns"]["percentile"]["99.000000"]
    except FileNotFoundError:
        return 0


def listResults(path):
    """
    列出目录下所有的测试结果
    :param path: data path, 可以是文件或文件夹, 如果为all, 则展示DATAPATH下所有的测试结果
    """
    if path == 'all':
        path = DATA_PATH

    if os.path.isfile(path):
        if path.endswith(".txt"):
            print(f"amp: {matchAmplification(path):.6f}")
            print(f"gc_amp: {matchGcAmplification(path):.6f}")
        elif path.endswith(".json"):
            print(f"speed: {matchSpeed(path):.2f} MB/s")
            print(f"lat99: {matchLatency99(path)} ns")
    elif os.path.isdir(path):
        visited = set()
        for f in listdir(path):
            base = os.path.splitext(f)[0]  # 去掉后缀
            baseName = os.path.basename(f).split(".")[0]
            if base in visited:
                continue
            visited.add(base)
            txt = f"{base}.txt"
            jsn = f"{base}.json"
            if baseName[-2] == 't':
                # 速度测试结果
                print(f"{baseName} \t speed: {matchSpeed(jsn):.2f} MB/s")
            else:
                # 普通测试结果
                print(f"{baseName} \t amp: {matchAmplification(txt):.6f}\t gc_amp: {matchGcAmplification(txt):.6f}\t "
                      f"speed: {matchSpeed(jsn):.2f} MB/s")
    else:
        print(f"no such file or directory: {path}")

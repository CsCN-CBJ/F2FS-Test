import re
import os
import json
from config import TOTAL_WRITE, DATA_PATH, ENCODING
from cbjLibrary.misc import listdir


def handleFileNotFound(returnValue):
    def outer_wrapper(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except FileNotFoundError as e:
                print(f"FileNotFound: {e}; args: {args}; kwargs: {kwargs}")
                return returnValue

        return wrapper

    return outer_wrapper


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
                    print(f"AssertionError wMetaAll: {wMetaAll}, wMetaCnt: {wMetaCnt}, wRefCnt: {wRefCnt}, "
                          f"filename: {filename}")
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


def calcUniqueWPages(totalBytes: int, dupRatio: int) -> int:
    """
    计算非重复写入量(单位: 4KB)
    :param totalBytes: 总写入量(单位: B)
    :param dupRatio: 重复率(单位: %, 即[0, 100])
    :return: 非重复写入量(单位: 4KB)
    """
    return int((totalBytes / 4096) * (100 - dupRatio) // 100)


def match2AmpsStr(content: str, unique_wPages) -> tuple[float, float]:
    """
    返回两个amplification
    :param content: 测试结果字符串
    :param unique_wPages: 非重复写入量(单位: 4KB)
    :return: IO amplification, GC amplification
    """
    if re.search("now gc", content) is None:
        raise ValueError("no gc")

    find = re.findall(
        r"normal_wCount: (\d+), normal_wPage_count: (\d+), "
        r"gc_count: (\d+), gc_wPage_count: (\d+), "
        r"valid_gc_write_count: (\d+), invalid_gc_write_count: (\d+)",
        content)

    if find is None:
        raise ValueError("no match")
    find = find[-1]

    wPageCnt, gcPageCnt = int(find[1]), int(find[3])
    return wPageCnt / unique_wPages, gcPageCnt / wPageCnt + 1


@handleFileNotFound((0, 0))
def match2Amps(filename: str, unique_wPages) -> tuple[float, float]:
    """
    返回两个amplification
    :param filename: 测试结果文件名
    :param unique_wPages: 非重复写入量(单位: 4KB)
    :return: IO amplification, GC amplification. 如果文件不存在, 返回(0, 0)
    """
    try:
        with open(filename, "r", encoding=ENCODING) as f:
            return match2AmpsStr(f.read(), unique_wPages=unique_wPages)
    except ValueError as e:
        print(f"Other Errors: {filename}", e)
        return 0, 0


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
    return int((size / 4096) * (100 - dupRatio) / 100 * lruRatio / 100)


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


@handleFileNotFound(0)
def matchSpeed(filename: str):
    """
    :return: speed (MB/s)
    """
    with open(filename, "r") as f:
        content = f.read()
        if content.startswith("note: "):
            content = content.split("\n", 1)[1]
        iops = json.loads(content)["jobs"][0]["write"]["bw"]
        return iops / 1024


@handleFileNotFound(0)
def matchLatency99(filename: str):
    """
    :return: 99% latency (ns)
    """
    with open(filename, "r") as f:
        content = f.read()
        return json.loads(content)["jobs"][0]["write"]["lat_ns"]["percentile"]["99.000000"]
        # return json.loads(content)["jobs"][0]["write"]["lat_ns"]["mean"] 失败的Dmdedup尝试


def calcCpuUsage(first, second):
    """
    计算CPU使用率
    """
    first = list(map(int, first.strip().split()[1:]))
    second = list(map(int, second.strip().split()[1:]))

    assert len(first) == len(second) == 10
    print(second[3], first[3])
    print(sum(second[:4]), sum(first[:4]))
    return 100 - (second[3] - first[3]) / (sum(second[:4]) - sum(first[:4])) * 100


def calcCpuUsageSmall(first, second):
    """
    计算CPU使用率
    """
    first = list(map(int, first.strip().split()[1:]))
    second = list(map(int, second.strip().split()[1:]))

    assert len(first) == len(second) == 10
    return 100 - (second[3] - first[3]) / (sum(second) - sum(first)) * 100


@handleFileNotFound(0)
def calcCpuUsageFile(filename):
    """
    计算CPU使用率
    """
    with open(filename, "r") as f:
        cpuResult = []
        for line in f:
            if line.startswith("cpu"):
                cpuResult.append(line)
        if len(cpuResult) != 2:
            print(f"cpuResult: {cpuResult}, filename: {filename}")
            return 0
        return calcCpuUsage(cpuResult[0], cpuResult[1])


@handleFileNotFound(0)
def calcCpuUsageFioFile(filename):
    """
    计算CPU使用率
    """
    with open(filename, "r", encoding=ENCODING) as f:
        content = f.read()
        print(filename)
        job = json.loads(content)["jobs"][0]
        print(job["ctx"], job["sys_cpu"])
        return job["ctx"] * job["sys_cpu"] / 100


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

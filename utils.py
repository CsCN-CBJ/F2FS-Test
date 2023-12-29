import re
from config import *


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


def matchGcAmplification(filename: str):
    """
    :return: GC amplification
    """
    with open(filename, "r") as f:
        content = f.read()
        if re.search("now gc", content) is None:
            print(f"no gc: {filename}")
        find = re.findall(
            r"normal_wCount: (\d+), normal_wPage_count: (\d+), "
            r"gc_count: (\d+), gc_wPage_count: (\d+), valid_gc_write_count: (\d+), invalid_gc_write_count: (\d+)",
            content)
        if find is None:
            print(f"no match: {filename}")
        find = find[-1]
        wPageCnt, gcPageCnt, valid_gc_write_count = int(find[1]), int(find[3]), int(find[4])
        if gcPageCnt != valid_gc_write_count:
            print(f"gcPageCnt: {gcPageCnt}, valid_gc_write_count: {valid_gc_write_count}, filename: {filename}")
        return gcPageCnt / wPageCnt + 1


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

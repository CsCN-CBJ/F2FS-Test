#!/bin/bash

set -x
set -e

# @param1: LRU_LIST_LENGTH
# @param2: dedupe_percentage or replayPath
# @param3: f2fs directory
# @param4: FIO size
# @param5: Dmdedup ratio
# @param6: number of threads

if [ $# -lt 3 ] || [ $# -gt 6 ]; then
  echo "Error: Missing argument"
  exit 1
fi

jobs=$6
if [ x$6 == x ]; then
  jobs=1
fi
echo jobs:$jobs

echo $* > result.txt
echo > fio.json

if [ $3 == 'Dmdedup' ]; then
  cd ~
  sudo ./startDmdedup.sh $(($1*36)) $5
else

  if [ $3 != 'f2fs' ]; then
    cd $3 && make clean && make LRU_LIST_LENGTH=$1
    sudo insmod f2fs.ko
  fi

  cd ~
  sudo mkfs.f2fs /dev/nvme0n1
  sudo mount /dev/nvme0n1 /home/femu/test

fi

# 开始计时CPU
head -n1 /proc/stat >> result.txt

# 执行IO测试
if [ ${2##*.} == 'hitsztrace' ]; then
  sudo ./replay -d test/ -o a -f $2 -m hitsz
elif [ ${2##*.} == 'blkparse' ]; then
  sudo ./replay -d test/ -o a -f $2
else
#  dirs=(/home/femu/test/a/a /home/femu/test/b/b /home/femu/test/c/c /home/femu/test/d/d)
#  sudo mkdir -p /home/femu/test/a /home/femu/test/b /home/femu/test/c /home/femu/test/d
#  sudo fio -filename=$(IFS=:; echo "${dirs[*]:0:$jobs}") -iodepth 1 -fallocate=none -thread -rw=write -bs=4K -size=$4 -numjobs=$jobs \
#  -group_reporting -name=dys-test --dedupe_percentage=$2 --output-format=json --output=fio.json --lat_percentiles=1
#  --offset=0 --offset_increment=$4
  sudo fio -filename=/home/femu/test/a -iodepth 1 -fallocate=none -thread -rw=write -bs=4K -size=$4 -numjobs=$jobs \
  -group_reporting -name=dys-test --dedupe_percentage=$2 --output-format=json --output=fio.json --lat_percentiles=1
fi

# 获取测试结果
head -n1 /proc/stat >> result.txt
sleep 60

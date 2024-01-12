#!/bin/bash

set -x
set -e

# @param1: LRU_LIST_LENGTH
# @param2: dedupe_percentage or replayPath
# @param3: f2fs directory

if [ $# -ne 3 ]; then
  echo "Error: Missing argument"
  exit 1
fi

# 如果是DedupFS, 则需要将LRU_LIST_LENGTH除以ENTRIES_PER_BLOCK(100)
LRU_LIST_LENGTH=$1
#if [ $3 == 'DedupFS' ]; then
#  LRU_LIST_LENGTH=$((LRU_LIST_LENGTH/100))
#fi

if [ $3 != 'f2fs' ]; then
  cd $3 && make clean && make LRU_LIST_LENGTH=${LRU_LIST_LENGTH}
  sudo insmod f2fs.ko
fi
cd ~
sudo mkfs.f2fs /dev/nvme0n1
sudo mount /dev/nvme0n1 /home/femu/test

# 执行IO测试
if [ ${2##*.} == 'hitsztrace' ]; then
  sudo ./replay -d test/ -o a -f $2 -m hitsz
elif [ ${2##*.} == 'blkparse' ]; then
  sudo ./replay -d test/ -o a -f $2
else
  sudo fio -filename=/home/femu/test/a -iodepth 1 -fallocate=none -thread -rw=write -bs=4K -size=16G -numjobs=1 \
  -group_reporting -name=dys-test --dedupe_percentage=$2 --output-format=json --output=fio.json
fi

# 获取测试结果
sleep 60
if [ $3 != 'f2fs' ]; then
  sudo ./ioctl
  sudo dmesg | tail -n 50 > result.txt
fi
#sudo mv *.log $imgDir
#cd $imgDir
#fio2gnuplot -b -g
#cd ~
#rm metadata ref_count
#sudo umount /home/femu/test
#sudo rmmod f2fs

#!/bin/bash

set -x
set -e

# @param1: LRU_LIST_LENGTH
# @param2: dedupe_percentage
# @param3: f2fs directory

if [ $# -ne 3 ]; then
  echo "Error: Missing argument"
  exit 1
fi

cd $3 && make clean && make LRU_LIST_LENGTH=$1
sudo insmod f2fs.ko
cd ~
sudo mkfs.f2fs /dev/nvme0n1
sudo mount /dev/nvme0n1 /home/femu/test
sudo fio -filename=/home/femu/test/a -iodepth 1 -fallocate=none -thread -rw=write -bs=4K -size=5G -numjobs=1 -group_reporting -name=dys-test --dedupe_percentage=$2 --dedupe_mode=working_set #--output-format=gnu
sleep 5
sudo ./ioctl
sudo dmesg | tail -n 50 > result.txt

#sudo mv *.log $imgDir
#cd $imgDir
#fio2gnuplot -b -g
#cd ~
#rm metadata ref_count
#sudo umount /home/femu/test
#sudo rmmod f2fs

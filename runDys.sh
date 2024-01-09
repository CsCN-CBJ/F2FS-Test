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

cd ~/femu/build-femu/
echo xiawon666!! | sudo -S ./run-blackbox.sh &
sleep 30 # 等启动

until scp -P 8080 ~/temp/runFemu.sh femu@127.0.0.1:~/
do
  echo "scp failed, retrying..."
  sleep 10
done

ssh -p 8080 femu@127.0.0.1 "bash ./runFemu.sh $*"

sleep 180 # 测试结束后等待一段时间, 确保测试结果写入log

scp -P 8080 femu@127.0.0.1:~/result.txt ~/temp/
scp -P 8080 femu@127.0.0.1:~/fio.json ~/temp/
tail -n4 ~/femu/build-femu/log >> ~/temp/result.txt

# 使用CBJ-SPECIAL来防止kill别人的
sudo kill -SIGINT -- $(pgrep -f "x86_64-softmmu/qemu-system-x86_64 -name FEMU-BBSSD-VM-CBJ-SPECIAL")

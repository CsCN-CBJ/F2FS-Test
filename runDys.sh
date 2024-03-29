#!/bin/bash

set -x
set -e

# @param1: LRU_LIST_LENGTH
# @param2: dedupe_percentage or replayPath
# @param3: f2fs directory

# 检查参数
if [ $# -ne 3 ]; then
  echo "Error: Missing argument"
  exit 1
fi

# 启动femu
cd ~/femu/build-femu/
cat ~/.ssh/passwd | sudo -S ./run-blackbox.sh &
sleep 30 # 等启动

# 复制脚本 & 执行脚本
until scp -P 8080 ~/temp/runFemu.sh femu@127.0.0.1:~/
do
  echo "scp failed, retrying..."
  sleep 10
done

ssh -p 8080 femu@127.0.0.1 "bash ./runFemu.sh $*"

# 脚本结束 等待gc
until [[ `tail -n10 ~/femu/build-femu/log` =~ "now gc" ]]
do
  echo "waiting for gc..."
  sleep 30
done

sleep 30 # 等待gc结束

# 取回数据
scp -P 8080 femu@127.0.0.1:~/result.txt ~/temp/
scp -P 8080 femu@127.0.0.1:~/fio.json ~/temp/
tail -n10 ~/femu/build-femu/log >> ~/temp/result.txt

# 使用CBJ-SPECIAL来防止kill别人的
cat ~/.ssh/passwd | sudo -S kill -SIGINT -- $(pgrep -f "x86_64-softmmu/qemu-system-x86_64 -name FEMU-BBSSD-VM-CBJ-SPECIAL")

@REM 将脚本拷贝过去
scp -i C:\Users\CsCN\.ssh\linux-generic .\runDys.sh dys@219.223.251.60:~/temp/
scp -i C:\Users\CsCN\.ssh\linux-generic .\runFemu.sh dys@219.223.251.60:~/temp/

@REM 运行脚本
@REM @param1: LRU_LIST_LENGTH
@REM @param2: dedupe_percentage
@REM @param3: f2fs directory
set resultFile=result.txt
ssh -i C:\Users\CsCN\.ssh\linux-generic dys@219.223.251.60 "bash ~/temp/runDys.sh %1 %2 %3"
scp -i C:\Users\CsCN\.ssh\linux-generic dys@219.223.251.60:~/temp/%resultFile% .\data\

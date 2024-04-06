@REM 将脚本拷贝过去
scp -i C:\Users\CsCN\.ssh\linux-generic .\runDys.sh cbj@10.249.43.159:~/temp/
scp -i C:\Users\CsCN\.ssh\linux-generic .\runFemu.sh cbj@10.249.43.159:~/temp/

@REM 运行脚本
@REM @param1: LRU_LIST_LENGTH
@REM @param2: dedupe_percentage or replayPath
@REM @param3: f2fs directory
ssh -i C:\Users\CsCN\.ssh\linux-generic cbj@10.249.43.159 "bash ~/temp/runDys.sh %*"
scp -i C:\Users\CsCN\.ssh\linux-generic cbj@10.249.43.159:~/temp/result.txt .\data\
scp -i C:\Users\CsCN\.ssh\linux-generic cbj@10.249.43.159:~/temp/fio.json .\data\

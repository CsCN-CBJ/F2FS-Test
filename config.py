# basic settings
ENCODING = 'utf-8'
GB = 1024 * 1024 * 1024
MB = 1024 * 1024
ENTRIES_PER_BLOCK = 100
fsList = ["DedupFS", "smartdedup", "HFDedup2", "Dmdedup"]
dupRatios = [0, 25, 50, 75]
lruRatios = [3, 5, 10, 20, 50, 75]

# runData settings
TOTAL_WRITE = 36 * GB
# traceList = ['hitsz_8GB.hitsztrace', 'homes_8GB.blkparse', 'mail_8GB.blkparse', 'web_8GB.blkparse']
# dups = [0.6909, 0.3350, 0.8800, 0.2002, 0.3391]
# traceSize = 8 * 1024 * 1024 * 1024
# traceList = ['hitsz_16GB.hitsztrace', 'homes_16GB.hitsztrace', 'mail_16GB.hitsztrace', 'web_16GB.hitsztrace',
#              'Nexus-5X_16GB.hitsztrace']
# dups = [0.7566, 0.3314, 0.9099, 0.3897, 0.3210]
# traceList = ['hitsz_08.hitsztrace', 'homes_08.hitsztrace', 'mail_08.hitsztrace', 'web_08.hitsztrace',
             # 'Nexus-5X_08.hitsztrace']
# dups = [0.8107, 0.6879, 0.8873, 0.4334, 0.3313]
# traceNameList = list(map(lambda x: x.split('_')[0], traceList))
traceNameBasicList = ['hitsz', 'homes', 'mail', 'web', 'smart']
traceSize = [77.3860, 43.9153, 115.6106, 23.2718, 20.1186]
traceList = list(map(lambda x: f"{x}_fit85.hitsztrace", traceNameBasicList))
traceFileBaseNameList = list(map(lambda x: x.split('.')[0], traceList))
# traceNameList = list(map(lambda x: x.split('_')[0], traceList))
traceNameList = ['Homes', 'HomesF', 'MailF', 'WebF', 'Smart']
uniqueSize = 16 * 0.85 * GB
fixedLRU = 5  # 5%

GB = 1024 * 1024 * 1024
ENTRIES_PER_BLOCK = 100
fsList = ["DedupFS", "smartdedup"]

TOTAL_WRITE = 16 * GB  # 16GB
# traceList = ['hitsz_8GB.hitsztrace', 'homes_8GB.blkparse', 'mail_8GB.blkparse', 'web_8GB.blkparse',
#              'smartdedup_8GB.hitsztrace']
# dups = [0.6909, 0.3350, 0.8800, 0.2002, 0.3391]
# traceSize = 8 * 1024 * 1024 * 1024
traceList = ['hitsz_16GB.hitsztrace', 'homes_16GB.hitsztrace', 'mail_16GB.hitsztrace', 'web_16GB.hitsztrace',
             'Nexus-5X_16GB.hitsztrace']
dups = [0.7566, 0.3314, 0.9099, 0.3897, 0.3210]
traceSize = 16 * GB


# plt settings
colors = ['b', 'r', 'g', 'y', 'c', 'm']
opacity = 0.8
bar_width = 0.35

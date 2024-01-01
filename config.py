ENTRIES_PER_BLOCK = 100
fsList = ["DedupFS", "smartdedup"]

TOTAL_WRTIE = 5 * 1024 * 1024 * 1024  # 5GB
traceList = ['hitsz_8GB.hitsztrace', 'homes_8GB.blkparse', 'mail_8GB.blkparse', 'web_8GB.blkparse',
             'smartdedup_8GB.hitsztrace']
dups = [0.6909, 0.3350, 0.8800, 0.2002, 0.3391]
traceSize = 8 * 1024 * 1024 * 1024

# plt settings
colors = ['b', 'r', 'g', 'y', 'c', 'm']
opacity = 0.8
bar_width = 0.35

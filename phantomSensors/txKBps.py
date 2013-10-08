#!/usr/bin/python
# transfered kilobytes per second
# simple script to get outgoing kilobytes per second (averaged over the collection interval) on eth0
# to be used in conjunction with tcollector
import sys
import time
COLLECTION_INTERVAL = 60  # seconds
load = 0
prevLoad = 0
path = '/sys/class/net/eth0/statistics/tx_bytes'
while True:
    try:
        tx = open(path)
        tx1 = int(tx.read())
	tx.close()
    except:
	load = prevLoad
    time.sleep(COLLECTION_INTERVAL)
    try:
        tx = open(path)
        tx2 = int(tx.read())
        tx.close()
        load = (tx2 - tx1) / (COLLECTION_INTERVAL * 1024)
    except:
        load = prevLoad
    ts = int(time.time()) # timestamp
    print "test.shoal.load %s %d" % (ts, load)
    prevLoad = load
    sys.stdout.flush()

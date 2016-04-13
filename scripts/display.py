#!/usr/bin
import psutil
import time
import math
import os
import sensors
import socket

BLOCK={1:u'\u2588',
       0.75:u"#",
       0.5:u"*",
       0.25:u"|",
       0:' '}

DSKNAME = {'/':'root','/mnt/stg':'data'}
CHPNAME = {'radeon-pci-0200':'GPU: '}

class co:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YEL = '\033[93m'
    RED= '\x1b[1;37;41m'
    RED2= '\033[91m' 
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

rcol = {'active':co.GREEN,
        'check':co.BLUE,
        'recovery':co.YEL,
        'inactive':co.RED2,
        'degraded':co.RED2,
        'resync':co.YEL}

def readRaid():
    with open('/proc/mdstat') as h: raw = h.read()
    h.close()
    out = {}
    r = raw.split('unused')[0].split('md')[1:]
    for a in r:
        outb = {}
        outb.update({'bar':'', 'prog':100,'finish':'','speed':''})
        b = a.split('\n')
        c = b[0].split(' ')
        id = 'md%s'%c[0]
        outb.update({'status':c[2],'type':c[3].strip(),'disks':c[4:]})
        c = b[1].split(' ')
        outb.update({'state':c[-1],'number':c[-2]})
        if '_' in c[-1]: outb.update({'status':'degraded'})
        if outb['type']=='raid1':t=4
        elif outb['type']=='raid5':t=5
        else:t=4
        if len(b) > t:
            c = b[2].split(' ')
            if len(c) <= 7: outb.update({'bar':co.RED2+'[.......DELAYED.......]'+co.ENDC,'prog':0})
            else:
                outb.update({'speed':c[-1].split('=')[1],'finish':c[-2].split('=')[1],
                             'prog':float(c[-4].split('%')[0]),'status':c[8],'bar':c[6]})
        out.update({id:outb})
    return out

class monitor:
    hdd = {}
    def __init__(self):
        self.netCounters = psutil.net_io_counters(pernic=True)
        sensors.init()
        while True:
            self.updateInfoPerSecond()
            self.updateInfoPerMinute()
            self.display()

    def display(self):
        os.system('clear')
        print '%sCPU Cores:%s'%(co.BOLD, co.ENDC)
        p = round(sum(self.cpuPercent) / float(len(self.cpuPercent)), 1)
        for i in range(0,len(self.cpuPercent),2):
            c0 = self.drawGraph(23, self.cpuPercent[i])
            c1 = self.drawGraph(23, self.cpuPercent[i+1])
            print '   C%s: %s %-5s%%  C%s: %s %-5s%%'%(i,c0,self.colP(self.cpuPercent[i]),i+1,c1,self.colP(self.cpuPercent[i+1]))

        print '\n%sMemory:%s'%(co.BOLD,co.ENDC)
        r = self.drawGraph(23.0, self.ramInfo.percent)
        s = self.drawGraph(23.0, self.swapInfo.percent)
        print '   RAM %s %s%% SWAP %s %s%%'%(r,self.colP(self.ramInfo.percent),s,self.colP(self.swapInfo.percent))

        print '\n%sDisks:%s'%(co.BOLD,co.ENDC)
        for mnt, info in self.diskPartsUsage.iteritems():
            gr = self.drawGraph(62, info.percent)
            if mnt in DSKNAME.keys():n = DSKNAME[mnt]
            else: n = mnt
            print '  %-4s %s %+4s%%\n'%(n,gr, self.colP(info.percent))

        print '%sHARDWARE MONITORING:%s'%(co.BOLD,co.ENDC)
        print '  CPU: %-3sC Mobo: %-3sC GPU: %-3sC'%(self.colT(self.sensors[8]),self.colT(self.sensors[9]),self.colT(self.sensors[0]))
        print '  %sVcore:%s %-4sV  %s+3.3V_Rail:%s %-4sV  %s+5V_Rail:%s %-4sV  %s+12V_Rail:%s %-4sV '%(co.BOLD,co.ENDC,self.sensors[1],co.BOLD,co.ENDC,self.sensors[2],co.BOLD,co.ENDC,self.sensors[3],co.BOLD,co.ENDC,self.sensors[4])
        k = self.hdd.keys()
        k.sort()
        print "  Disks: ",
        for key in k:
            print '  %s%sC'%(key, self.colT(self.hdd[key])),

        print '\n\n%sRAID ARRAYS:%s'%(co.BOLD,co.ENDC)
        for key, dat in self.raid.iteritems():
            print ' %sArray: %s%s (%s)'%(co.BOLD,key,co.ENDC,dat['type'])
            print '   Status: %s%-8s%s %-5s %s'%(rcol[dat['status']],dat['status'].upper(),co.ENDC,dat['number'],dat['state'])
            if not dat['bar'] == '':
                print '   %s%s %s%s%% %s%s'%(rcol[dat['status']],dat['bar'],co.ENDC+co.BOLD,dat['prog'],dat['finish'],co.ENDC)
            else: print ''

    def updateInfoPerSecond(self):
        self.cpuPercent = psutil.cpu_percent(interval=1, percpu=True)
        self.ramInfo = psutil.virtual_memory()
        self.swapInfo = psutil.swap_memory()
        self.diskParts = psutil.disk_partitions()
        self.diskPartsUsage = {}
        for disk in self.diskParts:
            mnt = disk.mountpoint
            usage = psutil.disk_usage(mnt)
            self.diskPartsUsage.update({mnt:usage})

        self.oldNetCounters = self.netCounters
        self.netCounters = psutil.net_io_counters(pernic=True)
        self.netNicStats = psutil.net_if_stats()
        self.netStats = {}
        for nic in self.netCounters.iterkeys():
            m = self.netNicStats[nic].speed
            sent = self.netCounters[nic].bytes_sent
            recv = self.netCounters[nic].bytes_recv
            oSent = self.oldNetCounters[nic].bytes_sent
            oRecv = self.oldNetCounters[nic].bytes_recv
            sent = (sent-oSent)*8
            recv = (recv-oRecv)*8
            try: pr = recv/(m*1000.0)
            except ZeroDivisionError: pr = 0
            try: ps = sent/(m*1000.0)
            except ZeroDivisionError: ps = 0
            self.netStats.update({nic:{'sent':sent,
                                       'recv':recv,
                                       's_per':ps,
                                       'r_per':pr}})

        self.sensors = []
        for c in sensors.iter_detected_chips():
            for f in c:
                self.sensors.append(f.get_value())
        self.raid = {}
        self.raid = readRaid()
        #fetches the data from hddtemp
        #self.hdd = {}
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(('localhost',7634))
            data = s.recv(4096)
            s.close()
            parts = data.split('|')
            for i in range(1,len(parts),5):
                self.hdd[parts[i].split('/dev/')[1]] = int(parts[i+2])
        except: pass

    def updateInfoPerMinute(self):
        pass

    def drawGraph(self, length, percent, char=u'\u2588'):
        col = co.GREEN
        if percent >= 90: col = co.RED2
        elif percent >= 70: col = co.YEL
        elif percent >= 50: col = co.BLUE
        len=int(math.floor(percent/(100/float(length))))
        k = BLOCK.keys()
        k.sort()
        k = [x for x in k if x<(percent-(((100.0/length)*len)))/(100.0/length)]
        k.insert(0,0)
        return '[%s%s%s%s%s]'%(col,len*char,BLOCK[k[-1]],' '*(int(length-len)),co.ENDC)

    def drawGraphI(self, length, percent, char=u'\u2588'):
        col = co.RED
        if percent >= 90: col = co.GREEN
        elif percent >= 70: col = co.BLUE
        elif percent >= 40: col = co.YEL
        len=int(math.floor(percent/(100/float(length))))
        k = BLOCK.keys()
        k.sort()
        k = [x for x in k if x<(percent-(((100.0/length)*len)))/(100.0/length)]
        k.insert(0,0)
        return '[%s%s%s%s%s]'%(col,len*char,BLOCK[k[-1]],' '*(int(length-len)),co.ENDC)

    def colP(self,percent):
        col = co.GREEN
        if percent >= 90: col = co.RED2
        elif percent >= 70: col = co.YEL
        elif percent >= 50: col = co.BLUE
        return str('%s%5s%s'%(col,percent,co.ENDC))

    def colT(self,temp):
        col = co.GREEN
        if temp >= 70: col = co.RED2
        elif temp >= 55: col = co.YEL
        elif temp >= 45: col = co.BLUE
        return str('%s%3i%s'%(col,temp,co.ENDC))



if __name__ == '__main__':
    while True:
        try:m = monitor()
        except KeyboardInterrupt: break
        except BaseException as er: print er
        sensors.cleanup()

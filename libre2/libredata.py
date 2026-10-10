#!/usr/bin/env python3

import csv, sys, datetime, os, re

class libredata(object):
    
    period = 35
    def __init__(self, fname, use_blood=False, defmeals=None):
        self.fname = fname
        self.use_blood = use_blood
        self.mindate = datetime.datetime.combine(datetime.date.today()-datetime.timedelta(40), datetime.time(0,0,0))
        self.defmeals=defmeals if defmeals is not None else [7*60, 13*60, 17*60]

    def readCSV(self):
        fdic={
            '0':[], '1':[],'5':[], '6': []
            }
        with open(self.fname, newline='') as csvfile:
            reader=csv.reader(csvfile)
            for a in reader:
                if a[3] not in ('0','1','5','6'):
                    continue
                ti= datetime.datetime.strptime(a[2],'%d-%m-%Y %H:%M')
                if ti < self.mindate:
                    continue
                typ = a[3]
                
                if len(fdic[typ]) == 0 or ti > fdic[typ][-1][0]:
                    if typ == '6':
                        if (blo := self.isblood(a[13])) is not None:
                            #print(blo)
                            fdic[typ].append([ti, blo])
                        continue
                    ct=int(a[4] if typ == '0' else a[5] if typ == '1' else '1')
                    fdic[typ].append([ti, ct])
        tmr=[]
        tma=list(x[0] for x in fdic['1'])
        for a in fdic['0']:
            if a[0] not in tma:
                tmr.append(a)
        tmr.extend(fdic['1'])
        self.glu = self.uniq(tmr)
        self.mls = self.uniq(fdic['5'])
        self.pre = self.uniq(fdic['6'])

    @staticmethod
    def uniq(lista):
        out=[]
        dgs=set()
        for item in lista:
            if item[0] not in dgs:
                out.append(item)
                dgs.add(item[0])
        return sorted(out)

    @staticmethod
    def isblood(fld):
        r=re.match(r'\D*(\d+)[/\s]+(\d+)+[:\s]+(\d+)\D*$',fld)
        if r is None:
            return None
        sy = int(r.group(1))
        di = int(r.group(2))
        pu = int(r.group(3))
        if sy < 90 or sy > 250 or di < 50 or di > 150 or pu <40 or pu > 180:
            return None
        
        return (sy,di,pu)

    @staticmethod
    def daymin(dat):
        dte = dat.strftime('%d-%m-%Y %H:%M')
        return dte[:10], int(dte[11:13]) * 60 + int(dte[14:16])
    
    def mkdata(self):
        self.dlist = []
        self.ddict = {}
        self.mdict = {}
        self.bdict = {}
        self.smpl = None
        for g in self.glu:
            dag, mnt = self.daymin(g[0])
            if dag not in self.dlist:
                self.dlist.append(dag)
                self.ddict[dag] = []
                self.mdict[dag] = []
                self.bdict[dag] = []
            self.ddict[dag].append([mnt,int(g[1])])
        #self.dlist.sort() # should be soered?
        llen = len(self.dlist)
        if llen > self.__class__.period:
            rmv  = self.dlist[:llen-self.__class__.period]
            self.dlist = self.dlist[-self.__class__.period:]
            for a in rmv:
                self.ddict.pop(a)
        for g in self.mls:
            dag, mnt = self.daymin(g[0])            
            if dag not in self.dlist:
                continue
            if len(self.mdict[dag]) < 3:
                self.mdict[dag].append(mnt)
        if self.use_blood:
            for g in self.pre:
                dag, mnt = self.daymin(g[0])            
                if dag not in self.dlist:
                    continue
                pry = '%02d:%02d<br>%d/%d %d' % (mnt // 60, mnt % 60, g[1][0],g[1][1],g[1][2])
                if len(self.bdict[dag]) < 2:
                    self.bdict[dag].append(pry)
                else:
                    self.bdict[dag][1] = pry
        self.remdic()
        self.mksimple()


    #add missing meals houre
    def remdic(self):
        for dag in self.mdict:
            dl=self.mdict[dag]
            if len(dl) >= 3:
                continue
            if len(dl) == 0:
                dl.extend(self.defmeals)
                continue
            dcs = [0,0,0]
            for a in dl:
                if a < 11 * 60:
                    dcs[0] = a
                elif a < 17 * 60:
                    dcs[1] = a
                else:
                    dcs[2] = a
            for a in range(3):
                if dcs[a] == 0:
                    dcs[a] = self.defmeals[a]
            self.mdict[dag] = dcs

    #create simple glucose values after meals
    def mksimple(self):
        self.smpl={}
        for dag in self.dlist:
            sl=[self.glike(dag, 6*60)]
            for mnt in self.mdict[dag]:
                sl.append(self.glike(dag, mnt+150))
            self.smpl[dag]=sl
            
    def glike(self, dag, mnt):
        g=self.ddict[dag]
        if mnt < g[0][0] or mnt > g[-1][0]:
            return 0
        ps=-1
        for p in g:
            if p[0] >= mnt:
                return p[1]
        return 0
                

    
        

if __name__ == "__main__":
    lr=libredata(sys.argv[1])
    lr.readCSV()
    lr.mkdata()


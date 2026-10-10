#!/usr/bin/env python3

from PIL import Image, ImageDraw, ImageShow
import base64, io

def linesplit(line):
    lines = []
    while len(line) > 1:
        lout=[line.pop(0)]
        while len(line) > 0 and line[0][0] < lout[-1][0]+25:
            lout.append(line.pop(0))
        if len(lout) > 1:
            lines.append(lout)
    return lines
            
        
        

class librepic(object):
    viewer=ImageShow.DisplayViewer()
    def __init__(self, glu, meal, width = 480):
        self.width = int(width)
        self.height = int((width * 2) / 4)
        self.glu = glu
        self.meal = meal
        self.im = Image.new('L',(self.width, self.height), 255)
        self.draw=ImageDraw.Draw(self.im)
        self.scale = self.height / 340
        self.draw.rectangle([(0,self.ypos(80)),(self.width-1,self.height)], fill=200)
        self.draw.rectangle([(0,0),(self.width-1,self.ypos(180))], fill=200)
        self.draw.rectangle([(0,0),(self.width-1,self.ypos(240))], fill=160)
        for m in self.meal:
            self.draw.line([(self.xpos(m),0), (self.xpos(m), self.height)], 100, 2)

        #print("A",self.glu[0])
        lsp=linesplit(self.glu)
        
        for line in lsp:
            #print(line[0])
            bs=list(
                (self.xpos(g[0]), self.ypos(g[1])) for g in line)
            #print(bs)
            self.draw.line(bs, 0,2)

    def ypos(self, y):
        return int(self.height-self.scale * y)

    def xpos(self, x):
        return int((x * self.width)/1440)

    def show(self):        
        self.__class__.viewer.show(self.im)

    def get64(self):
        b=io.BytesIO()
        self.im.save(b, format='PNG')
        bb = base64.b64encode(b.getvalue()).decode('ascii')
        return "data:image/png;base64,"+bb

if __name__ == '__main__':
    #pic=librepic(None, [7*60, 13*60, 17*60])
    print(linesplit(
        [(0,),(15,),(30,),(80,),(90,)]))


    

    

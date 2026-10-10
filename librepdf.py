#!/usr/bin/env python3

from libre2 import libredata, librepng
import sys

#header line 
header = "ethanak"

#accept blood pressure comments
use_blood = True

#standard meals in minutes oe None for default
def_meals = [7*60, 14*60, 18*60+30]

#create pdf instead of html
create_pdf = True

#pdf viewer with optional parameters or None
#pdf_viewer = ["atril","-s"]
pdf_viewer = "evince"

#output filename (html or pdf extension will be added)
outname = "temp_gluco"

#nothing interesting below

cells = 5
rows = 4 if use_blood else 3

template="""
<!DOCTYPE html>
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<title>Libre 2 glucose</title>
<style type="text/css">
html, body {
    margin: 0pt;
    padding: 0pt;
    font-family: monospace;
    font-size: 13pt;
    color: black;
    max-height: 23cm;
    }
    
h1 {
    padding: 0;
    margin: 2pt auto;
    font-size: 24pt;
    text-align: center;
    }
table {
    border-collapse: collapse;
    margin: 1em;
}
thead { display: table-header-group }
tfoot { display: table-row-group }
tr { page-break-inside: avoid }

th, td {
    border-style: solid;
    border-color: black;
    border-width: 1px;
    padding: 1pt 5pt;
}

th.ubor {
    background-color: #ddd;
    padding-top: 4pt;
    padding-bottom: 4pt;
    font-size: 2em;
    }

th.lbor, td.lbor {
    border-width: 1px 1px 1px 3px;
}
    

td {
    text-align:left;
}

th {
    vertical-align: top;
}

td.czczo {
    background-color: #ddd;
}
    
tr.rodd {
    background-color: #eee;
}

</style>
<body>
<h1>%HEADING%</h1>
<table>
<tbody>
%TABELA%
</tbody>
</table>
</body>
</html>
"""

rowtemp = [
    '<th colspan="4" class="ubor">%DATA</th>',
    '<td colspan="4" style="padding:0"><img src="%IMAGE"></td>',
    '<td class="czczo">%G0</td><td>%G1</td><td>%G2</td><td>%G3</td>',
    '<td colspan="2">%PA</td><td colspan="2">%PB</td>'
]


data=libredata.libredata(sys.argv[1], use_blood, def_meals)
data.readCSV()
data.mkdata()

table= []
trows = ['','','','']
cnr = 0
#print (data.dlist)
for dag in data.dlist:
    trows[0] += rowtemp[0] . replace('%DATA',dag)
    dcs=data.ddict[dag]
    mcs=data.mdict[dag]
    scs=data.smpl[dag]
    png=librepng.librepic(dcs,mcs,288)
    trows[1] += rowtemp[1] . replace('%IMAGE',png.get64())
    g4=list(str(a) if a > 0 else 'n/a' for a in scs)
        
    trows[2] += rowtemp[2]. replace('%G0',g4[0]) . replace('%G1',g4[1]) . \
        replace('%G2',g4[2]).replace('%G3',g4[3])
    if use_blood:
        pcs=data.bdict[dag] if data.bdict is not None else []
        pcl=['n/a','n/a']
        if len(pcs) > 0:
            pcl[0] = pcs[0]
        if len(pcs) > 1:
            pcl[1] = pcs[1]
        trows[3] += rowtemp[3].replace('%PA', pcl[0]).replace('%PB', pcl[1])
    cnr += 1
    if cnr >= cells:
        for a in range(rows):
            table.append('<tr>%s</tr>' % trows[a])
            trows[a] = ''
        cnr = 0

if cnr > 0:
    trows[0] += '<td rowspan="%d" colspan="%d">&nbsp</td>' % (rows,4 * (cells-cnr))
    for a in range(rows):
        table.append('<tr>%s</tr>' % trows[a])
        
table='\n'.join(table)
html=template.replace('%TABELA%',table).replace('%HEADING%', header)

if create_pdf:
    try:
        import pdfkit
    except:
        create_pdf = False

if not create_pdf:
    import os
    fname=outname+".html"
    open(fname,'w').write(html)
    try:
        import webbrowser
        webbrowser.open('file://%s' % os.path.realpath(fname))
    except:
        pass
    exit(0) 
options={
        'page-size': 'A4',
        'encoding': 'UTF-8'
    }
    
import pdfkit
fname=outname+'.pdf'
pdfkit.from_string(html,fname,options=options)
if pdf_viewer is not None:
    import subprocess
    viewer = pdf_viewer
    if isinstance(pdf_viewer,str):
        viewer = [pdf_viewer]
    else:
        viewer = list(pdf_viewer)
    viewer.append(fname)
    subprocess.call(viewer)

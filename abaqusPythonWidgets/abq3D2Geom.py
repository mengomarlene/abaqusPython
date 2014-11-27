# python script for abaqus to create geometry from 3D Orphan mesh
# 2012/05 Rupert Feldbacher - Graz University of Technology
from abaqusConstants import *
######## Getting input and creating temporary parts
fields = (('Modelname:','M'), ('Partname:', 'P'), 
    ('Keep internal faces (Y/N) ?','N'),('Try to add cells (Y/N) ?','N'), 
    ('Try to keep sets/surfaces (Y/N) ?','N'))
moname, paname, intfacYN, cellsYN, setsYN = getInputs(
    fields=fields, label='Specify Model and Part:', 
    dialogTitle='Create geometry from Orphan Mesh', )
xmodel=mdb.models[moname]
wpart=xmodel.parts[paname]
xpart=xmodel.Part(name=paname+'_geom_temp',dimensionality=THREE_D,type=DEFORMABLE_BODY)
ypart=xmodel.Part(name=paname+'_temp',objectToCopy=xmodel.parts[paname])
######## create shell (internal element faces are lost) and set up view
if intfacYN=='N' or intfacYN=='n':
    ypart.convertSolidMeshToShell()
session.viewports[session.currentViewportName].setValues(displayedObject=xpart)
session.viewports[session.currentViewportName].view.rotate(
            xAngle=-60,yAngle=0,zAngle=-135,mode=TOTAL)
######### create wire edges
print 'Generating Wires'
e=ypart.elementEdges
l=0
m=0
e20=len(e)/20
wiredata=[]
# read nodal data from ypart (copied model)
for i in range (0,len(e)):
    en=e[i].getNodes()
    points=[]
    for j in range (0,len(en)):
        points+=[en[j].coordinates]
    wiredata+=[points]
print 'wiredata was read'
# create wire splines for each element edge
for i in range (0,len(e)):
    xpart.WireSpline(points=wiredata[i], 
        mergeWire=ON,meshable=ON, smoothClosedSpline=ON)
    l=l+1
    if l > e20:
        l=0
        m=m+1
        print i+1,' of ',len(e),' wires completed'
        session.viewports[session.currentViewportName].view.fitView(drawImmediately=TRUE)
print '100% of wires completed'
session.viewports[session.currentViewportName].view.fitView(drawImmediately=TRUE)
######### create faces
print 'Generating Faces'
e=ypart.elementFaces
l=0
m=0
n=[]
e20=len(e)/20
for i in range (0,len(e)):
    ee=e[i].getElemEdges()
    edl=[]
    for j in range (0,len(ee)):
        en=ee[j].getNodes()
        if len(en)==3:      # quad elems - take midside node
            co2=en[1].coordinates
        else:               # lin elems - calculate mid point
            co2=[]
            for k in range (0,len(en[0].coordinates)):
                co0=en[0].coordinates[k]
                co1=en[1].coordinates[k]
                co2+=[(co0+co1)/2]
        ed=xpart.edges.findAt(co2)
        edl+=[ed]
# generate faces - try different settings and order
    try:
        xpart.AddFaces(edgeList = edl, tryAnalytical=True)
    except AbaqusException, message:
        try:
            xpart.AddFaces(edgeList = edl, tryAnalytical=False)
        except AbaqusException, message:
            edl.sort()
            try:
                xpart.AddFaces(edgeList = edl, tryAnalytical=True)
            except AbaqusException, message:
                try:
                    xpart.AddFaces(edgeList = edl, tryAnalytical=False)
                except AbaqusException, message:
                    n+=[i]
                    print message, ' ... skipping this face ...'
    l=l+1
    if l > e20:
        l=0
        m=m+1
        print i+1,' of ',len(e),' faces completed'
        session.viewports[session.currentViewportName].forceRefresh()
# try again after rest of faces has been completed
o=0
if len(n) > 0:
    print 'Trying to add missing faces'
    for i in range (0,len(n)):
        ee=e[n[i]].getElemEdges()
        edl=[]
        for j in range (0,len(ee)):
            en=ee[j].getNodes()
            if len(en)==3:
                co2=en[1].coordinates
            else:    
                co2=[]
                for k in range (0,len(en[0].coordinates)):
                    co0=en[0].coordinates[k]
                    co1=en[1].coordinates[k]
                    co2+=[(co0+co1)/2]
            ed=xpart.edges.findAt(co2)
            edl+=[ed]
        try:
            xpart.AddFaces(edgeList = edl, tryAnalytical=True)
            o+=1
        except AbaqusException, message:
            try:
                xpart.AddFaces(edgeList = edl, tryAnalytical=False)
                o+=1
            except AbaqusException, message:
                edl.sort()
                try:
                    xpart.AddFaces(edgeList = edl, tryAnalytical=True)
                    o+=1
                except AbaqusException, message:
                    try:
                        xpart.AddFaces(edgeList = edl, tryAnalytical=False)
                        o+=1
                    except AbaqusException, message:
                        print message, ' ... skipping this face ...'
    print o,' of ',len(n),' missing faces completed'
if len(n)-o == 0:
    print '100% of faces completed'
else:
    print 'Generation of ',len(n)-o,' face(s) failed'
session.viewports[session.currentViewportName].forceRefresh()
######## adding cells and cleaning up
if cellsYN=='Y' or cellsYN=='y':
    print 'Adding cells'
    try:
        xpart.AddCells(faceList = xpart.faces[0:len(xpart.faces)])
    except AbaqusException, message:
        print message
del xmodel.parts[paname+'_temp']
zpart=xmodel.Part(name=paname+'_geom', objectToCopy=xpart, compressFeatureList=ON)
del xmodel.parts[paname+'_geom_temp']
zpart.features.changeKey(fromName=zpart.features.keys()[0],
    toName='geometry_of_'+paname)
session.viewports[session.currentViewportName].setValues(displayedObject=zpart)
session.viewports[session.currentViewportName].view.rotate(
            xAngle=-60,yAngle=0,zAngle=-135,mode=TOTAL)
session.viewports[session.currentViewportName].view.fitView(drawImmediately=TRUE)
########### adding sets and surfaces
if setsYN=='Y' or setsYN=='y':
    setkeys=wpart.allSets.keys()
    for i in range(len(setkeys)):
        print 'Generating Set:',setkeys[i]
        elfailed=0
        nofailed=0
# read element sets and try to find cells
        esettoadd=[]
        for j in range (0,len(wpart.allSets[setkeys[i]].elements)):
            wconn=wpart.sets[setkeys[i]].elements[j].connectivity
# calculate mean coordinates to find point inside element/cell
            meancoords=[]
            for k in range (0, len(wpart.nodes[wconn[0]].coordinates)):
                meancoords+=[0]
                for l in range (0, len(wconn)):
                    meancoords[k]+=wpart.nodes[wconn[l]].coordinates[k]/len(wconn)
            etoadd=zpart.cells.findAt(((meancoords), ),printWarning=FALSE)
            if not etoadd:
                elfailed+=1
            esettoadd+=(etoadd,)
# read nodes sets and try to find vertices
        nsettoadd=[]
        for j in range (0,len(wpart.allSets[setkeys[i]].nodes)):
            coords=wpart.allSets[setkeys[i]].nodes[j].coordinates
            ntoadd=zpart.vertices.findAt(((coords), ),printWarning=FALSE)
            if not ntoadd:
                nofailed+=1
            nsettoadd+=(ntoadd,)
        if nsettoadd or esettoadd:
            zpart.Set(vertices=nsettoadd,cells=esettoadd,name=setkeys[i])
        if elfailed!=0:
            print elfailed,'Cell(s) could not be added to set',setkeys[i]
        if nofailed!=0:
            print nofailed,'Point(s) could not be added to set',setkeys[i]
######## surfaces
    surfkeys=wpart.surfaces.keys()
    elnonum=[4,6,8,10,15,20]
# connectivity for faces of solid elements
    facecon=[((0,1,2),(0,3,1),(1,3,2),(2,3,0)),
        ((0,1,2),(3,5,4),(0,3,4,1),(1,4,5,2),(2,5,3,0)),
        ((0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)),
        ((0,1,2,4,5,6),(0,3,1,4,7,8),
        (1,3,2,5,8,9),(2,3,0,6,7,9)),
        ((0,1,2,6,7,8),(3,5,4,9,10,11),(0,3,4,1,6,12,9,13),
        (1,4,5,2,7,13,10,14),(2,5,3,0,8,12,11,14)),
        ((0,1,2,3,8,9,10,11),(4,7,6,5,12,13,14,15),(0,4,5,1,8,16,12,17),
        (1,5,6,2,9,17,13,18),(2,6,7,3,10,18,14,19),(3,7,4,0,11,16,15,19))]
# read information for each surface
    for i in range(0,len(surfkeys)):
        print 'Generating Surface:',surfkeys[i]
        susettoadd=[]
        sufailed=0
        elems=wpart.surfaces[surfkeys[i]].elements
        sides=wpart.surfaces[surfkeys[i]].sides
# find faces on elements
        for j in range(0, len(elems)):
            nodes=[]
            conlen=len(elems[j].connectivity)
            if sides[j]==BOTHSIDES or sides[j]==SIDE1 or sides[j]==SIDE2:
                nodes=elems[j].connectivity
            else:
                elnocon=facecon[elnonum.index(conlen)][int(str(sides[j])[4])-1]
                for k in range (0,len(elnocon)):
                    nodes+=[elems[j].connectivity[elnocon[k]]]
# calculate mean coordinates to find faces in solid part
            meancoords=[]
            for k in range(0,len(wpart.nodes[nodes[0]].coordinates)):
                meancoords+=[0]
                for l in range(0,len(nodes)):
                    meancoords[k]+=wpart.nodes[nodes[l]].coordinates[k]/len(nodes)
#### alternative approach using getClosest
#                sutoadd=zpart.faces.getClosest(coordinates=((meancoords),))
#                if not sutoadd:
#                    sufailed+=1
#                sutoadd=zpart.faces.findAt((sutoadd[0][0].pointOn[0],))
            sutoadd=zpart.faces.findAt(((meancoords), ),printWarning=FALSE)
            if not sutoadd:
                sufailed+=1
            susettoadd+=((sutoadd),)
        if susettoadd:
            zpart.Surface(side1Faces=susettoadd, name=surfkeys[i])
        if sufailed!=0:
            print sufailed,'Face(s) could not be added to surface',surfkeys[i]
print 'script finished'




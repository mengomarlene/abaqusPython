# python script for abaqus to create geometry from 2D Orphan mesh
from abaqusConstants import *
######## Getting input and creating temporary parts
fileName = 'D:/myWork/MicroscopyModels/2DTensileTestsInpFiles/tt01_01_nobridgesScaled2D.inp'
fileName.replace('/',os.sep)
moName = 'tt01_01_nobridges'
paName = 'PART-1'
initModel = mdb.ModelFromInputFile(inputFileName=fileName, name=moName)
initPart = initModel.parts[paName]
newPartWithGeo = initModel.Part(name=paName+'_geom_temp',dimensionality=TWO_D_PLANAR,type=DEFORMABLE_BODY)
newPart = initModel.Part(name=paName+'_temp',objectToCopy=initModel.parts[paName])

######### create wire edges
print 'Generating Wires'
edges = newPart.elementEdges
wiredata=list()
# read nodal data from newPart (copied model)
for edge in edges:
    points=list()
    for node in edge.getNodes():
        points.append(node.coordinates)
    wiredata.append(points)
print 'wiredata was read'
#l=0#in gui
#e20=len(edges)/20#in gui
# create wire splines for each element edge
print 'generating %i wires - this is going to take a while'%len(wiredata)
#for i,wire in enumerate(wiredata):
#    newPartWithGeo.WireSpline(points=wire, mergeWire=ON,meshable=ON, smoothClosedSpline=ON)
    #this is just in gui
    #l=l+1
    #if l > e20:
    #    l=0
    #    print i+1,' of ',len(edges),' wires completed'
    #    session.viewports[session.currentViewportName].view.fitView(drawImmediately=TRUE)
    # end of just in gui
#print '100% of wires completed'
#session.viewports[session.currentViewportName].view.fitView(drawImmediately=TRUE)

######### create faces
if 0:
    print 'Generating Faces'
    f=newPart.elementFaces
    #l=0#gui
    n=list()
    e20=len(f)/20
    for i,face in enumerate(f):
        ee=face.getElemEdges()
        edl=list()
        for ee in face.getElemEdges():
            en=ee.getNodes()
            if len(en)==3:      # quadratic elems - take midside node
                co2=en[1].coordinates
            else:               # linear elems - calculate mid point
                co2=[]
                for k in range (0,len(en[0].coordinates)):
                    co0=en[0].coordinates[k]
                    co1=en[1].coordinates[k]
                    co2.append((co0+co1)/2)
            ed=newPartWithGeo.edges.findAt(co2)
            edl.append(ed)
    # generate faces - try different settings and order
        try:
            newPartWithGeo.CoverEdges(edgeList = edl, tryAnalytical=True)
        except AbaqusException, message:
            try:
                newPartWithGeo.CoverEdges(edgeList = edl, tryAnalytical=False)
            except AbaqusException, message:
                edl.sort()
                try:
                    newPartWithGeo.CoverEdges(edgeList = edl, tryAnalytical=True)
                except AbaqusException, message:
                    try:
                        newPartWithGeo.CoverEdges(edgeList = edl, tryAnalytical=False)
                    except AbaqusException, message:
                        n.append(i)
                        print message, ' ... skipping this face ...'
    #in gui
#    l=l+1
#    if l > e20:
#        l=0
#        print i+1,' of ',len(f),' faces completed'
#        session.viewports[session.currentViewportName].forceRefresh()
    #end in gui
# try again after rest of faces has been completed
    o=0
    if len(n) > 0:
        print 'Trying to add missing faces'
        for i in range (0,len(n)):
            ee=f[n[i]].getElemEdges()
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
                ed=newPartWithGeo.edges.findAt(co2)
                edl+=[ed]
            try:
                newPartWithGeo.CoverEdges(edgeList = edl, tryAnalytical=True)
                o+=1
            except AbaqusException, message:
                try:
                    newPartWithGeo.CoverEdges(edgeList = edl, tryAnalytical=False)
                    o+=1
                except AbaqusException, message:
                    edl.sort()
                    try:
                        newPartWithGeo.CoverEdges(edgeList = edl, tryAnalytical=True)
                        o+=1
                    except AbaqusException, message:
                        try:
                            newPartWithGeo.CoverEdges(edgeList = edl, tryAnalytical=False)
                            o+=1
                        except AbaqusException, message:
                            print message, ' ... skipping this face ...'
        print o,' of ',len(n),' missing faces completed'
    if len(n)-o == 0:
        print '100% of faces completed'
    else:
        print 'Generation of ',len(n)-o,' face(s) failed'
    session.viewports[session.currentViewportName].forceRefresh()

# del initModel.parts[paName+'_temp']
# zpart=initModel.Part(name=paName+'_geom', objectToCopy=newPartWithGeo, compressFeatureList=ON)
# del initModel.parts[paName+'_geom_temp']
# zpart.features.changeKey(fromName=zpart.features.keys()[0], toName='geometry_of_'+paName)

########### adding sets and surfaces
if 0:
    setkeys=initPart.allSets.keys()
    for i in range(len(setkeys)):
        print 'Generating Set:',setkeys[i]
        elfailed=0
        nofailed=0
    # read element sets and try to find cells
        esettoadd=[]
        for j in range (0,len(initPart.allSets[setkeys[i]].elements)):
            wconn=initPart.sets[setkeys[i]].elements[j].connectivity
    # calculate mean coordinates to find point inside element/cell
            meancoords=[]
            for k in range (0, len(initPart.nodes[wconn[0]].coordinates)):
                meancoords+=[0]
                for l in range (0, len(wconn)):
                    meancoords[k]+=initPart.nodes[wconn[l]].coordinates[k]/len(wconn)
            etoadd=zpart.cells.findAt(((meancoords), ),printWarning=FALSE)
            if not etoadd:
                elfailed+=1
            esettoadd+=(etoadd,)
    # read nodes sets and try to find vertices
        nsettoadd=[]
        for j in range (0,len(initPart.allSets[setkeys[i]].nodes)):
            coords=initPart.allSets[setkeys[i]].nodes[j].coordinates
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
    surfkeys=initPart.surfaces.keys()
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
        elems=initPart.surfaces[surfkeys[i]].elements
        sides=initPart.surfaces[surfkeys[i]].sides
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
            for k in range(0,len(initPart.nodes[nodes[0]].coordinates)):
                meancoords+=[0]
                for l in range(0,len(nodes)):
                    meancoords[k]+=initPart.nodes[nodes[l]].coordinates[k]/len(nodes)
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




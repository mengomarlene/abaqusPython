'''
sipShell2Abq2D.py: procedure part of the 2DImage2Mesh project
Create a 2d quadrangular mesh from an image using scanIP (Simpleware Ltd) and Abaqus (Dassault Systeme)
----------------------------------------------
INSTRUCTIONS: see readme.md or 2DIm2Mesh.txt
----------------------------------------------
Author: MMENGONI, Jan 2014
----------------------------------------------
'''

## default abaqus modules
from abaqus import *
backwardCompatibility.setValues(reportDeprecated=False)
import mesh

#-----------------------------------------------------
def shellTo2DGeo(myModel,seedSize=0.5):
    from abaqusConstants import TWO_D_PLANAR,DEFORMABLE_BODY,OFF,ON,QUAD,CPS3,CPS4R,STANDARD,ENHANCED

    ## ELEMENT INTEGRATION (2D elements: CPE=plane strain, CPS=plane stress)
    elemType1 = mesh.ElemType(elemCode=CPS4R, elemLibrary=STANDARD, hourglassControl=ENHANCED)
    elemType2 = mesh.ElemType(elemCode=CPS3, elemLibrary=STANDARD)
    
    myAssembly = myModel.rootAssembly
    for myPart in myModel.parts.values():
        ## clean node list (remove nodes not in the zMin plane)
        #1/ find zMin...
        zCoord = list()
        nodeLabels = list()
        for node in myPart.nodes:
            zCoord.append(node.coordinates[2])
            nodeLabels.append(node.label)
        minZ = min(zCoord)
        #2/ build a list of nodes not in zMin
        remNodes = [nodeLabels[i] for i, x in enumerate(zCoord) if x > minZ+1e-10]
        #3/ remove those nodes
        if len(remNodes):
            myPart.SetFromNodeLabels(nodeLabels=remNodes, name='remNodeSet')
            myPart.deleteNode(nodes=myPart.sets['remNodeSet'], deleteUnreferencedNodes=ON)
            del myPart.sets['remNodeSet']
        del nodeLabels
           
    myAssembly.regenerate()#needed to still have acces to assembly node sets
        
    ## for each set that make a shell, create a new part (by getting the external edges as Lines) and mesh it
    # rebuild assembly sets as part sets and surfaces
    for setName in myAssembly.sets.keys():
            #build a list of the assembly set node coord
            nodeCoord = tuple(node.coordinates for node in myAssembly.sets[setName].nodes)
            #find the part edges at those coord
            myEdgeList = list(myAssembly.edges.findAt((nC,)) for nC in nodeCoord)
            #for what ever reason when parts.edges[0] should be in the list it is not...
            #so here is a long way to add it if needed...
            #1/ build a list of all vertices in the edge list
            #listVertices = list()
            #for edge in myEdgeList:
                #myEdgeList is a list of edge entities, the edge itself is the first element of that entity --> edge[0]
            #    listVertices.extend([v for v in edge[0].getVertices() if v not in listVertices])
            #2/ parts.edges[0] has vertices (0,1) --> if those two vertices are in the list of all vertices, add part.edges[0] to myEdgeList
            #if all(x in listVertices for x in [0,1]):
            #    pt0 = part.edges[0].getNodes()[0].coordinates
            #    pt1 = part.edges[0].getNodes()[1].coordinates
            #    newPt = ((pt0[0]+pt1[0])/2.,(pt0[1]+pt1[1])/2.,(pt0[2]+pt1[2])/2.)
            #    myEdgeList.append(part.edges.findAt((newPt,)))        
            #create surface
            myAssembly.Surface(side1Edges=myEdgeList,name=setName)
        del myAssembly.sets[setName]


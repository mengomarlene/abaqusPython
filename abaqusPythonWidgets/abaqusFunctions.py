# -*- coding: mbcs -*-
"""
Python functions for abaqus to be used within cae only
"""

#-----------------------------------------------------
def shellTo2DSolid(modelName,newInpFileName):
    from abaqus import mdb
    from abaqusConstants import TWO_D_PLANAR,DEFORMABLE_BODY,OFF
    import mesh
    import shutil
    myModel = mdb.models[modelName]
    myPart = myModel.parts['PART-1']
    ## clean node list (remove nodes not in the zMin plane)
    zCoord = list()
    nodeLabels = list()
    for node in myPart.nodes:
        zCoord.append(node.coordinates[2])
        nodeLabels.append(node.label)
    minZ = min(zCoord)
    remNodes = [nodeLabels[i] for i, x in enumerate(zCoord) if x > minZ]
    myPart.SetFromNodeLabels(nodeLabels=remNodes, name='remNodeSet')
    myPart.deleteNode(nodes=myPart.sets['remNodeSet'], deleteUnreferencedNodes=ON)
    del myPart.sets['remNodeSet']
    del nodeLabels
    # change parts from 3D shells to 2D planar
    myPart.setValues(space=TWO_D_PLANAR, type=DEFORMABLE_BODY)
    ## SECTIONS - delete shell sections
    for sName in myModel.sections.keys():
        del myModel.sections[sName]
    for sa,secAss in enumerate(myPart.sectionAssignments):
        del myPart.sectionAssignments[sa]
    myJob = mdb.Job(model=modelName, name=newInpFileName)
    myJob.writeInput(consistencyChecking=OFF)
#-----------------------------------------------------
def shellTo2DGeo(modelName,newInpFileName):
    from abaqus import mdb
    from abaqusConstants import TWO_D_PLANAR,DEFORMABLE_BODY,OFF,ON

    myModel = mdb.models[modelName]
    myAssembly = myModel.rootAssembly
    for myPart in myModel.parts.values():
        ## clean node list (remove nodes not in the zMin plane)
        zCoord = list()
        nodeLabels = list()
        for node in myPart.nodes:
            zCoord.append(node.coordinates[2])
            nodeLabels.append(node.label)
        minZ = min(zCoord)
        remNodes = [nodeLabels[i] for i, x in enumerate(zCoord) if x > minZ]
        if len(remNodes):
            myPart.SetFromNodeLabels(nodeLabels=remNodes, name='remNodeSet')
            myPart.deleteNode(nodes=myPart.sets['remNodeSet'], deleteUnreferencedNodes=ON)
            del myPart.sets['remNodeSet']
        del nodeLabels
        # change parts from 3D shells to 2D planar
        # myPart.setValues(space=TWO_D_PLANAR, type=DEFORMABLE_BODY)
        # for sa,secAss in enumerate(myPart.sectionAssignments):
        #     del myPart.sectionAssignments[sa]

    # nodeInASet = dict{}
    # for myASetName in myAssembly.sets.key():     
        # set = myAssembly.sets[myASetName]
        # nodeInASet[myASetName] = set.nodes
        
    for myInstance in myAssembly.instances.values():
        for myISet in myInstance.sets.keys():
            if myISet.endswith('WITH_ZMIN'):
                mySketch = myModel.ConstrainedSketch(name='mySketch', sheetSize=30.0)
                for ele in myInstance.sets[myISet].elements:
                    for edge in ele.getElemEdges():
                        if len(edge.getElements())==1:
                            points=list()
                            for node in edge.getNodes():
                                points.append((node.coordinates[0],node.coordinates[1]))
                            mySketch.Line(point1=tuple(points[0]),point2=tuple(points[1]))
                myNewPart = myModel.Part(name=myISet.split('_')[1]+'Geo', dimensionality=TWO_D_PLANAR, type=DEFORMABLE_BODY)
                myNewPart.BaseShell(sketch=mySketch)
                del mySketch
                abaqusTools.createInstanceAndAddtoAssembly(myNewPart,myAssembly)
                
    for setName in myAssembly.sets.keys():
        part = myModel.parts[setName.split('_')[1]+'Geo']
        labelList = list()
        pNodes = list(part.vertices)
        aSNodes = list()
        print pNodes
        for node in myAssembly.sets[setName].nodes:
            aSNodes.append(node.coordinates)
        xMin = min(x[0] for x in aSNodes)
        xMax = max(x[0] for x in aSNodes)
        yMin = min(x[1] for x in aSNodes)
        yMax = max(x[1] for x in aSNodes)

        for pNode in pNodes:
            if nodeCoord == pNode.pointOn[0]:
                pNodes.remove(pNode)
                labelList.append(pNode)
        print len(labelList)
        part.Set(vertices=labelList,name=setName)
        #del myAssembly.sets[setName]
    del myAssembly.features['PART-1-1']

    ## SECTIONS - delete shell sections
    for sName in myModel.sections.keys():
        del myModel.sections[sName]
    
    myJob = mdb.Job(model=modelName, name=newInpFileName)
    myJob.writeInput(consistencyChecking=OFF)
#-----------------------------------------------------
def createSurfaceOnNodeSet(aSetName,surfaceName,model):
    myPart = model.parts['PART-1']
    myAssembly = model.rootAssembly
    myInstance = myAssembly.instances['PART-1-1']
    myISets = myInstance.sets

    partName = aSetName.split('_')[1]
    nodeCoord = list()
    for node in myASets[aSetName].nodes:
        nodeCoord.append(node.label)
    f1List = list()
    f2List = list()
    f3List = list()
    f4List = list()
    iSet = myISets[[name for name in myISets.keys() if partName in name][0]]
    for ele in iSet.elements:
        for edge in ele.getElemEdges():
            if len([n for n in edge.getNodes() if n.label in nodeCoord])==2:
                if edge.getElemFaces()[0].face == FACE1:
                    f1List.append(ele.label)
                    break
                elif edge.getElemFaces()[0].face == FACE2:
                    f2List.append(ele.label)
                    break
                elif edge.getElemFaces()[0].face == FACE3:
                    f3List.append(ele.label)
                    break
                elif edge.getElemFaces()[0].face == FACE4:
                    f4List.append(ele.label)
                    break
    f1=myPart.elements.sequenceFromLabels(f1List)
    f2=myPart.elements.sequenceFromLabels(f2List)
    f3=myPart.elements.sequenceFromLabels(f3List)
    f4=myPart.elements.sequenceFromLabels(f4List)
    region = myPart.Surface(face1Elements=f1,face2Elements=f2,face3Elements=f3,face4Elements=f4,name=surfaceName)
    surface = myInstance.surfaces[surfaceName]
    return surface
        
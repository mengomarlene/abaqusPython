# -*- coding: mbcs -*-
"""
Python tools for abaqus
"""

#######################################################
## MODEL BUILD FUNCTIONS ##
#######################################################
def deleteDefaultModel():
    from abaqus import mdb
    defaultName = 'Model-1'
    if defaultName in mdb.models.keys():
        del mdb.models[defaultName]
#-----------------------------------------------------		
def assignMaterialToPart(materialName,part,model,orientation=None):
    from abaqusConstants import SYSTEM
    partName = part.name
    sectionName = partName.split('_')[0]+'_section'
    model.HomogeneousSolidSection(sectionName, material=materialName)
    myRegion = (part.cells,)	
    part.SectionAssignment(region=myRegion, sectionName=sectionName)
    if orientation: part.MaterialOrientation(region=myRegion,orientationType=SYSTEM,localCsys=part.datum[orientation.id])
    else: part.MaterialOrientation(region=myRegion,orientationType=SYSTEM,localCsys=None)
#-----------------------------------------------------		
def assignMaterialToPartition(materialName,part,sectionName,cells,model,orientation=None):
    from abaqusConstants import SYSTEM,MIDDLE_SURFACE
    myRegion = part.Set(cells=cells, name='Set_'+sectionName)
    model.HomogeneousSolidSection(sectionName, material=materialName)
    part.SectionAssignment(region=myRegion, sectionName=sectionName, offset=0.0, offsetType=MIDDLE_SURFACE)
    if orientation: part.MaterialOrientation(region=myRegion,orientationType=SYSTEM,localCsys=part.datum[orientation.id])
    else: part.MaterialOrientation(region=myRegion,orientationType=SYSTEM,localCsys=None)
#-----------------------------------------------------	
def createInstanceAndAddtoAssembly(part,assembly,independent=True,translate=(0,0,0)):
    from abaqusConstants import OFF,ON
    myInstaneName = part.name.split('_')[0]+'_instance'
    if independent: myInstance = assembly.Instance(myInstaneName, part, dependent=OFF)
    else: myInstance = assembly.Instance(myInstaneName, part, dependent=ON)
    if any(translate): assembly.translate(instanceList=(myInstaneName, ), vector=translate)
    return myInstance
#-----------------------------------------------------	
def assignElemtypeAndMesh(instance,assembly,elemType,control=.2,meshType='seedPartInstance',edges = list()):
    assembly.setElementType((instance.cells,), (elemType,))
    from abaqusConstants import FIXED
    if meshType == 'seedPartInstance': assembly.seedPartInstance((instance,), size=control)
    else:
        for c,edge in enumerate(edges):
            if meshType == 'seedEdgeByNumber': assembly.seedEdgeByNumber(edge, number=control[c], constraint=FIXED)
            elif meshType == 'seedEdgeBySize': assembly.seedEdgeBySize(edge, size=control[c], constraint=FIXED)
    assembly.generateMesh(regions=(instance,))
#-----------------------------------------------------
def shellTo2DSolid(modelName,newInpFileName):
    from abaqus import mdb
    from abaqusConstants import TWO_D_PLANAR,DEFORMABLE_BODY,OFF
    import mesh
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
def defineAlternateProgressiveFiberAngle(nbParts,initAngle,finalAngle):
    fiberAngle = list()
    if nbParts>2:
        dalpha = (finalAngle-initAngle)/((nbParts-1)/2)
        for lam in range(nbParts):
            if (lam%2):
                if dalpha != 0.: alpha = -initAngle-lam/2*dalpha
                else: alpha = -initAngle
            else:
                if dalpha != 0.: alpha = initAngle+lam/2*dalpha
                else: alpha = initAngle
            fiberAngle.append(alpha)
    else: raise Exception("can define alternate fiber angles only if more than 2 lamellae")
    return fiberAngle
#-----------------------------------------------------
def defineMatName(nbParts,baseName):
    matName = list()
    for lam in range(nbParts): matName.append(baseName+str(lam))
    return matName
#-----------------------------------------------------
def applyInterpolatedDisplacement2(myModel,node,x1,x2,d1,d2,BCName):
    x = node.coordinates
    a = (x[0]-x2[0])/(x1[0]-x2[0])
    b = (x[1]-x2[1])/(x1[1]-x2[1])
    d = (a*d1[0]+(1.-a)*d2[0],b*d1[1]+(1.-b)*d2[1])
    import regionToolset 
    import mesh
    nodeArray = mesh.MeshNodeArray(nodes=(node,))
    nodeRegion = regionToolset.Region(nodes=nodeArray)
    myModel.DisplacementBC(createStepName='displ', localCsys=None, name=BCName, region=nodeRegion, u1=abs(d[0])*-1.,u2=d[1])
#-----------------------------------------------------
def applyInterpolatedDisplacement(myModel,node,x1,x2,d1,d2,BCName):
    x = node.coordinates
    a = (x[0]-x2[0])/(x1[0]-x2[0])
    b = (x[1]-x2[1])/(x1[1]-x2[1])
    d = (a*d1[0]+(1.-a)*d2[0],b*d1[1]+(1.-b)*d2[1])
    import regionToolset 
    import mesh
    nodeArray = mesh.MeshNodeArray(nodes=(node,))
    nodeRegion = regionToolset.Region(nodes=nodeArray)
    myModel.DisplacementBC(createStepName='displ', localCsys=None, name=BCName, region=nodeRegion, u1=d[0],u2=d[1])   
#######################################################
## ANALYSIS FUNCTIONS ##
#######################################################
def vizuMyJob(odbName):
    from abaqus import session
    from abaqusConstants import FILLED,DEFORMED,CONTOURS_ON_DEF,SYMBOLS_ON_DEF,INTEGRATION_POINT,INVARIANT,RESULTANT,UNIFORM,ON
    # Create a new viewport in which to display the model and the results of the analysis.
    myViewport = session.Viewport(name='session viewport', origin=(0, 0), width=300, height=190)  
    # Open the output database and display a contour plot.
    import visualization
    myOdb = visualization.openOdb(path=odbName + '.odb')
    myViewport.setValues(displayedObject=myOdb)
    myViewport.graphicsOptions.setValues(backgroundStyle=GRADIENT)
    myViewport.graphicsOptions.setValues(backgroundBottomColor='#B9C9E1', backgroundOverride=OFF)
    myViewport.graphicsOptions.setValues(backgroundBottomColor='#ECECEC')
    myOdbDisplay = myViewport.odbDisplay
    myOdbDisplay.commonOptions.setValues(renderStyle=FILLED)
    myOdbDisplay.display.setValues(plotState=(DEFORMED, CONTOURS_ON_DEF, SYMBOLS_ON_DEF, ))
    myOdbDisplay.setPrimaryVariable(variableLabel='S',  outputPosition=INTEGRATION_POINT, refinement=(INVARIANT, 'Mises'), )
    if 'FibresIn'  in odbName or 'WithFiberDirection' in odbName:
        myOdbDisplay.setSymbolVariable(variableLabel='LOCALDIR1', outputPosition=INTEGRATION_POINT,  vectorQuantity=RESULTANT, )
        myOdbDisplay.symbolOptions.setValues(vectorColor='White', vectorColorMethod=UNIFORM, symbolDensity=0.9)
        myOdbDisplay.commonOptions.setValues(translucency=ON,translucencyFactor=0.45)
#-----------------------------------------------------
def vizuOnCompletion(jobName, messageType, data, userData):
    vizuMyJob(jobName)
#-----------------------------------------------------
def analysisCompleted(jobName):
    key = 'THE ANALYSIS HAS BEEN COMPLETED'
    msgFile = open(jobName+'.msg', 'r')
    lines = msgFile.readlines()
    msgFile.close()
    lines.reverse()
    for line in lines:
        if key in line:return True
    return False
#-----------------------------------------------------
def runAnalysis(job):
    #############
    # done only in GUI!!!!
    # run a function (here vizuOnCompletion) if job successfully completed
    from abaqusConstants import JOB_COMPLETED
    from abaqus import monitorManager as monitorManager
    monitorManager.addMessageCallback(job.name, JOB_COMPLETED, vizuOnCompletion, None)
    #############
    job.submit()
    job.waitForCompletion()
#-----------------------------------------------------
def writeAnalysis(job):
    from abaqusConstants import OFF
    job.writeInput(consistencyChecking=OFF)
    job.waitForCompletion()
#-----------------------------------------------------
def restartModel(model):
    from abaqus import mdb
    from abaqusConstants import PERCENTAGE
    modelName = model.name
    resModel = mdb.Model(name=modelName+'-Restart', objectToCopy=model)
    resModel.setValues(restartJob=modelName+'-Restart')
    restartJob = mdb.Job(name=modelName+'-Restart', model=modelName+'-Restart', 
        type=RESTART, memory=60, memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True)
    restartJob.submit()
    restartJob.waitForCompletion()
#-----------------------------------------------------

# -*- coding: mbcs -*-

from abaqus import *
backwardCompatibility.setValues(reportDeprecated=False)
from abaqusConstants import *
from caeModules import *    
import mesh
import abaqusPythonTools.abaqusTools as abaqusTools
import os, math

def getParameters(_p={}):
    param = {}

    fileName = 'D:/myWork/MicroscopyModels/serialMicroscopyBeth/bridgeAllHex_sipExport.inp'
    fileName.replace('/',os.sep)
    param['sipInpFile'] = fileName
    param['modelName'] = 'bridgeAllHex_Lin'
    param['parts'] = ['BRIDGES','IN_PLANE_LAM','SECTIONED_LAM']
    param['loadDirection'] = 'X'  

    param['displ'] = 0.16 # 20% s

    param['matType'] = 'Hooke'#or 'Holzapfel' or 'neoHooke'
    param['holzapfelParameters'] = (.0754, 9.09e-4, 3., 45., 0.)
    param['fiberOrientation'] = math.pi/6.

    #relevant only if Contact pairs defined in scanIP (if so the inp file exported should have the word Contact in its name)
    param['interfaceType'] = 'Tie'              #'Frictionless', 'Friction'
    param['frictionCoef'] = 0.1                 #irrelevant if param['interfaceType']!='Friction'

    param['timePeriod'] = 1.
    param['nlgeom'] = False    

    param['scratchDir'] = 'D:/Abaqus'
    param['numCpus'] = 1
    param['allowRestart'] = False

    param.update(_p)
    return param

def getEandNu(holzapfelParam):
    c10 = holzapfelParam[0]
    d = holzapfelParam[1]
    k = holzapfelParam[2]
    #elastic equivalent for the full material, initial fibre stiffness
    if d==0.: nu = 0.499
    else: nu = (6-2*(4./3.*k+2*c10)*d)/(12+4*d*c10)
    E = 8./3.*k+4*(1+nu)*c10
    return E,nu
    
def createAnalysisFromSipExport(param):
    ## IMPORT FILE
    mdb.ModelFromInputFile(inputFileName=param['sipInpFile'], name=param['modelName'])
    abaqusTools.deleteDefaultModel()
    ## SHORTCUTS
    myModel = mdb.models[param['modelName']]
    myPart = myModel.parts['PART-1']
    myAssembly = myModel.rootAssembly
    myInstance = myAssembly.instances['PART-1-1']
    mySets =  myAssembly.sets

    ## STEP CREATION
    nlGeom = OFF
    if param['nlgeom']:
        nlGeom = ON
    if param['matType'] == 'Hooke':
        initInc = .05
        maxInc = .15
    else:
        initInc = .01
        maxInc = .1
    if 'Contact' in param['sipInpFile']:
        initInc = 1e-4
        maxInc = .1    

    minInc = min(initInc,maxInc)/1000.
    myModel.StaticStep(initialInc=initInc ,timePeriod=param['timePeriod'], maxInc=maxInc, minInc=minInc, name='displ', nlgeom=nlGeom, previous='Initial',maxNumInc=10000)
    ## ELEMENT INTEGRATION (to ensure hourglass control and hybrid integration - may not be needed!!)
    elemType1 = mesh.ElemType(elemCode=C3D8RH, elemLibrary=STANDARD, hourglassControl=ENHANCED)
    elemType2 = mesh.ElemType(elemCode=C3D4, elemLibrary=STANDARD)
    myPart.setElementType(regions=(myPart.elements,), elemTypes=(elemType1, elemType2))
    
    directions = list()
    matNames = list()
    for i,p in enumerate(param['parts']):
        ## MATERIALS
        mat = 'PM_'+p
        allMats = myModel.materials
        if allMats.has_key(mat):
            myMat = myModel.materials[mat]
        else:continue
        E,nu = getEandNu(param['holzapfelParameters'])
        if 'BRIDGES' in mat:
            if param['nlgeom']:
                myMat.Hyperelastic(testData=OFF,table=((6*(1-2.*0.45)/0.4,0.4/(4*(1.+0.45))),),materialType=ISOTROPIC,type=NEO_HOOKE,behaviorType=COMPRESSIBLE)
            else: myMat.Elastic(table=((0.4, 0.45), ))
        elif param['matType'] == 'Hooke':
            myMat.Elastic(table=((E, nu), ))
        elif param['matType'] == 'neoHooke':
            if param['holzapfelParameters'][1]==0.:# incompressible
                myMat.Hyperelastic(testData=OFF,table=((E/(4*(1.+nu)),6*(1-2.*nu)/E),),materialType=ISOTROPIC,type=NEO_HOOKE
                ,behaviorType=INCOMPRESSIBLE)
            else:
                myMat.Hyperelastic(testData=OFF,table=((E/(4*(1.+nu)),6*(1-2.*nu)/E),),materialType=ISOTROPIC,type=NEO_HOOKE
                ,behaviorType=COMPRESSIBLE)
        elif param['matType'] == 'Holzapfel':
            if param['holzapfelParameters'][1]==0.:# incompressible
                myMat.Hyperelastic(table=(param['holzapfelParameters'],),materialType=ANISOTROPIC,anisotropicType=HOLZAPFEL
                ,behaviorType=INCOMPRESSIBLE,localDirections=1)
            else:
                myMat.Hyperelastic(table=(param['holzapfelParameters'],),materialType=ANISOTROPIC,anisotropicType=HOLZAPFEL
                ,behaviorType=COMPRESSIBLE,localDirections=1)
            if 'SECTIONED' in mat:
                fibreAngle = 2.*param['fiberOrientation']
            else:
                fibreAngle = 0.
            region = myPart.sets['PT_'+p]
            myPart.MaterialOrientation(region=region, orientationType=SYSTEM, localCsys=None)
            directions.append((0.,math.sin(fibreAngle),math.cos(fibreAngle)))
            matNames.append(mat)
        ##BC'S
        dMin = 'NS_%s_WITH_%sMIN'%(p,param['loadDirection'])
        if  mySets.has_key(dMin):
            myModel.PinnedBC(createStepName='displ', localCsys=None, name='fix_%d'%(i), region=mySets[dMin])
        dMax = 'NS_%s_WITH_%sMAX'%(p,param['loadDirection'])
        if  mySets.has_key(dMax):
            if param['loadDirection'] == 'X':
                myModel.DisplacementBC(createStepName='displ', localCsys=None, name='mov_%d'%(i), region=mySets[dMax], u1=param['displ'])
            elif param['loadDirection'] == 'Y':
                myModel.DisplacementBC(createStepName='displ', localCsys=None, name='mov_%d'%(i), region=mySets[dMax], u2=param['displ'])
            elif param['loadDirection'] == 'Z':
                myModel.DisplacementBC(createStepName='displ', localCsys=None, name='mov_%d'%(i), region=mySets[dMax], u3=param['displ'])
        
        ##CONSTRAINTS - same for all interfaces - could be changed depending on the interface name!!
        if 'Contact' in param['sipInpFile']:
            for interactionName in myModel.interactionProperties.keys():
                from abaqusPythonTools.interactions import Interactions
                inter = Interactions(myModel)
                inter.setName(interactionName)
                if param['interfaceType'] == 'Tie':
                    masterRegion = myModel.interactions[interactionName+'-1'].master[0]
                    slaveRegion = myModel.interactions[interactionName+'-1'].slave[0]
                    del myModel.interactions[interactionName+'-1']
                    del myModel.interactionProperties[interactionName]
                    inter.setMasterSlave(masterRegion,slaveRegion)
                    inter.setInteractionToTie()
                elif param['interfaceType'] == 'Friction':
                    inter.setFrictionBehaviour('Friction')
                elif param['interfaceType'] == 'Cohesive':
                    inter.setCohesiveBehaviour()
                inter.changeInteraction()                        
    ## OUTPUT REQUESTS
    fieldVariable = ('S', 'LE', 'U', 'RT', 'P', 'CSTRESS', 'CDISP', 'CFORCE')
    myModel.fieldOutputRequests['F-Output-1'].setValues(variables=fieldVariable)
    ## RESTART DEF
    if param['allowRestart']:
        myModel.steps['displ'].Restart(numberIntervals=5,timeMarks=OFF,overlay=ON)
    ## JOB
    from abaqusPythonTools.jobCreation import JobDefinition
    myJobDef = JobDefinition(param['modelName'])
    myJobDef.setScratchDir(param['scratchDir'])
    if param['matType'] == 'Holzapfel':
        myJobDef.setToFibrous()        
        myJobDef.fibreDirections(directions)
        myJobDef.setFibreInputType('fromSip')
        myJobDef.setMatNames(matNames)
    myNewJob = myJobDef.create()
    if param['numCpus']>1: 
        myNewJob.setValues(numCpus=param['numCpus'],numDomains=param['numCpus'],multiprocessingMode=DEFAULT)
    mdb.saveAs(param['modelName'])
    ##
    return myNewJob,mdb

# -*- coding: mbcs -*-

from abaqus import *
backwardCompatibility.setValues(reportDeprecated=False)
from abaqusConstants import *
from caeModules import *    
import mesh
import abaqusTools
import os, math

def getParameters(_p={}):
    param = {}

    name = 'soob0'
    fileName = 'D:/myWork/scanIpScripts/workspace/sphereOutOfBoxSip5_Tie_%s/%s_ExportInp.inp'%(name,name)
    fileName.replace('/',os.sep)
    param['sipInpFile'] = fileName
    param['modelName'] = name
    param['parts'] = ['BOX','SPHERE']
    param['loadDirection'] = 'X'
    
    param['nlgeom'] = False
    param['timePeriod'] = 1.
    param['displ'] = 0.16 # 20% s
    param['matType'] = 'Hooke'#or 'neoHooke'
    param['matParameters'] = (100.,.3)#E,nu sphere (E_box = 0.1E_sphere) - if nu=0.5 and Hooke: nu:= 0.499, if nu=0.5 and neoHooke --> incompressible hyperelasticity

    #relevant only if Contact pairs defined in scanIP (if so the inp file exported should have the word Contact in its name)
    param['interfaceType'] = 'Tie'              #'Frictionless', 'Friction'
    param['frictionCoef'] = 0.1                 #irrelevant if param['interfaceType']!='Friction'
    
    param['scratchDir'] = 'D:\Abaqus'
    param['numCpus'] = 1
    param.update(_p)
    return param

def createAnalysisFromSipExport(param):
    ## IMPORT FILE
    mdb.ModelFromInputFile(inputFileName=param['sipInpFile'], name=param['modelName'])
    abaqusTools.deleteDefaultModel()

    ## SHORTCUTS
    myModel = mdb.models[param['modelName']]
    myPart = myModel.parts['PART-1']
    myInstance = myModel.rootAssembly.instances['PART-1-1']
    mySets =  myModel.rootAssembly.sets

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
    myModel.StaticStep(initialInc=initInc ,timePeriod=param['timePeriod'], maxInc=maxInc, minInc=minInc, name='displ', nlgeom=nlGeom, previous='Initial')

    ## ELEMENT INTEGRATION (to ensure hourglass control - may not be needed!!)
    elemType1 = mesh.ElemType(elemCode=C3D8R, elemLibrary=STANDARD, hourglassControl=ENHANCED)
    elemType2 = mesh.ElemType(elemCode=C3D4, elemLibrary=STANDARD)
    myPart.setElementType(regions=(myPart.elements,), elemTypes=(elemType1, elemType2))
    
    for i,p in enumerate(param['parts']):
        ## MATERIALS
        mat = 'PM_'+p
        myMat = myModel.materials[mat]
        if param['matType'] == 'Hooke':
            if param['matParameters'][1] == 0.5:
                matParam = (param['matParameters'][0],0.499)
            else:
                matParam = param['matParameters']
            if 'BOX' in mat:
                myMat.Elastic(table=((matParam[0]/10., matParam[1]), ))
            else:
                myMat.Elastic(table=(matParam, ))
        elif param['matType'] == 'neoHooke':
            c10 = param['matParameters'][0]/(2*(1+param['matParameters'][1]))
            D = (6*(1-2*param['matParameters'][1]))/param['matParameters'][0]
            if 'BOX' in mat:
                matParam = (c10/10.,D*10)
            else:
                matParam = (c10,D)
            if D==0.:# incompressible
                myMat.Hyperelastic(table=(matParam,),materialType=ISOTROPIC,anisotropicType=NEO_HOOKE
                ,behaviorType=INCOMPRESSIBLE)
            else:
                myMat.Hyperelastic(table=(matParam,),materialType=ISOTROPIC,anisotropicType=NEO_HOOKE
                ,behaviorType=COMPRESSIBLE)                
        
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
                from interactions import Interactions
                inter = Interactions(myModel)
                inter.setName(interactionName)
                if param['interfaceType'] == 'Friction':
                    inter.setFrictionBehaviour('Friction')
                inter.changeInteraction()
                    
    ## OUTPUT REQUESTS
    fieldVariable = ('S', 'LE', 'U', 'RT', 'P', 'CSTRESS', 'CDISP', 'CFORCE')
    myModel.fieldOutputRequests['F-Output-1'].setValues(variables=fieldVariable)

    ##JOB
    from jobCreation import JobDefinition
    myJobDef = JobDefinition(param['modelName'])
    myJobDef.setScratchDir(param['scratchDir'])
    myJob = myJobDef.create()
    if param['numCpus']>1: 
        myJob.setValues(numCpus=param['numCpus'],numDomains=param['numCpus'],multiprocessingMode=DEFAULT)
    mdb.saveAs(myJob.name)
    #-----------------------------------------------------------
    return myJob,mdb

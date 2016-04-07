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

    fileName = 'D:/myWork/MRIModels/BL15-S3/smoothDisc/homogeneousTZHemiDisc.inp'#height~5.5 - model with external annulus surface defined + material orientation
    fileName.replace('/',os.sep)
    param['inpFile'] = fileName
    param['parts'] = ['TRANSITIONZONE','ANNULUS','NUCLEUS','BOTTOMENDPLATE','TOPENDPLATE']

    param['displ'] = -0.25 # ~10% ;negative for compression

    param['matType'] = 'neoHooke'# 'Holzapfel' or 'neoHooke'
    param['holzapfelParameters'] = (.022, 9.09e-4, 6.86, 219.94, 0.)#ovine data - c10,D made up...
    param['fiberOrientation'] = math.pi/6.

    #relevant only if Contact pairs defined in scanIP (if so the inp file exported should have the word Contact in its name)
    param['interfaceType'] = 'Frictionless'     #'Frictionless', 'Friction'
    param['frictionCoef'] = 0.1                 #irrelevant if param['interfaceType']!='Friction'

    param['timePeriod'] = 1.
    param['nlgeom'] = True    

    param['scratchDir'] = 'D:\Abaqus'
    param['numCpus'] = 1

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

def createAnalysis(param):
    nbLamellae = len(param['parts'])-4
    ## IMPORT FILE
    mdb.ModelFromInputFile(inputFileName=param['inpFile'], name=param['modelName'])
    abaqusTools.deleteDefaultModel()
    ## SHORTCUTS
    myModel = mdb.models[param['modelName']]
    myPart = myModel.parts['PART-1']
    myAssembly = myModel.rootAssembly
    myInstance = myAssembly.instances['PART-1-1']
    mySets =  myAssembly.sets

    ## STEP CREATION
    nlGeom = OFF
    if param['nlgeom']: nlGeom = ON

    initInc = .01
    maxInc = .1
    if 'homogeneous' not in param['inpFile']:
        initInc = 1e-4
        maxInc = .1
        if ('Bonded' not in param['inpFile']) and ('bonded' not in param['inpFile']): initInc = 1e-6
    minInc = initInc/10000.
    myModel.StaticStep(initialInc=initInc ,timePeriod=param['timePeriod'], maxInc=maxInc, minInc=minInc, name='displ', nlgeom=nlGeom, previous='Initial',maxNumInc=10000)
    if 'homogeneous' not in param['inpFile'] and 'Bonded' not in param['inpFile']:
        myModel.steps['displ'].control.setValues(allowPropagation=OFF, resetDefaultValues=OFF, discontinuous=ON)
    ## ELEMENT INTEGRATION (to ensure hourglass control - may not be needed!!)
    elemType1 = mesh.ElemType(elemCode=C3D8R, elemLibrary=STANDARD, hourglassControl=ENHANCED)
    elemType2 = mesh.ElemType(elemCode=C3D4, elemLibrary=STANDARD)
    myPart.setElementType(regions=(myPart.elements,), elemTypes=(elemType1, elemType2))
    
    directions = list()
    matNames = list()
    for i,p in enumerate(param['parts']):
        ## MATERIALS
        mat = 'PM_'+p
        allMats = myModel.materials
        if allMats.has_key(mat): myMat = myModel.materials[mat]
        else:continue
        E,nu = getEandNu(param['holzapfelParameters'])
        if 'PLATE' in mat:
            if param['nlgeom']: myMat.Hyperelastic(testData=OFF,table=((300./1.3,2.4/1200.),),materialType=ISOTROPIC,type=NEO_HOOKE,behaviorType=COMPRESSIBLE)
            else: myMat.Elastic(table=((1200., 0.3), ))
        elif 'NUCLEUS' in mat:
            if param['nlgeom']:
                myMat.Hyperelastic(testData=OFF,table=((0.00025,0.0),),materialType=ISOTROPIC,type=NEO_HOOKE,behaviorType=INCOMPRESSIBLE)
                elemType1 = mesh.ElemType(elemCode=C3D8RH, elemLibrary=STANDARD, hourglassControl=ENHANCED)
                elemType2 = mesh.ElemType(elemCode=C3D4H, elemLibrary=STANDARD)
                region = myPart.sets['PT_'+p]
                myPart.setElementType(regions=region, elemTypes=(elemType1, elemType2))
            else: myMat.Elastic(table=((.0015, 0.499), ))
        elif not param['nlgeom']: myMat.Elastic(table=((E, nu), ))
        elif param['matType'] == 'neoHooke' or 'TRANSITIONZONE' in mat:
            matParam = (E/(4*(1.+nu)),6*(1-2.*nu)/E)
            if param['holzapfelParameters'][1]==0.:# incompressible
                myMat.Hyperelastic(testData=OFF,table=(matParam,),materialType=ISOTROPIC,type=NEO_HOOKE
                ,behaviorType=INCOMPRESSIBLE)
                elemType1 = mesh.ElemType(elemCode=C3D8RH, elemLibrary=STANDARD, hourglassControl=ENHANCED)
                elemType2 = mesh.ElemType(elemCode=C3D4H, elemLibrary=STANDARD)
                region = myPart.sets['PT_'+p]
                myPart.setElementType(regions=region, elemTypes=(elemType1, elemType2))
            else: myMat.Hyperelastic(testData=OFF,table=(matParam,),materialType=ISOTROPIC,type=NEO_HOOKE,behaviorType=COMPRESSIBLE)
        elif param['matType'] == 'Holzapfel':
            matParam = param['holzapfelParameters']
            if 'homogeneous' not in param['inpFile']: nbDirection=1
            else: nbDirection=2
                        
            if matParam[1]==0.:# incompressible
                myMat.Hyperelastic(table=(matParam,),materialType=ANISOTROPIC,anisotropicType=HOLZAPFEL
                ,behaviorType=INCOMPRESSIBLE,localDirections=nbDirection)
                elemType1 = mesh.ElemType(elemCode=C3D8RH, elemLibrary=STANDARD, hourglassControl=ENHANCED)
                elemType2 = mesh.ElemType(elemCode=C3D4H, elemLibrary=STANDARD)
                region = myPart.sets['PT_'+p]
                myPart.setElementType(regions=region, elemTypes=(elemType1, elemType2))
            else: myMat.Hyperelastic(table=(matParam,),materialType=ANISOTROPIC,anisotropicType=HOLZAPFEL,behaviorType=COMPRESSIBLE,localDirections=nbDirection)
            
            if isinstance(param['fiberOrientation'],tuple) and len(param['fiberOrientation']) == nbLamellae:
                lamellarNo = int(''.join(x for x in mat if x.isdigit()))
                fibreAngle = param['fiberOrientation'][lamellarNo-1]
            elif isinstance(param['fiberOrientation'],float): fibreAngle = param['fiberOrientation']
            else: raise("parameter 'fiberOrientation' of wrong type or length")
            directions.append((math.sin(fibreAngle),math.cos(fibreAngle),0.))
            matNames.append(mat)

        ##BC'S
        if 'Hemi' in param['inpFile']:
            #symmetry at yMin
            yMax = 'NS_%s_WITH_YMIN'%p
            if  mySets.has_key(yMax): myModel.YsymmBC(createStepName='displ', name='ySymm_%s'%(p), region=mySets[yMax])
            #fixation
            dMin = 'NS_%s_WITH_ZMIN'%p
            if  mySets.has_key(dMin): myModel.PinnedBC(createStepName='displ', localCsys=None, name='fix_%d'%(i), region=mySets[dMin])
            #displacement
            dMax = 'NS_%s_WITH_ZMAX'%p
            if  mySets.has_key(dMax): myModel.DisplacementBC(createStepName='displ', localCsys=None, name='mov_%d'%(i), region=mySets[dMax], u3=param['displ'],u1=0.,u2=0.)
        else:
            #fixation
            dMin = 'NS_BOTTOMPLATE_WITH_BACKGROUND'
            if mySets.has_key(dMin): myModel.PinnedBC(createStepName='displ', localCsys=None, name='fix_%d'%(i), region=mySets[dMin])
            #displacement
            dMax = 'NS_TOPPLATE_WITH_BACKGROUND'
            if mySets.has_key(dMax): myModel.DisplacementBC(createStepName='displ', localCsys=None, name='mov_%d'%(i), region=mySets[dMax], u1=param['displ'],u2=0.,u3=0.)
        
        ##CONSTRAINTS - same for all interfaces - could be changed depending on the interface name!!
        if 'homogeneous' not in param['inpFile'] and 'Bonded' not in param['inpFile'] and 'bonded' not in param['inpFile'] :
            for interactionName in myModel.interactionProperties.keys():
                from abaqusPythonTools.interactions import Interactions
                inter = Interactions(myModel)
                inter.setName(interactionName)
                if param['interfaceType'] == 'Friction':
                    inter.setFrictionBehaviour('Friction',param['frictionCoef'])
                    inter.setSeparationAllowed()
                elif param['interfaceType'] == 'Rough':
                    inter.setFrictionBehaviour('Rough')
                elif param['interfaceType'] == 'Cohesive':
                    inter.setCohesiveBehaviour(useDefaultBehaviour=False,penalties=(100.0, 100.0, 100.0))
                elif param['interfaceType'] == 'CohesiveRough':
                    inter.setCohesiveBehaviour(useDefaultBehaviour=False)
                    inter.setFrictionBehaviour('Rough')
                elif param['interfaceType'] == 'CohesiveFriction':
                    inter.setCohesiveBehaviour(useDefaultBehaviour=False)
                    inter.setFrictionBehaviour('Friction',param['frictionCoef'])
                inter.changeInteraction()                        
    ## OUTPUT REQUESTS
    # fieldVariable = ('S', 'LE', 'U', 'RT', 'P', 'CSTRESS', 'CDISP', 'CFORCE')
    # myModel.fieldOutputRequests['F-Output-1'].setValues(variables=fieldVariable)

    ## JOB
    from abaqusPythonTools.jobCreation import JobDefinition
    myJobDef = JobDefinition(param['modelName'])
    myJobDef.setScratchDir(param['scratchDir'])
    if param['matType'] == 'Holzapfel':
        myJobDef.setToFibrous()        
        myJobDef.fibreDirections(directions)
        if 'homogeneous' in param['inpFile']: myJobDef.setFibreInputType('twoDirectionsZVert')
        myJobDef.setMatNames(matNames)
    myNewJob = myJobDef.create()
    if param['numCpus']>1: myNewJob.setValues(numCpus=param['numCpus'],numDomains=param['numCpus'],multiprocessingMode=DEFAULT)
    mdb.saveAs(param['modelName'])
    ##
    return myNewJob,mdb

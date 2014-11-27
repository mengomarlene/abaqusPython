# -*- coding: mbcs -*-

from abaqus import *
backwardCompatibility.setValues(reportDeprecated=False)
from abaqusConstants import *
from caeModules import *    
import mesh
import abaqusTools
from sipShell2Abq2D import shellTo2DGeo
import os, math

def getParameters(_p={}):
    param = {}

    fileName = 'D:/myWork/MicroscopyModels/2DTensileTests/tt01_01_noBScSegDS.inp'
    fileName.replace('/',os.sep)
    #either give a sip file with shell deifinition (in param['sipInpFile']) - or give a 2D inp file (in param['inpFile'])
    param['sipInpFile'] = fileName
    param['inpFile'] = None
    param['modelName'] = 'tt01_01_nobridges'
    param['parts'] = ['INPLANE','SECTIONED']

    param['load'] = 'tension'#'tension' or 'shear' (compression is a negative displ and 'tension')
    param['displ'] = 0.085 # ~5% stretch

    param['matType'] = 'Hooke'#or 'Holzapfel' or 'neoHooke'
    param['holzapfelParameters'] = (.02, 0.001, 23.9167, 1044.7, 0.)#OVINE anterior 24.8084  977.3121
    
    param['fiberOrientation'] = math.pi/6. #(direction = vertical for inPlane lamellae, 2theta from the vertical for sectionned ones)

    param['interfaceType'] = 'Tie'         #'Rough', 'Friction', 'CohesiveRough', 'Cohesive', 'CohesiveFriction'  
    param['frictionCoef'] = 0.1           #irrelevant if param['interfaceType']!='Friction' or  'CohesiveFriction'
    param['cohesivePenalties'] = (.1,.1,.1)
    param['normalStiffness'] = 1.

    param['timePeriod'] = 1.
    param['nlgeom'] = False
    
    param['scratchDir'] = 'D:\Abaqus'
    param['numCpus'] = 1

    param.update(_p)
    return param
    
def createAnalysis(param):
    if param['matType'] != 'Hooke' and not param['nlgeom']:
        print 'non linear geometry enforced with hyperelastic materials'
        param['nlgeom'] = True
    ## IMPORT FILE
    if param['sipInpFile']:
        myModel = mdb.ModelFromInputFile(inputFileName=param['sipInpFile'], name=param['modelName'])
        shellTo2DGeo(myModel)
    else:
        myModel = mdb.ModelFromInputFile(inputFileName=param['inpFile'], name=param['modelName'])
    abaqusTools.deleteDefaultModel()
    ## SHORTCUTS
    myAssembly = myModel.rootAssembly
    allMats = myModel.materials
    ## STEP CREATION
    nlGeom = OFF
    if param['nlgeom']: nlGeom = ON
    t0 = 0.01
    if (param['interfaceType'] is not 'Tie') and (param['interfaceType'] is not 'Rough'):t0 = 1e-5
    myModel.StaticStep(initialInc=t0 ,timePeriod=param['timePeriod'], maxInc=.1, minInc=1e-9, name='displ', nlgeom=nlGeom, previous='Initial')
    
    directions = list()
    matNames = list()
    slMaCouples = list()
    for i,myPart in enumerate(myModel.parts.values()):
        myPSet = myPart.sets
        part = myPart.name.split('_')[0]
        if part == 'INPLANE6' and param['load'] == 'custom':
            del myModel.parts['INPLANE6_Geo']
            del myAssembly.features['INPLANE6_instance']
            continue
        partType = [p for p in param['parts'] if p in part][0]#find if it is a sectionned or in plane lamellae
        ## MATERIALS
        cSys = myPart.DatumCsysByThreePoints(coordSysType=CARTESIAN,origin=(0.,0.,0.),point1=(1.,0.,0.),point2=(0.,1.,0.))       
        mat = 'SM_'+part
        if allMats.has_key(mat):
            myMat = myModel.materials[mat]
        else:
            print 'material %s unknown!!!'%mat
            continue
        E = 0.06#equivalent GM only as we are perp to fibers!!
        nu = 0.499
        if partType == 'BRIDGES':
            myMat.Elastic(table=((0.4, 0.45), ))
        elif param['matType'] == 'Hooke':
            myMat.Elastic(table=((E, nu), ))
        elif param['matType'] == 'neoHooke':
            matParam = (E/(4*(1.+nu)),6*(1-2.*nu)/E)
            if matParam[1]==0.:# incompressible
                myMat.Hyperelastic(testData=OFF,table=(matParam,),materialType=ISOTROPIC,type=NEO_HOOKE
                ,behaviorType=INCOMPRESSIBLE)
            else:
                myMat.Hyperelastic(testData=OFF,table=(matParam,),materialType=ISOTROPIC,type=NEO_HOOKE
                ,behaviorType=COMPRESSIBLE)
        elif param['matType'] == 'Holzapfel':
            if partType == 'SECTIONED':
                #issue: shell/2D do not allow for mat properties out-of-plane --> fibres cannot be out-of-plane
                #--> the effect of the angle is incorporated into the mat properties, k1 only, that are reduced according to the cos of the angle
                fibreAngle = 2.*param['fiberOrientation']
                matParam = (param['holzapfelParameters'][0],param['holzapfelParameters'][1],param['holzapfelParameters'][2]*math.cos(fibreAngle),param['holzapfelParameters'][3],param['holzapfelParameters'][4])
            else:
                matParam = param['holzapfelParameters']
            if matParam[1]==0.:# incompressible
                myMat.Hyperelastic(table=(matParam,),materialType=ANISOTROPIC,anisotropicType=HOLZAPFEL
                ,behaviorType=INCOMPRESSIBLE,localDirections=1)
            else:
                myMat.Hyperelastic(table=(matParam,),materialType=ANISOTROPIC,anisotropicType=HOLZAPFEL
                ,behaviorType=COMPRESSIBLE,localDirections=1)
            myPart.MaterialOrientation(region=(myPart.faces[0],), orientationType=SYSTEM, axis=AXIS_3, localCsys=myPart.datums[cSys.id])#AXIS_3 is the normal to the shell
            directions.append((0.,1.,0.))
            matNames.append(mat)
        ## SECTION
        myModel.HomogeneousSolidSection(name='Section_%s'%part, material=mat, thickness=None)
        myPart.SectionAssignment(region=(myPart.faces[0],), sectionName='Section_%s'%part)
        ## BC'S
        
        myISet = myAssembly.instances['%s_instance'%part].sets
        dMin = 'NS_%s_WITH_XMIN'%part
        dMax = 'NS_%s_WITH_XMAX'%part

        if param['load'] == 'custom':
            if 'tt01_01_noBScSegDS' in param['sipInpFile']:
                if  myISet.has_key(dMin):
                    myModel.PinnedBC(createStepName='displ', localCsys=None, name='fix_%d'%(i), region=myISet[dMin])
                if part == 'INPLANE5':
                    x1 = (1.10898,1.29364)
                    x2 = (1.29274,0.74189)
                    d1 = (0.134,-0.12)
                    d2 = (0.18,-0.10)
                    for node in myISet['SF_%s_WITH_SECTIONNED6'%part].nodes:
                        i += 1
                        abaqusTools.applyInterpolatedDisplacement(myModel,node,x1,x2,d1,d2,'mov_%d'%(i))
            elif 'tt02_02_CroppedNoBScSegDS' in param['sipInpFile']:
                if  myISet.has_key(dMax):
                    myModel.PinnedBC(createStepName='displ', localCsys=None, name='fix_%d'%(i), region=myISet[dMax])
                if part == 'SECTIONED2':
                    x1 = (0.261,1.943)
                    x2 = (0.297,0)
                    d1 = (-0.23617,0.09717)
                    d2 = (-0.390945,-0.02034)
                    for node in myISet['SF_%s_WITH_INPLANE1'%part].nodes:
                        i += 1
                        abaqusTools.applyInterpolatedDisplacement2(myModel,node,x1,x2,d1,d2,'mov_%d'%(i))
        else:
            if  myISet.has_key(dMin):
                myModel.PinnedBC(createStepName='displ', localCsys=None, name='fix_%d'%(i), region=myISet[dMin])
            if  myISet.has_key(dMax):
                if param['load'] == 'tension':
                    myModel.DisplacementBC(createStepName='displ', localCsys=None, name='mov_%d'%(i), region=myISet[dMax], u1=param['displ'])
                elif param['load'] == 'shear':
                    myModel.DisplacementBC(createStepName='displ', localCsys=None, name='mov_%d'%(i), region=myISet[dMax], u2=param['displ'])
                else:raise Exception('unknonw load type')
        ## Get Master/Slave couples
        oParts = list(myModel.parts.keys())
        oParts.remove(myPart.name)
        for setName in myPSet.keys():
            if setName.startswith('SF_%s_WITH_'%part):
                for oPart in oParts:
                    oPartName = oPart.split('_')[0]
                    if oPartName=='INPLANE6':
                        continue
                    elif oPartName in setName:
                        if [oPartName,part] not in slMaCouples:
                            slMaCouples.append([part,oPartName])
    ## CONSTRAINTS - same for all interfaces!!
    for nbInteraction,slMaCouple in enumerate(slMaCouples):
        masterName = 'SF_%s_WITH_%s'%(slMaCouple[1],slMaCouple[0])
        slaveName = 'SF_%s_WITH_%s'%(slMaCouple[0],slMaCouple[1])
        myMaInstance = myAssembly.instances['%s_instance'%slMaCouple[1]]
        mySlInstance = myAssembly.instances['%s_instance'%slMaCouple[0]]
        from interactions import Interactions
        inter = Interactions(myModel)
        inter.setName('interaction_%i'%nbInteraction)
        if param['interfaceType'] == 'Tie':
            inter.setMasterSlave(myMaInstance.sets[masterName],mySlInstance.sets[slaveName])
            inter.setInteractionToTie()
        else:
            inter.setMasterSlave(myMaInstance.surfaces[masterName],mySlInstance.surfaces[slaveName])
            inter.setNormalStiffness(param['normalStiffness'])
            if param['interfaceType'] == 'Friction':
                inter.setFrictionBehaviour('Friction')
            elif param['interfaceType'] == 'Rough':
                inter.setFrictionBehaviour('Rough')
            elif param['interfaceType'] == 'Cohesive':
                inter.setCohesiveBehaviour(useDefaultBehaviour=False,penalties=param['cohesivePenalties'])
            elif param['interfaceType'] == 'CohesiveRough':
                inter.setCohesiveBehaviour(useDefaultBehaviour=False,penalties=param['cohesivePenalties'])
                inter.setFrictionBehaviour('Rough')
            elif param['interfaceType'] == 'CohesiveFriction':
                inter.setCohesiveBehaviour()
                inter.setFrictionBehaviour('Friction')
        inter.createInteraction()

    ## OUTPUT REQUESTS
    #fieldVariable = ('S', 'LE', 'U', 'RF', 'P', 'CSTRESS', 'CDISP', 'CFORCE')
    #myModel.fieldOutputRequests['F-Output-1'].setValues(variables=fieldVariable)
    ## JOB
    from jobCreation import JobDefinition
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
    return myNewJob,mdb
    
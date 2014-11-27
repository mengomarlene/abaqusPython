from abaqus import *
backwardCompatibility.setValues(reportDeprecated=False)
from abaqusConstants import *
from caeModules import *    
import os, math
import abaqusTools

param = {}

fileName = 'D:/myWork/MicroscopyModels/serialMicroscopyBeth/BL04/bridgeSmooth_sipExport.inp'
fileName.replace('/',os.sep)
param['sipInpFile'] = fileName
param['modelName'] = 'bridgeAllHex_Lin'
param['scaleFactor'] = .6
param['matName'] = ['PM_BRIDGES','PM_IN_PLANE_LAM','PM_SECTIONED_LAM']
param['matType'] = 'Hooke'
param['holzapfelParameters'] = (.0754, 9.09e-4, 3., 45., 0.)
param['fiberOrientation'] = math.pi/6.

myModel = mdb.ModelFromInputFile(inputFileName=param['sipInpFile'], name=param['modelName'])
abaqusTools.deleteDefaultModel()
myPart = myModel.parts['PART-1']
myAssembly = myModel.rootAssembly
myInstance = myAssembly.instances['PART-1-1']
mySets =  myAssembly.sets

allMats = myModel.materials
if len(param['matName'])>1:
    matList = param['matName']
else: matList = allMats
for i,p in enumerate(matList):
    ## MATERIAL NAME
    if len(param['matName'])>1:
        if allMats.has_key(p):
            myMat = allMats[p]
        else:continue
    else: myMat = p
    try:
        E = myMat.elastic.table[0][0]*param['scaleFactor']
        nu = myMat.elastic.table[0][1]
        del myMat.elastic#delete existing material def
    except (AttributeError):
        E = 8.8627
        nu = 0.4993
    if param['matType'] == 'Hooke':
        myMat.Elastic(table=((E, nu), ))
    elif param['matType'] == 'neoHooke':
        matParam = (E/(4*(1.+nu)),6*(1-2.*nu)/E)
        ###matParam = (5.9693+param['holzapfelParameters'][0],param['holzapfelParameters'][1])
        if matParam[1]==0.:# incompressible
            myMat.Hyperelastic(testData=OFF,table=(matParam,),materialType=ISOTROPIC,type=NEO_HOOKE
            ,behaviorType=INCOMPRESSIBLE)
        else:
            myMat.Hyperelastic(testData=OFF,table=(matParam,),materialType=ISOTROPIC,type=NEO_HOOKE
            ,behaviorType=COMPRESSIBLE)
    elif param['matType'] == 'Holzapfel':
        matParam = param['holzapfelParameters']
        if matParam[1]==0.:# incompressible
            myMat.Hyperelastic(table=(matParam,),materialType=ANISOTROPIC,anisotropicType=HOLZAPFEL
            ,behaviorType=INCOMPRESSIBLE,localDirections=1)
        else:
            myMat.Hyperelastic(table=(matParam,),materialType=ANISOTROPIC,anisotropicType=HOLZAPFEL
            ,behaviorType=COMPRESSIBLE,localDirections=1)
        if 'SECTIONED' in myMat.name:
            fibreAngle = 2.*param['fiberOrientation']
        else:
            fibreAngle = 0.
        region = myPart.sets['PT_'+myMat.name]
        myPart.MaterialOrientation(region=region, orientationType=SYSTEM, localCsys=None)
        directions.append((0.,math.sin(fibreAngle),math.cos(fibreAngle)))
        matNames.append(mat)

myJob = mdb.Job(model=param['modelName'], name=param['modelName'])
myJob.writeInput(consistencyChecking=OFF)
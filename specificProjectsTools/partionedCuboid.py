# -*- coding: mbcs -*-
from abaqus import *
backwardCompatibility.setValues(reportDeprecated=False)
from abaqusConstants import *
import mesh,regionToolset
import math
import abaqusPythonTools.abaqusTools as abaqusTools
from abaqusPythonTools.jobCreation import JobDefinition as JobDefinition
#from caeModules import *
#-----------------------------------------------------  
def getParameters(_p={}):
    param = {}
    param['l1'] = 50.
    param['l2'] = 30.
    param['h'] = 20.
    param['displ'] = 2.
    param['seedSize'] = .6
    param['BCType'] = 'Tension'#Tension,Compression,ParrTension,ParrCompression
    param['nbParts'] = 4
    param['modelName'] = 'partitionedCube'
    param['stupidMaterial'] = False
    param['holzapfelParameters'] = (.0377/2., 9.09e-4, 3., 45., 0.)
    param['fiberDirection'] = [-math.pi/6.,math.pi/6.,-math.pi/6.,math.pi/6.]
    #param['twoDirections'] = False
    param['scratchDir'] = 'D:\Abaqus'
    param['numCpus'] = 1
    param['saveCaeFile'] = True
    #
    param.update(_p)
    return param
#-----------------------------------------------------  
def getEandNu(holzapfelParam):
    c10 = holzapfelParam[0]
    d = holzapfelParam[1]
    k = holzapfelParam[2]
    #elastic equivalent for the full material, initial fibre stiffness
    if d==0.: nu = 0.499
    else: nu = (6-2*(4./3.*k+2*c10)*d)/(12+4*d*c10)
    E = 8./3.*k+4*(1+nu)*c10
    return E,nu
#-----------------------------------------------------
def createAnalysisPartionedCuboid(param):
    dH = param['h']/param['nbParts']
    m = mdb.Model(param['modelName'])
    directions = list()
    matNames = list()
    a = m.rootAssembly
    s = m.ConstrainedSketch(name='__profile__', sheetSize=200.0)
    s.setPrimaryObject(option=STANDALONE)
    s.rectangle(point1=(param['l1'],0.), point2=(0.,param['l2']))
    p = m.Part(name='Part-1', dimensionality=THREE_D, type=DEFORMABLE_BODY)
    p.BaseSolidExtrude(sketch=s, depth=param['h'])
    s.unsetPrimaryObject()
    for cube in range(param['nbParts']-1):
        z0 = cube*dH
        middlePt = (param['l1']/3.,param['l2']/3.,z0+dH/3.)
        pt1 = p.DatumPointByCoordinate(coords=(0.,0.,z0+dH))
        pt2 = p.DatumPointByCoordinate(coords=(0.,param['l2']/3.,z0+dH))
        pt3 = p.DatumPointByCoordinate(coords=(param['l1']/3.,0.,z0+dH))
        pickedCells = p.cells.findAt((middlePt,))
        p.PartitionCellByPlaneThreePoints(cells=pickedCells, point1=p.datums[pt1.id], point2=p.datums[pt2.id], point3=p.datums[pt3.id])
    p.seedPart(size=param['seedSize'])
    p.generateMesh()
    elType = mesh.ElemType(C3D8R, hourglassControl=ENHANCED)
    p.setElementType((p.cells,), (elType,))
    i = a.Instance(name=p.name+'-1', part=p, dependent=ON)
    upperFaces = list()
    lowerFaces = list()
    for cube in range(param['nbParts']):
        sectionName = 'section_%i'%cube
        matName = 'mat_%i'%cube
        z0 = cube*dH
        middlePt = (param['l1']/3.,param['l2']/3.,z0+dH/3.)
        pickedCells2 = p.cells.findAt((middlePt,))
        # create material
        myMat = m.Material(name=matName)
        if isinstance(param['holzapfelParameters'],list) and len(param['holzapfelParameters']) == param['nbParts']: matParam = param['holzapfelParameters'][cube]
        elif len(param['holzapfelParameters']) == 5: matParam = param['holzapfelParameters']
        else: raise("parameter 'holzapfelParameters' of unknown type or wrong length")
        E,nu = getEandNu(matParam)
        if not param['stupidMaterial']:
            if matParam[1]==0.: myMat.Hyperelastic(table=(matParam,),materialType=ANISOTROPIC,anisotropicType=HOLZAPFEL ,behaviorType=INCOMPRESSIBLE,localDirections=1)
            else: myMat.Hyperelastic(table=(matParam,),materialType=ANISOTROPIC,anisotropicType=HOLZAPFEL ,behaviorType=COMPRESSIBLE,localDirections=1)
            if isinstance(param['fiberDirection'],list) and len(param['fiberDirection']) == param['nbParts']: fibreAngle = param['fiberDirection'][cube]
            elif isinstance(param['fiberDirection'],float): fibreAngle = param['fiberDirection']
            else: raise("parameter 'fiberDirection' of unknown type or wrong length")
            directions.append((math.cos(fibreAngle),math.sin(fibreAngle),0.))
            matNames.append(matName)
        else:
            if matParam[1]==0.: myMat.Hyperelastic(testData=OFF,table=((E/(4*(1.+nu)),0.),),materialType=ISOTROPIC,type=NEO_HOOKE,behaviorType=INCOMPRESSIBLE)            
            else: myMat.Hyperelastic(testData=OFF,table=((E/(4*(1.+nu)),6*(1-2.*nu)/E),),materialType=ISOTROPIC,type=NEO_HOOKE,behaviorType=COMPRESSIBLE)            
        abaqusTools.assignMaterialToPartition(matName,p,sectionName,pickedCells2,m)
        upperFacePoint = (param['l1']/3.,param['l2'],z0+dH/3.)
        upperFaces.append(i.faces.findAt((upperFacePoint,) ))
        lowerFacePoint = (param['l1']/3.,0.,z0+dH/3.)
        lowerFaces.append(i.faces.findAt((lowerFacePoint,) ))

    innerPt = (param['l1']/3.,param['l2']/3.,0.)
    innerFace = i.faces.findAt((innerPt,))
    innerSet = a.Set(faces=innerFace, name='innerFace')
    outerPt = (param['l1']/3.,param['l2']/3.,z0+dH)
    outerFace = i.faces.findAt((outerPt,))
    outerSet = a.Set(faces=outerFace, name='outerFace')
    lowerSet = tuple(lowerFaces)
    a.Set(faces=lowerSet, name='lowerFace')
    upperSet = tuple(upperFaces)
    a.Set(faces=upperSet, name='upperFace')
    
    m.StaticStep(name='Step-1', previous='Initial', nlgeom=ON, timePeriod=1.,initialInc=.0001,maxNumInc=10000, minInc=.000001)
    if param['BCType'] == 'Tension':
        m.PinnedBC(name='BC-1', createStepName='Step-1', region=innerSet, localCsys=None)
        m.DisplacementBC(name='BC-2', createStepName='Step-1', region=outerSet, u1=0.0, u2=0.0, u3=param['displ'])
    elif param['BCType'] == 'Compression':
        m.PinnedBC(name='BC-1', createStepName='Step-1', region=innerSet, localCsys=None)
        m.DisplacementBC(name='BC-2', createStepName='Step-1', region=outerSet, u1=0.0, u2=0.0, u3=-1.*param['displ'])
    elif param['BCType'] == 'ParrTension':
        m.PinnedBC(name='BC-1', createStepName='Step-1', region=upperSet, localCsys=None)
        m.DisplacementBC(name='BC-2', createStepName='Step-1', region=lowerSet, u1=0.0, u2=-1.*param['displ'], u3=0.0)
    elif param['BCType'] == 'ParrCompression':
        m.PinnedBC(name='BC-1', createStepName='Step-1', region=upperSet, localCsys=None)
        m.DisplacementBC(name='BC-2', createStepName='Step-1', region=lowerSet, u1=0.0, u2=param['displ'], u3=0.0)
    ## JOB
    myJobDef = JobDefinition(param['modelName'])
    myJobDef.setScratchDir(param['scratchDir'])
    if not param['stupidMaterial']:
        myJobDef.setToFibrous()        
        myJobDef.fibreDirections(directions)
        myJobDef.setFibreInputType('partition')
        myJobDef.setMatNames(matNames)
    myNewJob = myJobDef.create()
    if param['numCpus']>1: myNewJob.setValues(numCpus=param['numCpus'],numDomains=param['numCpus'],multiprocessingMode=THREADS)
    if param['saveCaeFile']:mdb.saveAs(myNewJob.name)
    return myNewJob,mdb


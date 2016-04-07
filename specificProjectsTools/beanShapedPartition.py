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
    # MODEL
    fileName = 'D:/myWork/FEModels/beanShapedAnnulus/modelBuilt/monoPartition.inp'
    fileName.replace('/',os.sep)
    param['inpFile'] = fileName
    #most inner part = part lam_8 --> instance_8, section_8, mat_8
    param['modelName'] = 'beanAnnulus'
    # LOAD
    param['load'] = 'displ'
    #loadMagnitude:
    #value is equivalent force (N) if load = Pressure [area = 202.74], 
    #      is displacement (mm)    if load = displ (positive for tension, negative for compression) or shear,
    #      is force (N)            if load = PressurePlane
    param['loadMagnitude'] = -0.6 #default load = 10% compression by displacement
    param['internalLoad'] = None # None if no internal pressure, value in MPa otherwise [area = 248.453846397946]

    # MATERIAL
    param['matType'] = 'Hooke'#or 'Holzapfel' or 'neoHooke'
    param['holzapfelParametersA'] = (.01885, 9.09e-4, 2., 190., 0.)
    param['holzapfelParametersP'] = (.01885, 9.09e-4, 5., 10., 0.)
    param['fiberOrientation'] = (math.pi/6., )
    param['twoDirections'] = False
    # INTERFACE
    param['interfaceType'] = 'Tie'#default is frctionless contact
    param['frictionCoef'] = 0.1
    # COMPUTATION
    param['timePeriod'] = 1.
    param['nlgeom'] = False
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
    if param['matType'] != 'Hooke' and not param['nlgeom']:
        print 'non linear geometry enforced with hyperelastic materials'
        param['nlgeom'] = True
    ## IMPORT FILE
    mdb.ModelFromInputFile(inputFileName=param['inpFile'], name=param['modelName'])
    abaqusTools.deleteDefaultModel()
    ## SHORTCUTS
    myModel = mdb.models[param['modelName']]
    myAssembly = myModel.rootAssembly
    myASets =  myAssembly.sets
    ## STEP CREATION
    nlGeom = OFF
    if param['nlgeom']:
        nlGeom = ON
    myModel.StaticStep(initialInc=1e-5 ,timePeriod=param['timePeriod'], maxInc=.1, minInc=1e-8, name='Load', nlgeom=nlGeom, previous='Initial',maxNumInc=10000)
    
    directions = list()
    matNames = list()
    for p,myPart in enumerate(myModel.parts.values()):
        myPSet = myPart.sets
        partNo = int(myPart.name.split('_')[1])
        ## MATERIALS
        myMatA = myModel.materials['MATA_%i'%partNo]
        myMatP = myModel.materials['MATP_%i'%partNo]

        fullPartSet = myPart.sets['ALLPARTSET']

        EA,nuA = getEandNu(param['holzapfelParametersA'])
        EP,nuP = getEandNu(param['holzapfelParametersP'])
        if param['matType'] == 'Hooke':
            myMatA.Elastic(table=((EA, nuA), ))
            myMatP.Elastic(table=((EP, nuP), ))
        elif param['matType'] == 'neoHooke':
            myMatA.Hyperelastic(testData=OFF,table=((EA/(4*(1.+nuA)),6*(1-2.*nuA)/EA),),materialType=ISOTROPIC,type=NEO_HOOKE
            ,behaviorType=COMPRESSIBLE)
            myMatP.Hyperelastic(testData=OFF,table=((EP/(4*(1.+nuP)),6*(1-2.*nuP)/EP),),materialType=ISOTROPIC,type=NEO_HOOKE
            ,behaviorType=COMPRESSIBLE)
        elif param['matType'] == 'Holzapfel':
            if param['twoDirections']:
                myMatA.Hyperelastic(table=(param['holzapfelParametersA'],),materialType=ANISOTROPIC,anisotropicType=HOLZAPFEL
                ,behaviorType=COMPRESSIBLE,localDirections=2)
                myMatP.Hyperelastic(table=(param['holzapfelParametersP'],),materialType=ANISOTROPIC,anisotropicType=HOLZAPFEL
                ,behaviorType=COMPRESSIBLE,localDirections=2)
            else:
                myMatA.Hyperelastic(table=(param['holzapfelParametersA'],),materialType=ANISOTROPIC,anisotropicType=HOLZAPFEL
                ,behaviorType=COMPRESSIBLE,localDirections=1)
                myMatP.Hyperelastic(table=(param['holzapfelParametersP'],),materialType=ANISOTROPIC,anisotropicType=HOLZAPFEL
                ,behaviorType=COMPRESSIBLE,localDirections=1)

            datum = myPart.DatumAxisByPrincipalAxis(principalAxis=ZAXIS)
            normalAxis = myPart.surfaces['EXTERNALSURFACE']
            myPart.MaterialOrientation(region=fullPartSet, orientationType=DISCRETE, axis=AXIS_1, normalAxisDefinition=SURFACE, normalAxisRegion=normalAxis, normalAxisDirection=AXIS_1, primaryAxisDefinition=DATUM, primaryAxisDatum=myPart.datums[datum.id], primaryAxisDirection=AXIS_3)
            fibreAngle = param['fiberOrientation'][p]
            directions.append((0.,math.cos(fibreAngle),math.sin(fibreAngle)))
            directions.append((0.,math.cos(fibreAngle),math.sin(fibreAngle)))
            matNames.append('MATA_%i'%partNo)
            matNames.append('MATP_%i'%partNo)
        ## ELEMENT INTEGRATION (to ensure hourglass control - may not be needed!!)
        elemType1 = mesh.ElemType(elemCode=C3D8R, elemLibrary=STANDARD, hourglassControl=ENHANCED)
        elemType2 = mesh.ElemType(elemCode=C3D4, elemLibrary=STANDARD)
        myPart.setElementType(regions=(myPart.elements,), elemTypes=(elemType1, elemType2))

    ## BC'S - any vertical / internal pressure only / any vertical + internal pressure
    #print myASets
    if param['load'] == 'displ':
        myModel.DisplacementBC(createStepName='Load', name='displacement', region=myASets['ZMAX'], u3=param['loadMagnitude'])
        myModel.PinnedBC(createStepName='Load', name='fixation', region=myASets['ZMIN'])
        #myModel.DisplacementBC(createStepName='Load', name='noRadialDispl', region=myASets['ZMAX'], u1=0., u2=0.)
    elif param['load'] == 'shearLongAxis':
        myModel.DisplacementBC(createStepName='Load', name='displacement', region=myASets['ZMAX'], u2=param['loadMagnitude'])
        myModel.PinnedBC(createStepName='Load', name='fixation', region=myASets['ZMIN'])
        myModel.DisplacementBC(createStepName='Load', name='noRadialDispl', region=myASets['ZMAX'], u1=0., u2=0.)
    elif param['load'] == 'shearShortAxis':
        myModel.DisplacementBC(createStepName='Load', name='displacement', region=myASets['ZMAX'], u1=param['loadMagnitude'])
        myModel.PinnedBC(createStepName='Load', name='fixation', region=myASets['ZMIN'])
        myModel.DisplacementBC(createStepName='Load', name='noRadialDispl', region=myASets['ZMAX'], u1=0., u2=0.)
    elif param['load'] =='Pressure':
        # magnitude provided = PRESSURE
        myModel.Pressure(name='Pressure',createStepName='Load',region=myASurface['ZMAX'],magnitude=p['loadMagnitude'],
        distributionType=UNIFORM)
        myModel.PinnedBC(createStepName='Load', name='fixation', region=myASets['ZMIN'])
        myModel.DisplacementBC(createStepName='Load', name='noRadialDispl', region=myASets['ZMAX'], u1=0., u2=0.)
    elif param['load'] == 'PressurePlane':
        myModel.PinnedBC(createStepName='Load', name='fixation', region=myASets['ZMIN'])
        import regionToolset
        # magnitude provided = concentrated FORCE on the rigid plane
        surf = myModel.ConstrainedSketch(name='surf', sheetSize=200.)
        surf.Line(point1=(0., 0.), point2=(0.0, 30.))
        surfPart = myModel.Part(name='crushingPart', dimensionality=THREE_D, type=ANALYTIC_RIGID_SURFACE)
        surfPart.AnalyticRigidSurfExtrude(sketch=surf, depth=30.)
        surfPart.ReferencePoint(point=(7.5, 15., 0.))
        crushPlane = myAssembly.Instance(name='crushingPlane', part=surfPart, dependent=ON)
        myAssembly.ParallelFace(movablePlane=crushPlane.faces[0], fixedPlane=myASurface['ZMAX'], flip=ON)
        myAssembly.translate(instanceList=('crushingPlane', ), vector=(0., 0., 6.))
        side1Faces1 = crushPlane.faces.getSequenceFromMask(mask=('[#1 ]', ), )
        myCrushingSurface = myAssembly.Surface(side1Faces=side1Faces1, name='crushingSurface')
        myModel.Tie(name='tieTop', master=myCrushingSurface, slave=myASurface['ZMAX'])
        region = regionToolset.Region(referencePoints=(crushPlane.referencePoints[2], ))
        myModel.ConcentratedForce(name='Load-1', createStepName='Load', region=region, cf2=-p['loadMagnitude'], distributionType=UNIFORM,
        follower=ON)
        myModel.DisplacementBC(name='pressurePlane', createStepName='Load', region=region, u1=0., u2=0., ur1=0., ur2=0., ur3=0.,
        distributionType=UNIFORM)
    elif param['internalLoad']:#z fixations if internal pressure only
        myModel.ZsymmBC(name='FixedTop',createStepName='Load',region=myASurface['ZMAX'])
        myModel.ZsymmBC(name='Fixed',createStepName='Load',region=myASurface['ZMIN'])
    else: raise Exception("no BC's have been defined!!")
    if param['internalLoad']:
        mostInnerPart = myAssembly.instances['INSTANCE_1']
        mostInnerSurface = mostInnerPart.surfaces['INTERNALSURFACE']
        myModel.Pressure(name='intPressure',createStepName='Load',region=mostInnerSurface,magnitude=param['internalLoad'],
        distributionType=UNIFORM)
    ## OUTPUT REQUESTS
    #fieldVariable = ('S', 'LE', 'U', 'RT', 'P', 'CSTRESS', 'CDISP', 'CFORCE')
    #myModel.fieldOutputRequests['F-Output-1'].setValues(variables=fieldVariable)
    ## JOB
    from abaqusPythonTools.jobCreation import JobDefinition
    myJobDef = JobDefinition(param['modelName'])
    myJobDef.setScratchDir(param['scratchDir'])
    if param['matType'] == 'Holzapfel':
        myJobDef.setToFibrous()        
        myJobDef.fibreDirections(directions)
        if param['twoDirections']:
            myJobDef.setFibreInputType('twoDirections')
    myJob = myJobDef.create()
    if param['numCpus']>1: 
        myJob.setValues(numCpus=param['numCpus'],numDomains=param['numCpus'],multiprocessingMode=THREADS)
    mdb.saveAs(param['modelName'])
    return myJob,mdb

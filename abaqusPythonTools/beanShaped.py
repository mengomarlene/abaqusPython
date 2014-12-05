# -*- coding: mbcs -*-
from abaqus import *
backwardCompatibility.setValues(reportDeprecated=False)
from abaqusConstants import *
from caeModules import *    
import mesh
import abaqusTools
import os, math
#-----------------------------------------------------
def getParameters(_p={}):
    param = {}
    # MODEL
    fileName = 'D:/myWork/FEModels/myModels/beanShapedAnnulus/modelBuilt/multiLayer3D.inp'
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
    param['holzapfelParameters'] = (.0377/2., 9.09e-4, 3., 45., 0.)
    param['fiberOrientation'] = (math.pi/6.,-math.pi/6.,math.pi/6.,-math.pi/6.,math.pi/6.,-math.pi/6.,math.pi/6.,-math.pi/6.)
    param['twoDirections'] = False
    # INTERFACE
    param['interfaceType'] = 'Tie'#default is frctionless contact
    param['frictionCoef'] = 0.1
    param['cohesivePenalties'] = (100.0, 100.0, 100.0) #irrelevant if param['interfaceType'] does not contain 'Cohesive'
    # COMPUTATION
    param['timePeriod'] = 1.
    param['nlgeom'] = False
    param['scratchDir'] = 'D:\Abaqus'
    param['numCpus'] = 1

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
    myASurface = myAssembly.surfaces
    ## STEP CREATION
    nlGeom = OFF
    if param['nlgeom']:
        nlGeom = ON
    if 'Cohesive' in param['interfaceType']:
        myModel.StaticStep(initialInc=1e-5 ,timePeriod=param['timePeriod'], maxInc=.1, minInc=1e-9, name='Load', nlgeom=nlGeom, previous='Initial',maxNumInc=10000)
    elif param['interfaceType'] == 'Friction':
        myModel.StaticStep(initialInc=1e-4 ,timePeriod=param['timePeriod'], maxInc=.1, minInc=1e-9, name='Load', nlgeom=nlGeom, previous='Initial',maxNumInc=10000)
    else:
        myModel.StaticStep(initialInc=1e-3 ,timePeriod=param['timePeriod'], maxInc=.1, minInc=1e-8, name='Load', nlgeom=nlGeom, previous='Initial',maxNumInc=10000)
    myModel.steps['Load'].control.setValues(allowPropagation=OFF, resetDefaultValues=OFF, timeIncrementation=(8, 10, 0, 0, 10, 0, 12, 10, 0, 0, 50))
    #I0=4(nb equ ite),Ir=8 (),Ip=9,Ic=16,Il=10,Ig=4,Is=12,Ia=5 (nb of cut back in 1 inc),Ij=6,It=3,Isc=50
    directions = list()
    matNames = list()
    E,nu = getEandNu(param['holzapfelParameters'])
    for p,myPart in enumerate(myModel.parts.values()):
        myPSet = myPart.sets
        partNo = int(myPart.name.split('_')[1])
        ## MATERIALS
        myMat = myModel.materials['MAT_%i'%partNo]
        try:
            del myMat.hyperelastic#delete existing material def
        except (AttributeError):
            pass
        fullPartSet = myPart.sets['ALLPARTSET']
        if param['matType'] == 'Hooke': myMat.Elastic(table=((E, nu), ))
        elif param['matType'] == 'neoHooke':
            if param['holzapfelParameters'][1]==0.: myMat.Hyperelastic(testData=OFF,table=((E/(4*(1.+nu)),0.),),materialType=ISOTROPIC,type=NEO_HOOKE,behaviorType=INCOMPRESSIBLE)            
            else: myMat.Hyperelastic(testData=OFF,table=((E/(4*(1.+nu)),6*(1-2.*nu)/E),),materialType=ISOTROPIC,type=NEO_HOOKE,behaviorType=COMPRESSIBLE)            
        elif param['matType'] == 'Holzapfel':
            if param['holzapfelParameters'][1]==0.:# incompressible
                if param['twoDirections']: myMat.Hyperelastic(table=(param['holzapfelParameters'],),materialType=ANISOTROPIC,anisotropicType=HOLZAPFEL ,behaviorType=INCOMPRESSIBLE,localDirections=2)
                else: myMat.Hyperelastic(table=(param['holzapfelParameters'],),materialType=ANISOTROPIC,anisotropicType=HOLZAPFEL ,behaviorType=INCOMPRESSIBLE,localDirections=1)
            else:          
                if param['twoDirections']: myMat.Hyperelastic(table=(param['holzapfelParameters'],),materialType=ANISOTROPIC,anisotropicType=HOLZAPFEL ,behaviorType=COMPRESSIBLE,localDirections=2)
                else: myMat.Hyperelastic(table=(param['holzapfelParameters'],),materialType=ANISOTROPIC,anisotropicType=HOLZAPFEL ,behaviorType=COMPRESSIBLE,localDirections=1)
            datum = myPart.DatumAxisByPrincipalAxis(principalAxis=ZAXIS)
            normalAxis = myPart.surfaces['EXTERNALSURFACE']
            myPart.MaterialOrientation(region=fullPartSet, orientationType=DISCRETE, axis=AXIS_1, normalAxisDefinition=SURFACE, normalAxisRegion=normalAxis, normalAxisDirection=AXIS_1, primaryAxisDefinition=DATUM, primaryAxisDatum=myPart.datums[datum.id], primaryAxisDirection=AXIS_3)
            fibreAngle = param['fiberOrientation'][p]
            directions.append((0.,math.cos(fibreAngle),math.sin(fibreAngle)))
            matNames.append('MAT_%i'%partNo)
        ## ELEMENT INTEGRATION (to ensure hourglass control - may not be needed!!)
        elemType1 = mesh.ElemType(elemCode=C3D8R, elemLibrary=STANDARD, hourglassControl=ENHANCED)
        elemType2 = mesh.ElemType(elemCode=C3D4, elemLibrary=STANDARD)
        myPart.setElementType(regions=(myPart.elements,), elemTypes=(elemType1, elemType2))
        myModel.HomogeneousSolidSection('section_%s'%partNo, material='MAT_%i'%partNo)
        myPart.SectionAssignment(region=fullPartSet, sectionName='section_%s'%partNo)

    ## CONSTRAINTS - same for all interfaces!!
    for nbInteraction in range(1,len(myModel.parts.keys())):
        myMaInstance = myAssembly.instances['INSTANCE_%i'%nbInteraction]
        mySlInstance = myAssembly.instances['INSTANCE_%i'%(nbInteraction+1)]
        from interactions import Interactions
        inter = Interactions(myModel)
        inter.setMasterSlave(myMaInstance.surfaces['INTERNALSURFACE'],mySlInstance.surfaces['EXTERNALSURFACE'])
        inter.setName('interaction_%i'%(nbInteraction))
        if param['interfaceType'] == 'Tie':
            inter.setInteractionToTie()
        elif param['interfaceType'] == 'Friction':
            inter.setFrictionBehaviour('Friction',param['frictionCoef'])
            inter.setSeparationAllowed()
        elif param['interfaceType'] == 'Rough':
            inter.setFrictionBehaviour('Rough')
        elif param['interfaceType'] == 'Cohesive':
            inter.setCohesiveBehaviour(useDefaultBehaviour=False,penalties=param['cohesivePenalties'])
        elif param['interfaceType'] == 'CohesiveRough':
            inter.setCohesiveBehaviour(useDefaultBehaviour=False)
            inter.setFrictionBehaviour('Rough')
        elif param['interfaceType'] == 'CohesiveFriction':
            inter.setCohesiveBehaviour(useDefaultBehaviour=False)
            inter.setFrictionBehaviour('Friction',param['frictionCoef'])
        inter.createInteraction()
    ## BC'S - any vertical / internal pressure only / any vertical + internal pressure
    if param['load'] == 'displ':
        myModel.DisplacementBC(createStepName='Load', name='displacement', region=myASets['ZMAX'], u3=param['loadMagnitude'])
        myModel.PinnedBC(createStepName='Load', name='fixation', region=myASets['ZMIN'])
        #if 'Cohesive' not in param['interfaceType'] and param['interfaceType'] != 'Friction':
        myModel.DisplacementBC(createStepName='Load', name='noRadialDispl', region=myASets['ZMAX'], u1=0., u2=0.)
    elif param['load'] =='Pressure':
        # magnitude provided = PRESSURE
        myModel.Pressure(name='Pressure',createStepName='Load',region=myASurface['ZMAX'],magnitude=param['loadMagnitude'],
        distributionType=UNIFORM)
        myModel.PinnedBC(createStepName='Load', name='fixation', region=myASets['ZMIN'])
        myModel.DisplacementBC(createStepName='Load', name='noRadialDispl', region=myASets['ZMAX'], u1=0., u2=0.)
    elif param['load'] == 'PressurePlane':
        myModel.PinnedBC(createStepName='Load', name='fixation', region=myASets['ZMIN'])
        import regionToolset
        # magnitude provided = concentrated FORCE on the rigid plane
        surf = myModel.ConstrainedSketch(name='surf', sheetSize=200.)
        surf.Line(point1=(-1., 0.), point2=(17., 0.))
        surfPart = myModel.Part(name='crushingPart', dimensionality=THREE_D, type=ANALYTIC_RIGID_SURFACE)
        surfPart.AnalyticRigidSurfExtrude(sketch=surf, depth=26.)
        crushPlane = myAssembly.Instance(name='crushingPlane', part=surfPart, dependent=ON)
        myAssembly.rotate(instanceList=('crushingPlane', ), axisPoint=(0., 0., 0.), axisDirection=(1., 0., 0.), angle=90.)
        myAssembly.translate(instanceList=('crushingPlane', ), vector=(0., 13., 6.))
        surfPart.ReferencePoint(point=(8., 0., 0.))
        myCrushingSurface = myAssembly.Surface(side1Faces=crushPlane.faces.getSequenceFromMask(mask=('[#1 ]', ), ), name='crushingSurface')
        myModel.Tie(name='tieTop', master=myCrushingSurface, slave=myASurface['ZMAX'])
        region = regionToolset.Region(referencePoints=(crushPlane.referencePoints[2], ))
        myModel.ConcentratedForce(name='Load-1', createStepName='Load', region=region, cf3=-param['loadMagnitude'], distributionType=UNIFORM,
        follower=ON)
        myModel.DisplacementBC(name='pressurePlane', createStepName='Load', region=region, u1=0., u2=0., ur1=0., ur2=0., ur3=0.,
        distributionType=UNIFORM)
    elif param['internalLoad']:#z fixations if internal pressure only
        myModel.ZsymmBC(name='FixedTop',createStepName='Load',region=myASurface['ZMAX'])
        myModel.ZsymmBC(name='Fixed',createStepName='Load',region=myASurface['ZMIN'])
    else: raise Exception("no BC's have been defined!!")
    if param['internalLoad']:
        try:
            mostInnerSurface = myAssembly.instances['INSTANCE_8'].surfaces['INTERNALSURFACE']
        except KeyError:
            if param['twoDirections']:
                mostInnerSurface = myAssembly.instances['INSTANCE_1'].surfaces['INTERNALSURFACE']
            else: raise Exception("Undefined internal surface")
        myModel.Pressure(name='intPressure',createStepName='Load',region=mostInnerSurface,magnitude=param['internalLoad'],
        distributionType=UNIFORM)
    ## OUTPUT REQUESTS
    # fieldVariable = ('S', 'LE', 'U', 'RT', 'P', 'CSTRESS', 'CDISP', 'CFORCE')
    # myModel.fieldOutputRequests['F-Output-1'].setValues(variables=fieldVariable)
    ## JOB
    from jobCreation import JobDefinition
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

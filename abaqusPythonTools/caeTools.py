# -*- coding: mbcs -*-
"""
caeTools
"""
## classical python modules
import math
## my abaqus module
import abaqusTools

## default abaqus modules
from abaqus import *
backwardCompatibility.setValues(reportDeprecated=False)
from abaqusConstants import *
#some caeModules seem not to be imported by abaqus cae in noGUI,
#let's import all of them here!!
from caeModules import *
#-----------------------------------------------------
def getParameters(_p={}):
    param = {}
    #GEOMETRY
    param['nbParts'] = 2
    param['nbCut'] = [2,2]
    param['innerRadius'] = 12.
    param['lamellarThickness'] = .6
    param['height'] = 12.
    param['width'] = 5.#for cuboid models
    param['center'] = (0.,0.)
    param['length'] = 25.#for rectangular lamellae and cuboids
    #MATERIAL
    param['myMaterialName'] = ['AFPositif','AFNegatif']
    param['stupidMaterial'] = False
    param['matType'] = 'neoHooke'#'Holzapfel' or 'neoHooke'
    '''holzapfelParameters: C10,D,k1,k2,kappa
        ==========
        HUMAN DATA
        ==========
        C10 linear fit ground matrix shear stress/shear strain (Little_JMBBM_2010) in MPa
          fit at max apparent linear shear strain: 2*C10 = 0.0377 (r^2 = 0.9817)
        D: bulk modulus, K=2/D --> PhD@ETH K=2200MPa
        k1,k2 Holzapfel fit fiber Stretch/PK2 in MPa [C10 equivalent for initial fibre stretch only!)
          Holzapfel_2005
          coef1 - dorsalExternal1  k1,k2 = 1.9317   77.1463 r^2 = 0.9988 rms = 2.70%
                  equivalent (GM + fibres) E = 5.9315 MPa (see matlabScripts/plotFullStress)
                  equivalent (GM + fibres) nu = 0.4996 (0.5-E/6K)
                  equivalent (fibres) C10 = 0.9762 MPa (see matlabScripts/plotFullStress)
          coef2 - dorsalExternal2  k1,k2 = 2.4136   72.8267 r^2 = 0.9960 rms = 4.68%
                  equivalent (GM + fibres) E = 7.3585 MPa
                  equivalent (GM + fibres) nu = 0.4994
                  equivalent (fibres) C10 = 1.2142 MPa (see matlabScripts/plotFullStress)
          coef3 - dorsalInternal1  k1,k2 = 0.2115   13.0878 r^2 = 0.9962 rms = 2.91%
                  equivalent (GM + fibres) E = 0.6748 MPa
                  equivalent (GM + fibres) nu = 0.4999
                  equivalent (fibres) C10 = 0.0998 MPa (see matlabScripts/plotFullStress)
          coef4 - dorsalInternal2  k1,k2 = 0.3259   11.0381 r^2 = 0.9943 rms = 3.57%
                  equivalent (GM + fibres) E = 0.9968 MPa
                  equivalent (GM + fibres) nu = 0.4999
                  equivalent (fibres) C10 = 0.1535 MPa (see matlabScripts/plotFullStress)
          coef5 - vlExternal       k1,k2 = 8.2963  319.0410 r^2 = 0.9865 rms = 9.22%
                  equivalent (GM + fibres) E = 32.9071 MPa
                  equivalent (GM + fibres) nu = 0.4975
                  equivalent (fibres) C10 = 5.4810 MPa (see matlabScripts/plotFullStress)
          coef6 - vlInternal1      k1,k2 = 1.4536   40.4437 r^2 = 0.9984 rms = 1.81%
                  equivalent (GM + fibres) E = 4.3129 MPa
                  equivalent (GM + fibres) nu = 0.4997
                  equivalent (fibres) C10 = 0.7063 MPa (see matlabScripts/plotFullStress)
          coef7 - vlInternal2      k1,k2 = 0.8804   54.1728 r^2 = 0.9960 rms = 2.41%
                  equivalent (GM + fibres) E = 2.6799 MPa
                  equivalent (GM + fibres) nu = 0.4998
                  equivalent (fibres) C10 = 0.4340 MPa (see matlabScripts/plotFullStress)
          coef8 - Eberlein_CM_2004 k1,k2 = 3.0000   45 (also used in PhD@ETH) 
                  equivalent (GM + fibres) E = 8.8627 MPa
                  equivalent (GM + fibres) nu = 0.4993
                  equivalent (fibres) C10 = 1.4651 MPa (see matlabScripts/plotFullStress)
        kappa=0. for perfectly oriented; 1/3 for isotropic
    '''
    param['holzapfelParameters'] = (.0377/2., 9.09e-4, 3., 45., 0.)
    param['fiberDirection'] = [math.pi/6.,-math.pi/6.]#list of fiber angles in the (theta,z) plane
    param['twoDirections'] = False#creates a material with two complementary directions given by fiberDirections instead of two materials with one direction each
    #MESH
    param['meshType'] = 'seedEdgeByNumber'      #'seedEdgeBySize','seedEdgeByNumber','seedPartInstance'
    param['meshControl'] = 40                   #size for 'seedPartInstance' or 'seedEdgeBySize', 
                                                #number for 'seedEdgeByNumber'
    param['elemType'] = 'C3D8RH'
    #INTERACTIONS
    param['interfaceType'] = 'Tie'                  #'Frictionless', 'Tie', 'Friction'
    param['contactStiffness'] = 1.                  #irrelevant if param['interfaceType']=='Tie'
    param['frictionCoef'] = 0.1                     #irrelevant if param['interfaceType']!='Friction'
    param['cohesivePenalties'] = (5.0, 5.0, 5.0)    #irrelevant if param['interfaceType'] does not contain 'Cohesive'
    from abaqusConstants import ON,OFF
    param['allowSeparation'] = ON              #ON, OFF
    #STEP
    param['timePeriod'] = 1.
    param['initialInc'] = 1e-5# needed for contact detection, can be larger for Tie
    param['maxInc'] = 0.08
    param['minInc'] = min(1e-6,param['initialInc']/1000)
    #LOAD
    param['load'] = 'Pressure'
    param['loadMagnitude'] = 0.07 # [MPa] 12Rings --> area~700mm^2 --> force~50N
    param['displ'] = 0.1*param['height']
    param['internalPressure'] = None
    #JOB
    param['modelName'] = 'defaultName'
    param['scratchDir'] = '.'
    param['numCpus'] = 1
    param['saveCaeFile'] = True
    #
    param.update(_p)
    return param
#-----------------------------------------------------
def setElementType(eleTypeString):
    from abaqusConstants import C3D8R,C3D8RH,ENHANCED 
    if eleTypeString=='C3D8RH': eleType = mesh.ElemType(C3D8RH, hourglassControl=ENHANCED)
    else:eleType = mesh.ElemType(C3D8R, hourglassControl=ENHANCED)
    return eleType
#-----------------------------------------------------
def createHollowCylinderPart(center,innerRadius,outerRadius,height,name,model,angle=360):
    myCercle = model.ConstrainedSketch(name+'_sketch',sheetSize=250.)
    #hollow cylinder = rectangle revolution
    myCercle.rectangle((center[0]+innerRadius,center[1]),(center[0]+outerRadius,center[1]+height))
    myCercle.ConstructionLine((0.,0.),(0.,1.))#revolution axis
    myCylinder = model.Part(name+'_part',dimensionality=THREE_D,type=DEFORMABLE_BODY)
    myCylinder.BaseSolidRevolve(myCercle,angle)
    return myCylinder
#-----------------------------------------------------
def createCuboidPart(width,length,height,name,model):
    myRect = model.ConstrainedSketch(name+'_sketch',sheetSize=250.)
    myRect.rectangle((0,0),(width,length))
    myCuboid = model.Part(name+'_part',dimensionality=THREE_D,type=DEFORMABLE_BODY)
    myCuboid.BaseSolidExtrude(sketch=myRect, depth=height)
    return myCuboid
#-----------------------------------------------------  
def getEandNuPerp(holzapfelParam):
    c10 = holzapfelParam[0]
    d = holzapfelParam[1]
    #elastic equivalent for the full material, initial fibre stiffness
    if d==0.: nu = 0.499
    else: nu = (3-2*c10*d)/(6+2*d*c10)
    E = 4*(1+nu)*c10
    return E,nu
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
#-----------------------------------------------------
def analysisWithPartitionCylinders(p):
    # check parameter consistency
    if len(p['nbCut']) != p['nbParts']: raise Exception("nbCut is a list of number of cut for each lamellae, its length must be equal to nbParts!!")
    if len(p['myMaterialName']) != sum(p['nbCut']): raise Exception("number of material names as to be equal to the number of domains (total nb of cuts)!!")
    if any(360%i for i in p['nbCut']): raise Exception("number of cuts per part must be a divider of 360!!")

    # MODEL
    myModel = mdb.Model(p['modelName'])
    myAssembly = myModel.rootAssembly
    abaqusTools.deleteDefaultModel()

    instances = list()
    directions = list()
    bottomFace = list()
    topFace = list()
    innerFace = list()
    outerFace = list()

    for cyl in range(p['nbParts']):
        #geometry
        angle = 360/p['nbCut'][cyl]
        cylinderName = 'cylinder%d'%(cyl)
        r0 = p['innerRadius']+p['lamellarThickness']*cyl
        r1 = p['innerRadius']+p['lamellarThickness']*(cyl+1)
        rm = (r1+r0)/2.
        parts = createHollowCylinderPart(p['center'],r0,r1,p['height'],cylinderName,myModel)
        # coordinate system
        csysCyl = parts.DatumCsysByThreePoints(coordSysType=CYLINDRICAL,origin=(0.,0.,0.),point1=(1.,0.,0.),point2=(0.,0.,-1.))
        bottomPoint = list()
        topPoint = list()
        innerPoint = list()
        outerPoint = list()
        for arc in range(p['nbCut'][cyl]):
            middlePt = (r0*math.cos(angle*(arc+.5)*math.pi/180),p['height']/2,r0*math.sin(angle*(arc+.5)*math.pi/180))
            bottomPoint.append((rm*math.cos(angle*(arc+.5)*math.pi/180),0,rm*math.sin(angle*(arc+.5)*math.pi/180)))
            topPoint.append((rm*math.cos(angle*(arc+.5)*math.pi/180),p['height'],rm*math.sin(angle*(arc+.5)*math.pi/180)))
            innerPoint.append(middlePt)
            outerPoint.append((r1*math.cos(angle*(arc+.5)*math.pi/180),p['height']/2,r1*math.sin(angle*(arc+.5)*math.pi/180)))
            pt1 = parts.DatumPointByCoordinate(coords=(r0*math.cos(angle*(arc+1)*math.pi/180),0,r0*math.sin(angle*(arc+1)*math.pi/180)))
            pt2 = parts.DatumPointByCoordinate(coords=(r1*math.cos(angle*(arc+1)*math.pi/180),0,r1*math.sin(angle*(arc+1)*math.pi/180)))
            pt3 = parts.DatumPointByCoordinate(coords=(r1*math.cos(angle*(arc+1)*math.pi/180),p['height'],r1*math.sin(angle*(arc+1)*math.pi/180)))
            pt4 = parts.DatumPointByCoordinate(coords=(r0*math.cos(angle*(arc+1)*math.pi/180),p['height'],r0*math.sin(angle*(arc+1)*math.pi/180)))
            pickedCells = parts.cells.findAt((middlePt,))
            parts.PartitionCellByPatchNCorners(cell=pickedCells[0],cornerPoints=[parts.datums[pt1.id],
            parts.datums[pt2.id], parts.datums[pt3.id], parts.datums[pt4.id]])
        for arc in range(p['nbCut'][cyl]):
            sectionName = cylinderName+'_section%d'%(arc)
            domainNb = int(sum(p['nbCut'][0:cyl]))+arc
            middlePt = (r0*math.cos(angle*(arc+.5)*math.pi/180),p['height']/2,r0*math.sin(angle*(arc+.5)*math.pi/180))
            pickedCells2 = parts.cells.findAt((middlePt,))
            # create material
            myMat = myModel.Material(name=p['myMaterialName'][domainNb])
            if isinstance(p['holzapfelParameters'],list) and len(p['holzapfelParameters']) == int(sum(p['nbCut'])):#there is one set of parameters per cut
                matParam = p['holzapfelParameters'][domainNb]
            elif len(p['holzapfelParameters']) == 5:
                matParam = p['holzapfelParameters']
            else: raise("parameter 'holzapfelParameters' of unknown type or wrong length")
            E,nu = getEandNu(matParam)
            if not p['stupidMaterial']:
                if matParam[1]==0.:# incompressible
                    myMat.Hyperelastic(table=(matParam,),materialType=ANISOTROPIC,anisotropicType=HOLZAPFEL
                    ,behaviorType=INCOMPRESSIBLE,localDirections=1)
                else:
                    myMat.Hyperelastic(table=(matParam,),materialType=ANISOTROPIC,anisotropicType=HOLZAPFEL
                    ,behaviorType=COMPRESSIBLE,localDirections=1)
                if isinstance(p['fiberDirection'],list) and len(p['fiberDirection']) == int(sum(p['nbCut'])):
                    fibreAngle = p['fiberDirection'][domainNb]
                elif isinstance(p['fiberDirection'],float):
                    fibreAngle = p['fiberDirection']
                else: raise("parameter 'fiberDirection' of unknown type or wrong length")
                directions.append((0.,math.cos(fibreAngle),math.sin(fibreAngle)))
            else:
                if matParam[1]==0.:# incompressible
                    myMat.Hyperelastic(testData=OFF,table=((E/(4*(1.+nu)),0.),),materialType=ISOTROPIC,type=NEO_HOOKE,behaviorType=INCOMPRESSIBLE)            
                else:
                    myMat.Hyperelastic(testData=OFF,table=((E/(4*(1.+nu)),6*(1-2.*nu)/E),),materialType=ISOTROPIC,type=NEO_HOOKE,behaviorType=COMPRESSIBLE)            
            # assign material
            abaqusTools.assignMaterialToPartition(p['myMaterialName'][domainNb],parts,sectionName,pickedCells2,myModel,orientation=csysCyl)
        instances.append(abaqusTools.createInstanceAndAddtoAssembly(parts,myAssembly))
        ptMeshC = list()
        ptMeshW = list()
        for arc in range(p['nbCut'][cyl]):
            bottomFace.append(instances[cyl].faces.findAt((bottomPoint[arc],)))
            topFace.append(instances[cyl].faces.findAt((topPoint[arc],)))
            innerFace.append(instances[cyl].faces.findAt((innerPoint[arc],)))
            outerFace.append(instances[cyl].faces.findAt((outerPoint[arc],)))
            ptMeshC.append((r1*math.cos(angle*(arc+.5)*math.pi/180),0,r1*math.sin(angle*(arc+.5)*math.pi/180)))
            ptMeshC.append((r1*math.cos(angle*(arc+.5)*math.pi/180),p['height'],r1*math.sin(angle*(arc+.5)*math.pi/180)))
            ptMeshW.append((rm*math.cos(angle*arc*math.pi/180),0,rm*math.sin(angle*arc*math.pi/180)))
            ptMeshW.append((rm*math.cos(angle*arc*math.pi/180),p['height'],rm*math.sin(angle*arc*math.pi/180)))

        if 'Edge' in p['meshType']:
            intEdge = instances[cyl].edges.getSequenceFromMask(mask=('[#1 ]', ), )
            extEdge = instances[cyl].edges.getSequenceFromMask(mask=('[#4 ]', ), )
            edge = list()
            ctrl = list()
            for n in range(2*p['nbCut'][cyl]):
                edge.append(instances[cyl].edges.findAt((ptMeshW[n],)))
                if 'Number' in p['meshType']: ctrl.append(2)
                else: ctrl.append(.2)
                edge.append(instances[cyl].edges.findAt((ptMeshC[n],)))
                ctrl.append(int(p['meshControl']/p['nbCut'][cyl]))

            abaqusTools.assignElemtypeAndMesh(instances[cyl],myAssembly,setElementType(p['elemType']),control=ctrl,meshType=p['meshType']
            ,edges=edge)
        else:
            abaqusTools.assignElemtypeAndMesh(instances[cyl],myAssembly,setElementType(p['elemType']),control=p['meshControl'],meshType=p['meshType'])

    if p['nbParts']>1:
        ##CONSTRAINTS - same for all interfaces!!
        for nb in range(1,p['nbParts']):
            domainNb = int(sum(p['nbCut'][0:nb]))
            outerFaces = tuple(outerFace[domainNb-i-1] for i in range(p['nbCut'][nb-1]))
            innerFaces = tuple(innerFace[domainNb+i] for i in range(p['nbCut'][nb]))
            masterSurface = myAssembly.Surface(name='master%d'%(nb),side1Faces=outerFaces)
            slaveSurface = myAssembly.Surface(name='slave%d'%(nb),side1Faces=innerFaces)
            from interactions import Interactions
            inter = Interactions(myModel)
            inter.setMasterSlave(masterSurface,slaveSurface)
            inter.setName('interface%d'%(nb))
            if p['interfaceType'] == 'Tie':
                inter.setInteractionToTie()
            elif p['interfaceType'] == 'Friction':
                inter.setFrictionBehaviour('Friction')
            elif p['interfaceType'] == 'Cohesive':
                inter.setCohesiveBehaviour()
            elif p['interfaceType'] == 'CohesiveFriction':
                inter.setCohesiveBehaviour()
                inter.setFrictionBehaviour('Friction')
            inter.createInteraction()

	##STEP
    myModel.StaticStep(name='Load',previous='Initial',timePeriod=p['timePeriod'],initialInc=p['initialInc'],nlgeom=ON,
    maxInc=p['maxInc'],minInc=p['minInc'],maxNumInc=10000)
    myModel.steps['Load'].control.setValues(allowPropagation=OFF, resetDefaultValues=OFF, discontinuous=ON)
    #,timeIncrementation=(0, 0, 0, 0, 10.0, 0, 12.0, 0, 0, 0, 50.0))
    #I0=4(nb equ ite),Ir=8,Ip=9,Ic=16,Il=10,Ig=4,Is=12,Ia=5,Ij=6,It=3,Isc=50 cannot change if discontinuous ON
	
    ##LOAD/BC - after step as the step names are used!!!
    myTopSurface = myAssembly.Surface(name='topSurface',side1Faces=topFace)
    cylSys = myAssembly.DatumCsysByThreePoints(name='cylC',coordSysType=CYLINDRICAL, origin=(0,0,0),\
    point1=(1.0, 0.0, 0), point2=(0.0, 0.0, -1.0) )
    datumCyl = myAssembly.datums[cylSys.id]
    if p['load'] =='Pressure':#default
        # magnitude provided = PRESSURE
        myModel.Pressure(name='Pressure',createStepName='Load',region=myTopSurface,magnitude=p['loadMagnitude'],
        distributionType=UNIFORM)
        myModel.DisplacementBC(name='noRadialDispl',createStepName='Load',region=tuple(topFace),u1=0.,localCsys=datumCyl)
        myModel.PinnedBC(name='Fixed',createStepName='Load',region=tuple(bottomFace))
    elif p['load'] == 'Pressure_total':
        #!!magnitude provided = total INITIAL FORCE, when the area varies -> force = magnitude*area1/area0!!
        myModel.Pressure(name='Pressure',createStepName='Load',region=myTopSurface,magnitude=p['loadMagnitude'],
        distributionType=TOTAL_FORCE)
        myModel.DisplacementBC(name='noRadialDispl',createStepName='Load',region=tuple(topFace),u1=0.,localCsys=datumCyl)
        myModel.PinnedBC(name='Fixed',createStepName='Load',region=tuple(bottomFace))
    elif p['load'] == 'vertDispl':
        myModel.DisplacementBC(name='Displ',createStepName='Load',region=tuple(topFace),u1=0.,u2=-p['displ'],u3=0.)
        myModel.DisplacementBC(name='noRadialDispl',createStepName='Load',region=tuple(topFace),u1=0.,u3=-p['displ'],localCsys=datumCyl)
        myModel.PinnedBC(name='Fixed',createStepName='Load',region=tuple(bottomFace))
    elif p['load'] == 'PressurePlane':
        import regionToolset
        # magnitude provided = concentrated FORCE on the rigid plane
        extR = p['innerRadius']+p['lamellarThickness']*p['nbParts']
        surf = myModel.ConstrainedSketch(name='surf', sheetSize=200.0)
        surf.Line(point1=(0.0, extR), point2=(0.0, -extR))
        surfPart = myModel.Part(name='crushingPart', dimensionality=THREE_D, type=ANALYTIC_RIGID_SURFACE)
        surfPart.AnalyticRigidSurfExtrude(sketch=surf, depth=2.*extR)
        surfPart.ReferencePoint(point=(0.0, 0.0, 0.0))
        crushPlane = myAssembly.Instance(name='crushingPlane', part=surfPart, dependent=ON)
        f1 = myAssembly.instances['crushingPlane'].faces[0]
        f2 = myAssembly.instances['cylinder0_instance'].faces[1]
        myAssembly.ParallelFace(movablePlane=f1, fixedPlane=f2, flip=ON)
        myAssembly.translate(instanceList=('crushingPlane', ), vector=(0.0, p['height'], 0.0))
        side1Faces1 = crushPlane.faces.getSequenceFromMask(mask=('[#1 ]', ), )
        myCrushingSurface = myAssembly.Surface(side1Faces=side1Faces1, name='crushingSurface')
        myModel.Tie(name='tieTop', master=myCrushingSurface, slave=myTopSurface)
        region = regionToolset.Region(referencePoints=(crushPlane.referencePoints[2], ))
        myModel.ConcentratedForce(name='Load-1', createStepName='Load', region=region, cf2=-p['loadMagnitude'], distributionType=UNIFORM,
        follower=ON)
        myModel.DisplacementBC(name='BC-2', createStepName='Load', region=region, u1=0.0, u3=0.0, ur1=0.0, ur2=0.0, ur3=0.0,
        distributionType=UNIFORM)
        myModel.DisplacementBC(name='noRadialDispl',createStepName='Load',region=tuple(topFace),u1=0.,u3=-p['displ'],localCsys=datumCyl)
        myModel.PinnedBC(name='Fixed',createStepName='Load',region=tuple(bottomFace))
    else:#load only in internal pressure
        if p['internalPressure']:
            myModel.XsymmBC(name='FixedTop',createStepName='Load',region=tuple(topFace),localCsys=datumCyl)
            myModel.XsymmBC(name='Fixed',createStepName='Load',region=tuple(bottomFace),localCsys=datumCyl)
        else: raise Exception("no BC's have been defined!!")
    if p['internalPressure']:
        myInnerSurface = myAssembly.Surface(name='innerSurface',side1Faces=(innerFace[0],innerFace[1],))
        myModel.Pressure(name='intPressure',createStepName='Load',region=myInnerSurface,magnitude=p['internalPressure'],
        distributionType=UNIFORM)
    
    ## SETS FOR OUTPUT ANALYSIS
    intVerticalEdge = instances[0].edges.getSequenceFromMask(mask=('[#1 ]', ), )
    extVerticalEdge = instances[-1].edges.getSequenceFromMask(mask=('[#4 ]', ), )
    myAssembly.Set(edges=intVerticalEdge, name='intVerticalSegment')
    myAssembly.Set(edges=extVerticalEdge, name='extVerticalSegment')
    myAssembly.Set(faces=tuple(topFace), name='topFaces')
    myAssembly.Set(faces=tuple(bottomFace), name='bottomFaces')
	
    ## OUTPUT REQUESTS
    fieldVariable = ('S', 'LE', 'U', 'RT', 'P', 'CSTRESS', 'CDISP', 'CFORCE')
    # LOCALDIR1 added by default...
    #myModel.fieldOutputRequests['F-Output-1'].setValues(variables=fieldVariable)
    
    ## JOB
    from jobCreation import JobDefinition
    myJobDef = JobDefinition(p['modelName'])
    myJobDef.setScratchDir(p['scratchDir'])
    if not p['stupidMaterial']:
        myJobDef.setToFibrous()        
        myJobDef.fibreDirections(directions)
        myJobDef.setFibreInputType('partition')
        myJobDef.setMatNames(matNames)
    myNewJob = myJobDef.create()
    if p['numCpus']>1:
        myNewJob.setValues(numCpus=p['numCpus'],numDomains=p['numCpus'],multiprocessingMode=THREADS)
    myNewJob.setValues(memory=3, memoryUnits=GIGA_BYTES)
    if p['saveCaeFile']:mdb.saveAs(myNewJob.name)
    #-------------------------------------------------------
    return myNewJob,mdb
##################################################################################
##################################################################################  
def analysisWithPartialCylinders(p):
    # check parameter consistency
    if len(p['nbCut']) != p['nbParts']:  raise Exception("nbCut is a list of number of cut for each lamellae, its length must be equal to nbParts!!")
    if len(p['myMaterialName']) != sum(p['nbCut']): raise Exception("number of material names as to be equal to the number of domains (total nb of cuts)!!")
    if any(360%i for i in p['nbCut']): raise Exception("number of cuts per part must be a divider of 360!!")

    ## MODEL
    myModel = mdb.Model(p['modelName'])
    myAssembly = myModel.rootAssembly
    abaqusTools.deleteDefaultModel()

    instances = list()
    directions = list()
    bottomFace = list()
    topFace = list()
    innerFace = list()
    outerFace = list()
    endFaces = list()
    startFaces = list()
    
    for cyl in range(p['nbParts']):
        angle = 360/p['nbCut'][cyl]
        for arc in range(p['nbCut'][cyl]):
            domainNb = int(sum(p['nbCut'][0:cyl]))+arc
            # create cylinder arc
            cylinderName = 'cylinder%d'%(domainNb)
            parts = createHollowCylinderPart(p['center'],p['innerRadius']+p['lamellarThickness']*cyl,
            p['innerRadius']+p['lamellarThickness']*(cyl+1),p['height'],cylinderName,myModel,angle)
            # coordinate system
            csysCyl = parts.DatumCsysByThreePoints(coordSysType=CYLINDRICAL,origin=(0.,0.,0.),point1=(1.,0.,0.),point2=(0.,0.,-1.))
            # create material
            myMat = myModel.Material(name=p['myMaterialName'][domainNb])
            if isinstance(p['holzapfelParameters'],list):
                if isinstance(p['holzapfelParameters'][cyl],list) and len(p['holzapfelParameters'][cyl]) == p['nbCut'][cyl]:#there is one set of parameters per cut
                    matParam = p['holzapfelParameters'][cyl][arc]
                elif len(p['holzapfelParameters'][cyl]) == 5:#there is one set of parameters for the part
                    matParam = p['holzapfelParameters'][cyl]
            elif len(p['holzapfelParameters']) == 5:
                matParam = p['holzapfelParameters']
            else: raise("parameter 'holzapfelParameters' of unknown type or wrong length")
            E,nu = getEandNu(matParam)
            if not p['stupidMaterial']:
                if matParam[1]==0.:# incompressible
                    myMat.Hyperelastic(table=(matParam,),materialType=ANISOTROPIC,anisotropicType=HOLZAPFEL
                    ,behaviorType=INCOMPRESSIBLE,localDirections=1)
                else:
                    myMat.Hyperelastic(table=(matParam,),materialType=ANISOTROPIC,anisotropicType=HOLZAPFEL
                    ,behaviorType=COMPRESSIBLE,localDirections=1)
                if isinstance(p['fiberDirection'][cyl],list) and len(p['fiberDirection'][cyl]) == p['nbCut'][cyl]:#there is one set of fiber angle per cut
                    fibreAngle = p['fiberDirection'][cyl][arc]
                elif isinstance(p['fiberDirection'][cyl],float):#there is one set of fiber angle for the part
                    fibreAngle = p['fiberDirection'][cyl]
                else: raise("parameter 'fiberDirection' of unknown type or wrong length")
                directions.append((0.,math.cos(fibreAngle),math.sin(fibreAngle)))
            else:
                if matParam[1]==0.:# incompressible
                    myMat.Hyperelastic(testData=OFF,table=((E/(4*(1.+nu)),0.),),materialType=ISOTROPIC,type=NEO_HOOKE,behaviorType=INCOMPRESSIBLE)            
                else:
                    myMat.Hyperelastic(testData=OFF,table=((E/(4*(1.+nu)),6*(1-2.*nu)/E),),materialType=ISOTROPIC,type=NEO_HOOKE,behaviorType=COMPRESSIBLE) 
            # assign material
            abaqusTools.assignMaterialToPart(p['myMaterialName'][domainNb],parts,myModel,orientation=csysCyl)
            instances.append(abaqusTools.createInstanceAndAddtoAssembly(parts,myAssembly))
            myAssembly.rotate(instanceList=(cylinderName+'_instance', ), axisPoint=(0.0, 0.0, 0.0), 
            axisDirection=(0.0, 1.0, 0.0), angle=angle*arc)
            bottomFace.append(instances[domainNb].faces.getSequenceFromMask(mask=('[#8 ]', ), ))
            innerFace.append(instances[domainNb].faces.getSequenceFromMask(mask=('[#1 ]', ), ))
            topFace.append(instances[domainNb].faces.getSequenceFromMask(mask=('[#2 ]', ), ))
            outerFace.append(instances[domainNb].faces.getSequenceFromMask(mask=('[#4 ]', ), ))
            if 'Edge' in p['meshType']:
                circEdges = instances[domainNb].edges.getSequenceFromMask(mask=('[#4 ]',),)
                widthEdges = instances[domainNb].edges.getSequenceFromMask(mask=('[#8 ]',),)
                if 'Number' in p['meshType']: ctrl = [p['meshControl'],2]
                else: ctrl = [p['meshControl'],.2]
                abaqusTools.assignElemtypeAndMesh(instances[domainNb],myAssembly,setElementType(p['elemType']),control=ctrl,meshType=p['meshType']
                ,edges=[circEdges,widthEdges])
            else:
                abaqusTools.assignElemtypeAndMesh(instances[domainNb],myAssembly,setElementType(p['elemType']),control=p['meshControl'],meshType=p['meshType'])
            interfaceName = 'interdomain%d'%(domainNb)   
            if arc > 0 :
                endFace = instances[domainNb-1].faces.getSequenceFromMask(mask=('[#20 ]', ), )
                startFace = instances[domainNb].faces.getSequenceFromMask(mask=('[#10 ]', ), )
                endRegion = myAssembly.Surface(name='end%d'%(domainNb),side1Faces=endFace)
                startRegion = myAssembly.Surface(name='start%d'%(domainNb),side1Faces=startFace)
                myModel.Tie(name=interfaceName,master=endRegion,slave=startRegion)
        interfaceName = 'interdomain%d'%(int(sum(p['nbCut'][0:cyl])))   
        startFace = instances[int(sum(p['nbCut'][0:cyl]))].faces.getSequenceFromMask(mask=('[#10 ]', ), )
        endFace = instances[domainNb].faces.getSequenceFromMask(mask=('[#20 ]', ), )
        endRegion = myAssembly.Surface(name='end%d'%(int(sum(p['nbCut'][0:cyl]))),side1Faces=endFace)
        startRegion = myAssembly.Surface(name='start%d'%(int(sum(p['nbCut'][0:cyl]))),side1Faces=startFace)
        myModel.Tie(name=interfaceName,master=endRegion,slave=startRegion)

    if p['nbParts']>1:
        ## CONSTRAINTS - same for all interfaces!!
        for nb in range(1,p['nbParts']):
            domainNb = int(sum(p['nbCut'][0:nb]))
            outerFaces = tuple(outerFace[domainNb-i-1] for i in range(p['nbCut'][nb-1]))
            innerFaces = tuple(innerFace[domainNb+i] for i in range(p['nbCut'][nb]))
            masterRegion = myAssembly.Surface(name='master%d'%(nb),side1Faces=outerFaces)
            slaveRegion = myAssembly.Surface(name='slave%d'%(nb),side1Faces=innerFaces)
            from interactions import Interactions
            inter = Interactions(myModel)
            inter.setMasterSlave(masterRegion,slaveRegion)
            inter.setName('interface%d'%(nb))
            if p['interfaceType'] == 'Tie':
                inter.setInteractionToTie()
            elif p['interfaceType'] == 'Friction':
                inter.setFrictionBehaviour('Friction')
            inter.createInteraction()
	## STEP
    myModel.StaticStep(name='Load',previous='Initial',timePeriod=p['timePeriod'],initialInc=p['initialInc'],nlgeom=ON,
    maxInc=p['maxInc'],minInc=p['minInc'],maxNumInc=10000)
    myModel.steps['Load'].control.setValues(allowPropagation=OFF, resetDefaultValues=OFF, 
    timeIncrementation=(4.0, 8.0, 9.0, 9.0, 10.0, 4.0, 12.0, 5.0, 6.0, 3.0, 50.0))
	## LOAD/BC - after step as the step names are used!!!
    myModel.PinnedBC(name='Fixed',createStepName='Load',region=tuple(bottomFace))
    myTopSurface = myAssembly.Surface(name='topSurface',side1Faces=topFace)
    cylSys = myAssembly.DatumCsysByThreePoints(name='cylC',coordSysType=CYLINDRICAL, origin=(0,0,0),\
    point1=(1.0, 0.0, 0), point2=(0.0, 0.0, -1.0) )
    datumCyl = myAssembly.datums[cylSys.id]
    if p['load'] =='Pressure':#default
        # magnitude provided = PRESSURE
        myModel.Pressure(name='Pressure',createStepName='Load',region=myTopSurface,magnitude=p['loadMagnitude'],
        distributionType=UNIFORM)
        myModel.DisplacementBC(name='noRadialDispl',createStepName='Load',region=tuple(topFace),u1=0.,localCsys=datumCyl)
    elif p['load'] == 'Pressure_total':
        #!!magnitude provided = total INITIAL FORCE, when the area varies -> force = magnitude*area1/area0!!
        myModel.Pressure(name='Pressure',createStepName='Load',region=myTopSurface,magnitude=p['loadMagnitude'],
        distributionType=TOTAL_FORCE)
        myModel.DisplacementBC(name='noRadialDispl',createStepName='Load',region=tuple(topFace),u1=0.,localCsys=datumCyl)
    elif p['load'] == 'vertDispl':
        myModel.DisplacementBC(name='Displ',createStepName='Load',region=tuple(topFace),u1=0.,u2=-p['displ'],u3=0.)
        #myModel.DisplacementBC(name='noRadialDispl',createStepName='Load',region=tuple(topFace),u1=0.,u3=-p['displ'],localCsys=datumCyl)
    elif p['load'] == 'PressurePlane':
        import regionToolset
        # magnitude provided = concentrated FORCE on the rigid plane
        extR = p['innerRadius']+p['lamellarThickness']*p['nbParts']
        surf = myModel.ConstrainedSketch(name='surf', sheetSize=200.0)
        surf.Line(point1=(0.0, extR), point2=(0.0, -extR))
        surfPart = myModel.Part(name='crushingPart', dimensionality=THREE_D, type=ANALYTIC_RIGID_SURFACE)
        surfPart.AnalyticRigidSurfExtrude(sketch=surf, depth=2.*extR)
        surfPart.ReferencePoint(point=(0.0, 0.0, 0.0))
        crushPlane = myAssembly.Instance(name='crushingPlane', part=surfPart, dependent=ON)
        f1 = myAssembly.instances['crushingPlane'].faces[0]
        f2 = myAssembly.instances['cylinder0_instance'].faces[1]
        myAssembly.ParallelFace(movablePlane=f1, fixedPlane=f2, flip=ON)
        myAssembly.translate(instanceList=('crushingPlane', ), vector=(0.0, p['height'], 0.0))
        side1Faces1 = crushPlane.faces.getSequenceFromMask(mask=('[#1 ]', ), )
        myCrushingSurface = myAssembly.Surface(side1Faces=side1Faces1, name='crushingSurface')
        myModel.Tie(name='tieTop', master=myCrushingSurface, slave=myTopSurface)
        region = regionToolset.Region(referencePoints=(crushPlane.referencePoints[2], ))
        myModel.ConcentratedForce(name='Load-1', createStepName='Load', region=region, cf2=-p['loadMagnitude'], distributionType=UNIFORM,
        follower=ON)
        myModel.DisplacementBC(name='BC-2', createStepName='Load', region=region, u1=0.0, u3=0.0, ur1=0.0, ur2=0.0, ur3=0.0,
        distributionType=UNIFORM)
    if p['internalPressure']:
        myInnerSurface = myAssembly.Surface(name='innerSurface',side1Faces=(innerFace[0],))
        myModel.Pressure(name='intPressure',createStepName='Load',region=myInnerSurface,magnitude=p['internalPressure'],
        distributionType=UNIFORM)  
    ## SETS FOR OUTPUT ANALYSIS
    intVerticalEdge = instances[0].edges.getSequenceFromMask(mask=('[#1 ]', ), )
    myAssembly.Set(edges=intVerticalEdge, name='intVerticalSegment')
    extVerticalEdge = instances[-1].edges.getSequenceFromMask(mask=('[#80 ]', ), )
    myAssembly.Set(edges=extVerticalEdge, name='extVerticalSegment')
    myAssembly.Set(faces=tuple(topFace), name='topFaces')
    myAssembly.Set(faces=tuple(bottomFace), name='bottomFaces')	
    ## OUTPUT REQUESTS
    fieldVariable = ('S', 'LE', 'U', 'RT', 'P', 'CSTRESS', 'CDISP', 'CFORCE')
    #myModel.fieldOutputRequests['F-Output-1'].setValues(variables=fieldVariable)
    ## JOB
    from jobCreation import JobDefinition
    myJobDef = JobDefinition(p['modelName'])
    myJobDef.setScratchDir(p['scratchDir'])
    if not p['stupidMaterial']:
        myJobDef.setToFibrous()        
        myJobDef.fibreDirections(directions)
    myNewJob = myJobDef.create()    
    if p['numCpus']>1:
        myNewJob.setValues(numCpus=p['numCpus'],numDomains=p['numCpus'],multiprocessingMode=THREADS)
    if p['saveCaeFile']:mdb.saveAs(myNewJob.name)
    #-------------------------------------------------------
    return myNewJob,mdb
##################################################################################
##################################################################################    
def analysisWithCylinders(p):
    # check parameter consistency
    if len(p['myMaterialName']) != p['nbParts']: raise Exception("number of material names as to be equal to the number of parts!!")
    if not p['stupidMaterial']:
        if len(p['fiberDirection']) != p['nbParts']: raise Exception("number of fiber directions as to be equal to the number of parts!!")
	# MODEL
    myModel = mdb.Model(p['modelName'])
    myAssembly = myModel.rootAssembly
    abaqusTools.deleteDefaultModel()

    instances = list()
    directions = list()
    bottomFace = list()
    topFace = list()
    innerFace = list()
    outerFace = list()
    
    for cyl in range(p['nbParts']):
        # create cylinder
        cylinderName = 'cylinder%d'%(cyl)
        parts = createHollowCylinderPart(p['center'],p['innerRadius']+p['lamellarThickness']*cyl,
        p['innerRadius']+p['lamellarThickness']*(cyl+1),p['height'],cylinderName,myModel)
        # coordinate system
        csysCyl = parts.DatumCsysByThreePoints(coordSysType=CYLINDRICAL,origin=(0.,0.,0.),point1=(1.,0.,0.),point2=(0.,0.,-1.))
        # create material
        myMat = myModel.Material(name=p['myMaterialName'][cyl])

        if isinstance(p['holzapfelParameters'],list):
            if isinstance(p['holzapfelParameters'][cyl],list) and len(p['holzapfelParameters'][cyl]) == p['nbCut'][cyl]:#there is one set of parameters per cut
                matParam = p['holzapfelParameters'][cyl][arc]
            elif len(p['holzapfelParameters'][cyl]) == 5:#there is one set of parameters for the part
                matParam = p['holzapfelParameters'][cyl]
        elif len(p['holzapfelParameters']) == 5:
            matParam = p['holzapfelParameters']
        else: raise("parameter 'holzapfelParameters' of unknown type or wrong length")
        E,nu = getEandNu(matParam)
        if p['stupidMaterial']:
            myMat.Elastic(table=((E, nu), ))
        elif p['matType'] == 'Holzapfel':
            if matParam[1]==0.:# incompressible
                if p['twoDirections']:
                    myMat.Hyperelastic(table=(matParam,),materialType=ANISOTROPIC,anisotropicType=HOLZAPFEL
                    ,behaviorType=INCOMPRESSIBLE,localDirections=2)
                else:
                    myMat.Hyperelastic(table=(matParam,),materialType=ANISOTROPIC,anisotropicType=HOLZAPFEL
                    ,behaviorType=INCOMPRESSIBLE,localDirections=1)
            else:
                if p['twoDirections']:
                    myMat.Hyperelastic(table=(matParam,),materialType=ANISOTROPIC,anisotropicType=HOLZAPFEL
                    ,behaviorType=COMPRESSIBLE,localDirections=2)
                else:
                    myMat.Hyperelastic(table=(matParam,),materialType=ANISOTROPIC,anisotropicType=HOLZAPFEL
                    ,behaviorType=COMPRESSIBLE,localDirections=1)
        elif p['matType'] == 'neoHooke':
            if matParam[1]==0.:# incompressible
                myMat.Hyperelastic(testData=OFF,table=((E/(4*(1.+nu)),0.),),materialType=ISOTROPIC,type=NEO_HOOKE,behaviorType=INCOMPRESSIBLE)            
            else:
                myMat.Hyperelastic(testData=OFF,table=((E/(4*(1.+nu)),6*(1-2.*nu)/E),),materialType=ISOTROPIC,type=NEO_HOOKE,behaviorType=COMPRESSIBLE) 
        # assign material
        abaqusTools.assignMaterialToPart(p['myMaterialName'][cyl],parts,myModel,orientation=csysCyl)
        instances.append(abaqusTools.createInstanceAndAddtoAssembly(parts,myAssembly))
        if not p['stupidMaterial']:
            directions.append((0.,math.cos(p['fiberDirection'][cyl]),math.sin(p['fiberDirection'][cyl])))
        # Find the bottom/top faces using coordinates.
        bottomFacePoint = (p['innerRadius']+p['lamellarThickness']*cyl,0.,0.)
        bottomFace.append(instances[cyl].faces.findAt((bottomFacePoint,) ))
        innerFacePoint = (p['innerRadius']+p['lamellarThickness']*cyl,p['height']/2.,0.)
        innerFace.append(instances[cyl].faces.findAt((innerFacePoint,) ))
        topFacePoint = (p['innerRadius']+p['lamellarThickness']*cyl,p['height'],0.)
        topFace.append(instances[cyl].faces.findAt((topFacePoint,)))
        outerFacePoint = (p['innerRadius']+p['lamellarThickness']*(cyl+1),p['height']/2.,0.)
        outerFace.append(instances[cyl].faces.findAt((outerFacePoint,)))
        
        if 'Edge' in p['meshType']:
            circEdges = instances[cyl].edges.getSequenceFromMask(mask=('[#4 ]',),)
            widthEdges = instances[cyl].edges.getSequenceFromMask(mask=('[#8 ]',),)
            try:
                if len(p['meshControl'])==2:ctrl=p['meshControl']
            except(TypeError):
                if 'Number' in p['meshType']: ctrl = [p['meshControl'],2]
                else: ctrl = [p['meshControl'],.2]
            abaqusTools.assignElemtypeAndMesh(instances[cyl],myAssembly,setElementType(p['elemType']),control=ctrl,meshType=p['meshType']
            ,edges=[circEdges,widthEdges])
        else:
            abaqusTools.assignElemtypeAndMesh(instances[cyl],myAssembly,setElementType(p['elemType']),control=p['meshControl'],meshType=p['meshType'])
    if p['nbParts']>1:
        ## CONSTRAINTS - same for all interfaces!!
        for nb in range(1,p['nbParts']):
            masterRegion = myAssembly.Surface(name='master%d'%(nb),side1Faces=outerFace[nb-1])
            slaveRegion = myAssembly.Surface(name='slave%d'%(nb),side1Faces=innerFace[nb])
            from interactions import Interactions
            inter = Interactions(myModel)
            inter.setMasterSlave(masterRegion,slaveRegion)
            inter.setName('interface%d'%(nb))
            if p['interfaceType'] == 'Tie': inter.setInteractionToTie()
            elif p['interfaceType'] == 'Friction': inter.setFrictionBehaviour('Friction')
            elif p['interfaceType'] == 'Cohesive': inter.setCohesiveBehaviour(useDefaultBehaviour=False,penalties=p['cohesivePenalties'])
            inter.createInteraction()
	## STEP
    myModel.StaticStep(name='Load',previous='Initial',timePeriod=p['timePeriod'],initialInc=p['initialInc'],nlgeom=ON,
    maxInc=p['maxInc'],minInc=p['minInc'],maxNumInc=10000)

	## LOAD/BC - after step as the step names are used!!!
    myModel.PinnedBC(name='Fixed',createStepName='Load',region=tuple(bottomFace))
    myTopSurface = myAssembly.Surface(name='topSurface',side1Faces=topFace)
    cylSys = myAssembly.DatumCsysByThreePoints(name='cylC',coordSysType=CYLINDRICAL, origin=(0,0,0),\
    point1=(1.0, 0.0, 0), point2=(0.0, 0.0, -1.0) )
    datumCyl = myAssembly.datums[cylSys.id]
    if p['load'] =='Pressure':#default
        # magnitude provided = PRESSURE
        myModel.Pressure(name='Pressure',createStepName='Load',region=myTopSurface,magnitude=p['loadMagnitude'],
        distributionType=UNIFORM)
        myModel.DisplacementBC(name='noRadialDispl',createStepName='Load',region=tuple(topFace),u1=0.,localCsys=datumCyl)
    elif p['load'] == 'Pressure_total':
        #!!magnitude provided = total INITIAL FORCE, when the area varies -> force = magnitude*area1/area0!!
        myModel.Pressure(name='Pressure',createStepName='Load',region=myTopSurface,magnitude=p['loadMagnitude'],
        distributionType=TOTAL_FORCE)
        myModel.DisplacementBC(name='noRadialDispl',createStepName='Load',region=tuple(topFace),u1=0.,localCsys=datumCyl)
    elif p['load'] == 'vertDispl':
        myModel.DisplacementBC(name='Displ',createStepName='Load',region=tuple(topFace),u1=0.,u2=-p['displ'],u3=0.)        
    elif p['load'] == 'PressurePlane':
        import regionToolset
        # magnitude provided = concentrated FORCE on the rigid plane
        extR = p['innerRadius']+p['lamellarThickness']*p['nbParts']
        surf = myModel.ConstrainedSketch(name='surf', sheetSize=200.0)
        surf.Line(point1=(0.0, extR), point2=(0.0, -extR))
        surfPart = myModel.Part(name='crushingPart', dimensionality=THREE_D, type=ANALYTIC_RIGID_SURFACE)
        surfPart.AnalyticRigidSurfExtrude(sketch=surf, depth=2.*extR)
        surfPart.ReferencePoint(point=(0.0, 0.0, 0.0))
        crushPlane = myAssembly.Instance(name='crushingPlane', part=surfPart, dependent=ON)
        f1 = myAssembly.instances['crushingPlane'].faces[0]
        f2 = myAssembly.instances['cylinder0_instance'].faces[1]
        myAssembly.ParallelFace(movablePlane=f1, fixedPlane=f2, flip=ON)
        myAssembly.translate(instanceList=('crushingPlane', ), vector=(0.0, p['height'], 0.0))
        side1Faces1 = crushPlane.faces.getSequenceFromMask(mask=('[#1 ]', ), )
        myCrushingSurface = myAssembly.Surface(side1Faces=side1Faces1, name='crushingSurface')
        myModel.Tie(name='tieTop', master=myCrushingSurface, slave=myTopSurface)
        region = regionToolset.Region(referencePoints=(crushPlane.referencePoints[2], ))
        myModel.ConcentratedForce(name='Load-1', createStepName='Load', region=region, cf2=-p['loadMagnitude'], distributionType=UNIFORM,
        follower=ON)
        myModel.DisplacementBC(name='BC-2', createStepName='Load', region=region, u1=0.0, u3=0.0, ur1=0.0, ur2=0.0, ur3=0.0,
        distributionType=UNIFORM)
    else:
        myModel.PinnedBC(name='FixedTop',createStepName='Load',region=tuple(topFace))
    if p['internalPressure']:
        myInnerSurface = myAssembly.Surface(name='innerSurface',side1Faces=(innerFace[0],))
        myModel.Pressure(name='intPressure',createStepName='Load',region=myInnerSurface,magnitude=p['internalPressure'],
        distributionType=UNIFORM)
    
    ## SETS FOR OUTPUT ANALYSIS
    intVerticalEdge = instances[0].edges.getSequenceFromMask(mask=('[#1 ]', ), )
    myAssembly.Set(edges=intVerticalEdge, name='intVerticalSegment')
    extVerticalEdge = instances[-1].edges.getSequenceFromMask(mask=('[#20 ]', ), )
    myAssembly.Set(edges=extVerticalEdge, name='extVerticalSegment')
    myAssembly.Set(faces=tuple(topFace), name='topFaces')
    myAssembly.Set(faces=tuple(bottomFace), name='bottomFaces')
    fieldVariable = ('S', 'LE', 'U', 'RF', 'P', 'CSTRESS', 'CDISP', 'CFORCE')
    myModel.fieldOutputRequests['F-Output-1'].setValues(variables=fieldVariable)
    ## JOB
    from jobCreation import JobDefinition
    myJobDef = JobDefinition(p['modelName'])
    myJobDef.setScratchDir(p['scratchDir'])
    if not p['stupidMaterial'] and (p['matType'] == 'Holzapfel'):
        myJobDef.setToFibrous()        
        myJobDef.fibreDirections(directions)
        if p['twoDirections']:
            myJobDef.setFibreInputType('twoDirections')
    myNewJob = myJobDef.create()    
    if p['numCpus']>1: myNewJob.setValues(numCpus=p['numCpus'],numDomains=p['numCpus'],multiprocessingMode=THREADS)
    if p['saveCaeFile']:mdb.saveAs(myNewJob.name)
    #-------------------------------------------------------
    return myNewJob,mdb
##################################################################################
##################################################################################
def lamellarRectangle(p):

	# MODEL
    myModel = mdb.Model(p['modelName'])
    myAssembly = myModel.rootAssembly
    abaqusTools.deleteDefaultModel()
    name = p['modelName']

    # create rectangle
    from abaqusConstants import TWO_D_PLANAR,DEFORMABLE_BODY
    myRectangleSketch = myModel.ConstrainedSketch(name+'_sketch',sheetSize=250.)
    #hollow cylinder = rectangle revolution
    myRectangleSketch.rectangle((0.,0.),(p['length'],p['height']))
    myRectangle = myModel.Part(name+'_part',dimensionality=TWO_D_PLANAR, type=DEFORMABLE_BODY)
    myRectangle.BaseShell(sketch=myRectangleSketch)
    
    # create material
    myMat = myModel.Material(name=p['myMaterialName'])
    if not p['stupidMaterial']:
        myMat.Hyperelastic(table=(p['holzapfelParameters'],),materialType=ANISOTROPIC,anisotropicType=HOLZAPFEL
        ,behaviorType=INCOMPRESSIBLE,localDirections=1)
    else:
        E,nu = getEandNu(matParam)
        myMat.Elastic(table=((E,nu), ))
    # assign material
    sectionName = name+'_section'
    myModel.HomogeneousSolidSection(material=p['myMaterialName'],name=sectionName,thickness=p['lamellarThickness'])
    allSet = myRectangle.Set(faces=myRectangle.faces.getSequenceFromMask(('[#1 ]', ), ), name='Set-1')
    myRectangle.SectionAssignment(region=allSet,sectionName=sectionName,thicknessAssignment=FROM_SECTION)
    cartCoord = myRectangle.DatumCsysByDefault(CARTESIAN)
    myRectangle.MaterialOrientation(region=allSet,orientationType=SYSTEM,localCsys=myRectangle.datum[cartCoord.id])

    instanceName = name+'_instance'
    myInstance = myAssembly.Instance(dependent=OFF, name=instanceName, part=myRectangle)

    bottomEdge = myInstance.edges.getSequenceFromMask( ('[#4 ]', ), )
    topEdge = myInstance.edges.getSequenceFromMask( ('[#1 ]', ), )
    leftEdge = myInstance.edges.getSequenceFromMask( ('[#2 ]', ), )
    rightEdge = myInstance.edges.getSequenceFromMask( ('[#8 ]', ), )   
    
    myAssembly.setElementType(allSet, (setElementType(p['elemType']),))
    if p['meshType'] == 'seedPartInstance':
        myAssembly.seedPartInstance((myInstance,), size=p['meshControl'])
    else:
        p['meshControl'] *= 2
        if 'Number' in p['meshType']: 
            nbHeight = int(p['meshControl']/p['length']*p['height'])
            ctrl = [p['meshControl'],nbHeight,p['meshControl'],nbHeight]
        else: ctrl = [p['meshControl'],.2,p['meshControl'],.2]
        for c,edge in enumerate([bottomEdge,leftEdge,topEdge,rightEdge]):
            if p['meshType'] == 'seedEdgeByNumber':
                myAssembly.seedEdgeByNumber(tuple(edge,), number=ctrl[c])
            elif p['meshType'] == 'seedEdgeBySize':
                myAssembly.seedEdgeBySize(tuple(edge,), size=ctrl[c])
    myAssembly.generateMesh(regions=(myInstance,))
	##STEP
    myModel.StaticStep(name='Load',previous='Initial',timePeriod=p['timePeriod'],initialInc=p['initialInc'],nlgeom=ON,
    maxInc=p['maxInc'],minInc=p['minInc'],maxNumInc=10000)

	##LOAD/BC - after step as the step names are used!!!
    if p['load'].startswith('v'):
        myModel.PinnedBC(name='Fixed',createStepName='Load',region=tuple(bottomEdge))
        mySurface = myAssembly.Surface(side1Edges=topEdge, name='rightSurf')
        if p['load'] == 'vPressure_total':
            #!!magnitude provided = total INITIAL FORCE, when the area varies -> force = magnitude*area1/area0!!
            myModel.Pressure(name='Pressure',createStepName='Load',region=mySurface,magnitude=p['loadMagnitude'],
            distributionType=TOTAL_FORCE)
            myModel.DisplacementBC(name='noLongDispl',createStepName='Load',region=tuple(topEdge),u1=0.)
        elif p['load'] =='vPressure':
            #magnitude provided = PRESSURE
            myModel.Pressure(name='Pressure',createStepName='Load',region=mySurface,magnitude=p['loadMagnitude'],
            distributionType=UNIFORM)
            myModel.DisplacementBC(name='noLongDispl',createStepName='Load',region=tuple(topEdge),u1=0.)
        elif p['load'] =='vFreePressure':
            #magnitude provided = PRESSURE
            myModel.Pressure(name='Pressure',createStepName='Load',region=mySurface,magnitude=p['loadMagnitude'],
            distributionType=UNIFORM)
        elif p['load'] == 'vDispl':
            myModel.DisplacementBC(name='Displ',createStepName='Load',region=tuple(topEdge),u2=p['displ'],u1=0.)
        elif p['load'] == 'vFreeDispl':
            myModel.DisplacementBC(name='Displ',createStepName='Load',region=tuple(topEdge),u2=p['displ'])
    else:
        myModel.PinnedBC(name='Fixed',createStepName='Load',region=tuple(leftEdge))
        mySurface = myAssembly.Surface(side1Edges=rightEdge, name='rightSurf')
        if p['load'] =='Pressure':# default
            #magnitude provided = PRESSURE
            myModel.Pressure(name='Pressure',createStepName='Load',region=mySurface,magnitude=p['loadMagnitude'],
            distributionType=UNIFORM)
            myModel.DisplacementBC(name='noAxialDispl',createStepName='Load',region=tuple(rightEdge),u2=0.)
        elif p['load'] == 'Pressure_total':
            #!!magnitude provided = total INITIAL FORCE, when the area varies -> force = magnitude*area1/area0!!
            myModel.Pressure(name='Pressure',createStepName='Load',region=mySurface,magnitude=p['loadMagnitude'],
            distributionType=TOTAL_FORCE)
            myModel.DisplacementBC(name='noAxialDispl',createStepName='Load',region=tuple(rightEdge),u2=0.)
        elif p['load'] =='freePressure':
            myModel.Pressure(name='Pressure',createStepName='Load',region=mySurface,magnitude=p['loadMagnitude'],
            distributionType=UNIFORM)
        elif p['load'] == 'displ':
            myModel.DisplacementBC(name='Displ',createStepName='Load',region=tuple(rightEdge),u1=p['displ'],u2=0.)
        elif p['load'] == 'freeDispl':
            myModel.DisplacementBC(name='Displ',createStepName='Load',region=tuple(rightEdge),u1=p['displ'])
    
    ## SETS FOR OUTPUT ANALYSIS
    myAssembly.Set(edges=topEdge, name='top')
    myAssembly.Set(edges=leftEdge, name='left')
    myAssembly.Set(edges=bottomEdge, name='bottom')
    myAssembly.Set(edges=rightEdge, name='right')
    
    ## OUTPUT REQUESTS
    #fieldVariable = ('S', 'LE', 'U', 'RT', 'P', 'CSTRESS', 'CDISP', 'CFORCE')
    #myModel.fieldOutputRequests['F-Output-1'].setValues(variables=fieldVariable)
    ## JOB
    from jobCreation import JobDefinition
    myJobDef = JobDefinition(name)
    myJobDef.setScratchDir(p['scratchDir'])
    if not p['stupidMaterial']:
        myJobDef.setToFibrous()
        direction = list()
        direction.append((math.cos(p['fiberDirection']),math.sin(p['fiberDirection']),0.))
        myJobDef.fibreDirections(direction)
    myNewJob = myJobDef.create()    
    if p['numCpus']>1:
        myNewJob.setValues(numCpus=p['numCpus'],numDomains=p['numCpus'],multiprocessingMode=THREADS)
    if p['saveCaeFile']:mdb.saveAs(myNewJob.name)
    #-------------------------------------------------------
    return myNewJob,mdb
##################################################################################    
def analysisWithRectangles(p):
    # check parameter consistency
    if len(p['myMaterialName']) != p['nbParts']:  raise Exception("number of material names as to be equal to the number of parts!!")
    if not p['stupidMaterial']:
        if len(p['fiberDirection']) != p['nbParts']: raise Exception("number of fiber directions as to be equal to the number of parts!!")
	# MODEL
    myModel = mdb.Model(p['modelName'])
    myAssembly = myModel.rootAssembly
    abaqusTools.deleteDefaultModel()

    instances = list()
    directions = list()
    lowerFace = list()
    upperFace = list()
    innerFace = list()
    outerFace = list()
    
    for rec in range(p['nbParts']):
        # create cuboid
        rectangleName = 'cylinder%d'%(rec)
        myPart = createCuboidPart(p['width'],p['height'],p['length']/p['nbParts'],rectangleName,myModel)
        # coordinate system
        csysCyl = myPart.DatumCsysByThreePoints(coordSysType=CYLINDRICAL,origin=(0.,0.,0.),point1=(1.,0.,0.),point2=(0.,0.,-1.))
        # create material
        myMat = myModel.Material(name=p['myMaterialName'][rec])

        if isinstance(p['holzapfelParameters'],list) and len(p['holzapfelParameters']) == p['nbParts']:#there is one set of parameters per part
            matParam = p['holzapfelParameters'][rec]
        elif len(p['holzapfelParameters']) == 5:#there is one set of parameters
            matParam = p['holzapfelParameters']
        else: raise("parameter 'holzapfelParameters' of unknown type or wrong length")
        if p['load'] == 'vertDispl': E,nu = getEandNu(matParam)
        elif p['load'] == 'horizDispl': E,nu = getEandNuPerp(matParam)

        if p['stupidMaterial']:
            myMat.Elastic(table=((E, nu), ))
        elif p['matType'] == 'Holzapfel':
            if matParam[1]==0.:# incompressible
                if p['twoDirections']: myMat.Hyperelastic(table=(matParam,),materialType=ANISOTROPIC,anisotropicType=HOLZAPFEL, behaviorType=INCOMPRESSIBLE,localDirections=2)
                else: myMat.Hyperelastic(table=(matParam,),materialType=ANISOTROPIC,anisotropicType=HOLZAPFEL, behaviorType=INCOMPRESSIBLE,localDirections=1)
            else:
                if p['twoDirections']: myMat.Hyperelastic(table=(matParam,),materialType=ANISOTROPIC,anisotropicType=HOLZAPFEL, behaviorType=COMPRESSIBLE,localDirections=2)
                else: myMat.Hyperelastic(table=(matParam,),materialType=ANISOTROPIC,anisotropicType=HOLZAPFEL, behaviorType=COMPRESSIBLE,localDirections=1)
        elif p['matType'] == 'neoHooke': myMat.Hyperelastic(testData=OFF,table=((E/(4*(1.+nu)),6*(1-2.*nu)/E),),materialType=ISOTROPIC,type=NEO_HOOKE, behaviorType=COMPRESSIBLE)
        print "C10,K =  ",E/(4*(1.+nu)),6*(1-2.*nu)/E
        # assign material
        abaqusTools.assignMaterialToPart(p['myMaterialName'][rec],myPart,myModel,orientation=None)
        instances.append(abaqusTools.createInstanceAndAddtoAssembly(myPart,myAssembly,translate=(0,0,p['length']/p['nbParts']*rec)))
        if not p['stupidMaterial']: directions.append((math.cos(p['fiberDirection'][rec]),math.sin(p['fiberDirection'][rec]),0.))
        # Find the inner/outer faces using coordinates.
        innerFacePoint = (p['width']/2.,p['height']/2.,p['length']/p['nbParts']*rec)
        innerFace.append(instances[rec].faces.findAt((innerFacePoint,) ))
        outerFacePoint = (p['width']/2.,p['height']/2.,p['length']/p['nbParts']*(rec+1))
        outerFace.append(instances[rec].faces.findAt((outerFacePoint,)))
        lowerFacePoint = (p['width']/2.,0.,p['length']/p['nbParts']*(rec+0.5))
        lowerFace.append(instances[rec].faces.findAt((lowerFacePoint,) ))
        upperFacePoint = (p['width']/2.,p['height'],p['length']/p['nbParts']*(rec+0.5))
        upperFace.append(instances[rec].faces.findAt((upperFacePoint,)))
        myAssembly.seedPartInstance(regions=(instances[rec],), size=.3*p['length']/p['nbParts'])
        myAssembly.generateMesh(regions=(instances[rec],))
        myAssembly.setElementType((instances[rec].cells,), (setElementType(p['elemType']),))
    if p['nbParts']>1:
        ## CONSTRAINTS - same for all interfaces!!
        for nb in range(1,p['nbParts']):
            masterRegion = myAssembly.Surface(name='master%d'%(nb),side1Faces=outerFace[nb-1])
            slaveRegion = myAssembly.Surface(name='slave%d'%(nb),side1Faces=innerFace[nb])
            from interactions import Interactions
            inter = Interactions(myModel)
            inter.setMasterSlave(masterRegion,slaveRegion)
            inter.setName('interface%d'%(nb))
            if p['interfaceType'] == 'Tie': inter.setInteractionToTie()
            elif p['interfaceType'] == 'Friction': inter.setFrictionBehaviour('Friction')
            elif p['interfaceType'] == 'Cohesive': inter.setCohesiveBehaviour(useDefaultBehaviour=False,penalties=p['cohesivePenalties'])
            elif p['interfaceType'] == 'CohesiveFriction':
                inter.setCohesiveBehaviour()
                inter.setFrictionBehaviour('Friction')
            elif p['interfaceType'] == 'Rough': inter.setFrictionBehaviour('Rough')
            inter.createInteraction()
	## STEP
    myModel.StaticStep(name='Load',previous='Initial',timePeriod=p['timePeriod'],initialInc=p['initialInc'],nlgeom=ON,
    maxInc=p['maxInc'],minInc=p['minInc'],maxNumInc=10000)

	## LOAD/BC - after step as the step names are used!!!
    if p['load'] == 'vertDispl': myModel.PinnedBC(name='Fixed',createStepName='Load',region=tuple(upperFace))
    else: myModel.PinnedBC(name='Fixed',createStepName='Load',region=tuple(innerFace[0]))

    if p['load'] == 'horizDispl': myModel.DisplacementBC(name='Displ',createStepName='Load',region=tuple(outerFace[-1]),u1=0.,u2=0.,u3=p['displ'])#positive displ is tension
    elif p['load'] == 'vertDispl': myModel.DisplacementBC(name='Displ',createStepName='Load',region=tuple(lowerFace),u1=0.,u2=-1.*p['displ'],u3=0.)#positive displ is tension
    else: raise Exception("NOT IMPLEMENTED")
   
    ## SETS FOR OUTPUT ANALYSIS
    myAssembly.Set(faces=innerFace[0], name='innerFace')
    myAssembly.Set(faces=outerFace[-1], name='outerFace')
    myAssembly.Set(faces=tuple(lowerFace), name='lowerFace')
    myAssembly.Set(faces=tuple(upperFace), name='upperFace')
    ## JOB
    from jobCreation import JobDefinition
    myJobDef = JobDefinition(p['modelName'])
    myJobDef.setScratchDir(p['scratchDir'])
    if not p['stupidMaterial'] and (p['matType'] == 'Holzapfel'):
        myJobDef.setToFibrous()        
        myJobDef.fibreDirections(directions)
        if p['twoDirections']: myJobDef.setFibreInputType('twoDirections')
    myNewJob = myJobDef.create()    
    if p['numCpus']>1: myNewJob.setValues(numCpus=p['numCpus'],numDomains=p['numCpus'],multiprocessingMode=THREADS)
    if p['saveCaeFile']:mdb.saveAs(myNewJob.name)
    #-------------------------------------------------------
    return myNewJob,mdb
##################################################################################

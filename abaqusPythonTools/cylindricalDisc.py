# -*- coding: mbcs -*-
"""
caeTools
"""
## classical python modules
import math
## my abaqus module
import abaqusTools
import genericIVDCreation
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
    param['nbLamellae'] = 2
    param['nbCut'] = [2,2]
    param['innerRadius'] = 12.#mm
    param['outerRadius'] = 20.#mm
    param['height'] = 12.#mm
    #MATERIAL
    param['matType'] = 'neoHooke'#'Holzapfel' or 'neoHooke' or 'Yeoh'
    param['holzapfelParameters'] = (0.022, 9.09e-4, 23.92, 1045.7, 0.)#ovine anterior
    '''
    holzapfelParameters: C10,D,k1,k2,kappa (MPa, MPa-1,MPa,-,-)
        D: bulk modulus, K=2/D, K=2200MPa (considering compressibility equivalent to that of water)
        ==========
        HUMAN DATA
        ==========
        k1,k2 Holzapfel fit fiber Stretch/PK2 in MPa [C10 equivalent for initial fibre stretch only!)
          Holzapfel_2005
          coef1 - dorsalExternal1  k1,k2 = 1.9317   77.1463 r^2 = 0.9988 rms = 2.70%
                  equivalent (GM + fibres) E = 5.9315 MPa (see matlabScripts/modelFit/plotFullStress)
                  equivalent (GM + fibres) nu = 0.4996 (0.5-E/6K)
                  equivalent (fibres) C10 = 0.9762 MPa (see matlabScripts/modelFit/plotFullStress)
          coef2 - dorsalExternal2  k1,k2 = 2.4136   72.8267 r^2 = 0.9960 rms = 4.68%
                  equivalent (GM + fibres) E = 7.3585 MPa
                  equivalent (GM + fibres) nu = 0.4994
                  equivalent (fibres) C10 = 1.2142 MPa (see matlabScripts/modelFit/plotFullStress)
          coef3 - dorsalInternal1  k1,k2 = 0.2115   13.0878 r^2 = 0.9962 rms = 2.91%
                  equivalent (GM + fibres) E = 0.6748 MPa
                  equivalent (GM + fibres) nu = 0.4999
                  equivalent (fibres) C10 = 0.0998 MPa (see matlabScripts/modelFit/plotFullStress)
          coef4 - dorsalInternal2  k1,k2 = 0.3259   11.0381 r^2 = 0.9943 rms = 3.57%
                  equivalent (GM + fibres) E = 0.9968 MPa
                  equivalent (GM + fibres) nu = 0.4999
                  equivalent (fibres) C10 = 0.1535 MPa (see matlabScripts/modelFit/plotFullStress)
          coef5 - vlExternal       k1,k2 = 8.2963  319.0410 r^2 = 0.9865 rms = 9.22%
                  equivalent (GM + fibres) E = 32.9071 MPa
                  equivalent (GM + fibres) nu = 0.4975
                  equivalent (fibres) C10 = 5.4810 MPa (see matlabScripts/modelFit/plotFullStress)
          coef6 - vlInternal1      k1,k2 = 1.4536   40.4437 r^2 = 0.9984 rms = 1.81%
                  equivalent (GM + fibres) E = 4.3129 MPa
                  equivalent (GM + fibres) nu = 0.4997
                  equivalent (fibres) C10 = 0.7063 MPa (see matlabScripts/modelFit/plotFullStress)
          coef7 - vlInternal2      k1,k2 = 0.8804   54.1728 r^2 = 0.9960 rms = 2.41%
                  equivalent (GM + fibres) E = 2.6799 MPa
                  equivalent (GM + fibres) nu = 0.4998
                  equivalent (fibres) C10 = 0.4340 MPa (see matlabScripts/modelFit/plotFullStress)
          coef8 - Eberlein_CM_2004 k1,k2 = 3.0000   45 (also used in PhD@ETH) 
                  equivalent (GM + fibres) E = 8.8627 MPa
                  equivalent (GM + fibres) nu = 0.4993
                  equivalent (fibres) C10 = 1.4651 MPa (see matlabScripts/modelFit/plotFullStress)
        kappa=0. for perfectly oriented; 1/3 for isotropic
        C10 linear fit ground matrix shear stress/shear strain (Little_JMBBM_2010) in MPa; - ovine data!!!
          fit at max apparent linear shear strain: 2*C10 = 0.0377 (r^2 = 0.9817)
        ==========
        OVINE DATA
        ==========
        Fit an holzapfel model on a markert model (see matlabScripts/modelFit/fromReutlingerFitToHolzapfelModel)
        Markert model from Reutlinger 2014 JMBBM
        anterior lumbar discs
        k1 = 23.92, k2 = 1045.7         
        C10 linear fit ground matrix shear stress/shear strain (Little_JMBBM_2010) in MPa;
          fit at max apparent linear shear strain: 2*C10 = 0.0377 (r^2 = 0.9817)
        ==========
        BOVINE DATA
        ==========
        Data used in Cortes 2012 BMM
        caudal bovine discs
        k1 = 2.46 +/- 3.06, k2 = 2.11 +/- 2.16
        C10 from ground matrix radial shear modulus (Jacobs 2011 JMBBM) in MPa;
          C10 = 0.0075
        '''
    param['fiberDirection'] = [math.pi/6.,math.pi/6.,-math.pi/6.,-math.pi/6.]#list of fibre angles in the (theta,z) plane
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
    try: param['maxInc'] = max(0.02,_p['initialInc']*2)
    except(KeyError):param['maxInc'] = max(0.02,param['initialInc']*2)
    try: param['minInc'] = min(1e-6,_p['initialInc']/1000)
    except(KeyError):param['minInc'] = min(1e-6,param['initialInc']/1000)
    #LOAD
    param['load'] = 'Pressure'
    param['loadMagnitude'] = 0.07 # [MPa] 12Rings --> area~700mm^2 --> force~50N
    try:param['displ'] = 0.1*_p['height']
    except(KeyError):param['displ'] = 0.1*param['height']
    param['internalPressure'] = None
    #NUCLEUS
    param['withNucleus'] = False
    param['compressiveModulus'] = 0.4# bovine caudal discs Perie et al JoB 2005 (Iatridis team)
    #PUNCH CUT
    param['punchCut'] = False
    param['punchCentre'] = (0,0,0)
    param['punchRadius'] = 11/2.
    #JOB
    param['modelName'] = 'defaultName'
    param['scratchDir'] = '.'
    param['numCpus'] = 8
    #
    param.update(_p)
    return param
#-----------------------------------------------------
def getDistanceBetweenCentres(centreA,centreB):
    dx = centreA[0]-centreB[0]
    dy = centreA[1]-centreB[1]
    dz = centreA[2]-centreB[2]
    distance = math.sqrt(dx*dx+dy*dy+dz*dz)
    return distance
#-----------------------------------------------------
def caeAnalysis(p):
    # check parameter consistency
    assert not (p['withNucleus'] and p['internalPressure']), "do not set internal pressure if nucleus is modelled"
    
    # MODEL
    myModel = mdb.Model(p['modelName'])
    abaqusTools.deleteDefaultModel()
    myAssembly = myModel.rootAssembly
    
    #check if creating annulusCut and NucleusCut makes sense (ie check if there is indeed a cut to make with the dimensions given)
    cutAnnulus = False
    cutNucleus = False
    if p['punchCut']:
        D = getDistanceBetweenCentres((0,0,0),p['punchCentre']) 
        if D<p['punchRadius']+p['innerRadius']:
            cutNucleus = True
            if D>p['punchRadius']-p['innerRadius']:
                cutAnnulus = True      
        
        if (cutAnnulus or cutNucleus):
            punch =  genericIVDCreation.CylNucleus(myModel)
            punch.setCentre(p['punchCentre'])
            punch.setRadius(p['punchRadius'])
            punch.setHeight(p['height'])
            punch.setName('punch')
            #punchInstance,punchPart = punch.create()
    
    annulus =  genericIVDCreation.CylAnnulus(myModel)
    annulus.setInnerRadius(p['innerRadius'])
    annulus.setOuterRadius(p['outerRadius'])
    annulus.setHeight(p['height'])
    annulus.setNbLamellae(p['nbLamellae'])
    annulus.setNbCuts(p['nbCut'])
    if p['matType'] != 'Holzapfel':
        annulus.setToIncompressible()#will use hybrid elements for almost incompressible material - check if can be used for Holzapfel
    if cutAnnulus:
        annulus.cutWithPunch(punch)
    annulusParts,cutAnnulusPart = annulus.create()

    matNames = list()
    directions = list()
    for cyl in range(p['nbLamellae']):
        thisPart = annulusParts[cyl]
        for arc in range(p['nbCut'][cyl]):
            sectionName = 'annulus%i_section%i'%(cyl,arc)
            domainNb = int(sum(p['nbCut'][0:cyl]))+arc
            if cutAnnulusPart[cyl][arc]:# if the lamella is completely severed then two points are needed to define the cells
                lamellarThickness = (p['outerRadius']-p['innerRadius'])/p['nbLamellae']
                r0 = p['innerRadius']+(p['outerRadius']-p['innerRadius'])/p['nbLamellae']*cyl
                alpha = 360./p['nbCut'][cyl]*(arc+1-0.01)*math.pi/180.
                middlePt = ((r0*math.cos(alpha),p['height']/2.,r0*math.sin(alpha)),)
                pickedCells2 = (thisPart.cells.findAt(middlePt),thisPart.cells.findAt((annulus.midPoint[domainNb],)))
            else: pickedCells2 = thisPart.cells.findAt((annulus.midPoint[domainNb],))
            # create material
            matName = 'annulus%i'%domainNb
            if isinstance(p['holzapfelParameters'],list) and len(p['holzapfelParameters']) == int(sum(p['nbCut'])):#there is one set of parameters per cut
                matParam = p['holzapfelParameters'][domainNb]
            elif len(p['holzapfelParameters']) == 5:
                matParam = p['holzapfelParameters']
            else: raise("parameter 'holzapfelParameters' of unknown type or wrong length")
            if p['matType'] == 'Holzapfel':
                if isinstance(p['fiberDirection'],list) and len(p['fiberDirection']) == int(sum(p['nbCut'])):
                    fibreAngle = p['fiberDirection'][domainNb]
                elif isinstance(p['fiberDirection'],float) and p['nbLamellae']<2:
                    fibreAngle = p['fiberDirection']
                else: raise Exception("parameter 'fiberDirection' of unknown type or wrong length")
                matNames.append(matName)
                directions.append((0.,math.cos(fibreAngle),math.sin(fibreAngle)))
            
            material = genericIVDCreation.annulusMaterial(matName,p['matType'],myModel)
            material.setMatParam(matParam)
            if p['nbLamellae']<2:material.setToTwoDirections()
            material.define()
            
            # coordinate system
            csysCyl = thisPart.DatumCsysByThreePoints(coordSysType=CYLINDRICAL,origin=(0.,0.,0.),point1=(1.,0.,0.),point2=(0.,0.,-1.))
            # assign material
            #abaqusTools.assignMaterialToPart(matName,thisPart,myModel,orientation=csysCyl)
            abaqusTools.assignMaterialToPartition(matName,thisPart,sectionName,pickedCells2,myModel,orientation=csysCyl)
            
    if p['withNucleus']:
        #geometry and mesh
        nucleus =  genericIVDCreation.CylNucleus(myModel,annulus.bottomFaces,annulus.topFaces)
        nucleus.setRadius(p['innerRadius'])
        nucleus.setHeight(p['height'])
        if cutNucleus:
            nucleus.cutWithPunch(punch)
        nucleusInstance,nucleusPart = nucleus.create()
        # material - compressive modulus H~2G (Neo-Hookean model of sig = H/2(lambda-1/lambda)) and C10=G/2  ==> C10 = H/4
        myMat = myModel.Material(name='nucleus')
        myMat.Hyperelastic(testData=OFF,table=((p['compressiveModulus']/4.,0.0),),materialType=ISOTROPIC,type=NEO_HOOKE,behaviorType=INCOMPRESSIBLE)
        abaqusTools.assignMaterialToPart('nucleus',nucleusPart,myModel)
        #nucleus/annulus connection (rough contact)
        innerAnnulus = tuple(annulus.innerFaces[i] for i in range(p['nbCut'][0]))
        outerNucleus = nucleusInstance.faces.findAt((nucleus.outerPoint,))
        masterSurface = myAssembly.Surface(name='innerAnnulus',side1Faces=innerAnnulus)
        slaveSurface = myAssembly.Surface(name='outerNucleus',side1Faces=outerNucleus)
        from interactions import Interactions
        inter = Interactions(myModel)
        inter.setMasterSlave(masterSurface,slaveSurface)
        inter.setName('annulusNucleusInterface')
        inter.setFrictionBehaviour('Rough')
        inter.setNormalStiffness(1e8)
        inter.createInteraction()

        topFace = nucleus.topFaces
        bottomFace = nucleus.bottomFaces
    else:    
        topFace = annulus.topFaces
        bottomFace = annulus.bottomFaces
        
    ## SETS FOR OUTPUT ANALYSIS
    myAssembly.Set(faces=tuple(topFace), name='topFaces')
    myAssembly.Set(faces=tuple(bottomFace), name='bottomFaces')
        
    if p['nbLamellae']>1:
        ##CONSTRAINTS - same for all interfaces!!
        for nb in range(1,p['nbLamellae']):
            domainNb = int(sum(p['nbCut'][0:nb]))
            outerFaces = tuple(annulus.outerFaces[domainNb-i-1] for i in range(p['nbCut'][nb-1]))
            if any(cutAnnulusPart[cyl]):outerFaces2 = tuple(annulus.outerFaces2[domainNb-i-1] for i in range(p['nbCut'][nb-1]))
            innerFaces = tuple(annulus.innerFaces[domainNb+i] for i in range(p['nbCut'][nb]))
            if any(cutAnnulusPart[cyl]):masterSurface = myAssembly.Surface(name='master%d'%(nb),side1Faces=(outerFaces,outerFaces2))
            else:masterSurface = myAssembly.Surface(name='master%d'%(nb),side1Faces=outerFaces)
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
    myModel.steps['Load'].control.setValues(allowPropagation=OFF, resetDefaultValues=OFF, discontinuous=ON, timeIncrementation=(8, 10, 9., 16., 10.0, 4., 12., 10.0, 5., 3., 50.0))
    #I0=8(nb equ ite - cannot change if discontinuous ON),Ir=10 (nb conseq equ ite - cannot change if discontinuous ON),Ip=9,Ic=16,Il=10,Ig=4,Is=12,Ia=5,Ij=5,It=3,Isc=50
    myModel.steps['Load'].solverControl.setValues(allowPropagation=OFF, resetDefaultValues=OFF, maxIterations=10)
	
    ##LOAD/BC - after step as the step names are used!!!
    myTopSurface = myAssembly.Surface(name='topSurface',side1Faces=topFace)
    cylSys = myAssembly.DatumCsysByThreePoints(name='cylC',coordSysType=CYLINDRICAL, origin=(0,0,0),\
    point1=(1.0, 0.0, 0), point2=(0.0, 0.0, -1.0) )
    datumCyl = myAssembly.datums[cylSys.id]
    if p['load'] =='Pressure':#default !! magnitude provided = PRESSURE
        myModel.Pressure(name='Pressure',createStepName='Load',region=myTopSurface,magnitude=p['loadMagnitude'],
        distributionType=UNIFORM)
        myModel.PinnedBC(name='Fixed',createStepName='Load',region=tuple(bottomFace))
    elif p['load'] == 'Pressure_total': #!!magnitude provided = total INITIAL FORCE, when the area varies -> force = magnitude*area1/area0!!
        myModel.Pressure(name='Pressure',createStepName='Load',region=myTopSurface,magnitude=p['loadMagnitude'],
        distributionType=TOTAL_FORCE)
        myModel.PinnedBC(name='Fixed',createStepName='Load',region=tuple(bottomFace))
    elif p['load'] == 'vertDispl':
        myModel.DisplacementBC(name='Displ',createStepName='Load',region=tuple(topFace),u1=0.,u2=0.,u3=-p['displ'], localCsys=datumCyl)
        myModel.PinnedBC(name='Fixed',createStepName='Load',region=tuple(bottomFace))
    elif p['load'] == 'PressurePlane':# magnitude provided = concentrated FORCE on the rigid plane
        import regionToolset
        p['outerRadius'] = p['outerRadius']
        surf = myModel.ConstrainedSketch(name='surf', sheetSize=200.0)
        surf.Line(point1=(0.0, p['outerRadius']), point2=(0.0, -p['outerRadius']))
        surfPart = myModel.Part(name='crushingPart', dimensionality=THREE_D, type=ANALYTIC_RIGID_SURFACE)
        surfPart.AnalyticRigidSurfExtrude(sketch=surf, depth=2.*p['outerRadius'])
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
        myModel.DisplacementBC(name='noRadialDispl',createStepName='Load',region=tuple(topFace),u1=0.,u2=0.,localCsys=datumCyl)
        myModel.PinnedBC(name='Fixed',createStepName='Load',region=tuple(bottomFace))
    else:#load only in internal pressure
        if p['internalPressure']:
            myModel.XsymmBC(name='FixedTop',createStepName='Load',region=tuple(topFace),localCsys=datumCyl)
            myModel.XsymmBC(name='Fixed',createStepName='Load',region=tuple(bottomFace),localCsys=datumCyl)
        else: raise Exception("no BC's have been defined!!")
    if p['internalPressure']:
        myInnerSurface = myAssembly.Surface(name='innerSurface',side1Faces=tuple(annulus.innerFaces[i] for i in range(p['nbCut'][0])))
        myModel.Pressure(name='intPressure',createStepName='Load',region=myInnerSurface,magnitude=p['internalPressure'],
        distributionType=UNIFORM)
    	
    ## OUTPUT REQUESTS
    #fieldVariable = ('S', 'LE', 'U', 'RT', 'P', 'CSTRESS', 'CDISP', 'CFORCE')
    #myModel.fieldOutputRequests['F-Output-1'].setValues(variables=fieldVariable)
    
    ## JOB
    from jobCreation import JobDefinition
    myJobDef = JobDefinition(p['modelName'])
    myJobDef.setScratchDir(p['scratchDir'])
    if p['matType'] == 'Holzapfel':
        myJobDef.setToFibrous()        
        myJobDef.fibreDirections(directions)
        myJobDef.setFibreInputType('partition')
        myJobDef.setMatNames(matNames)
        if p['nbLamellae']<2:myJobDef.setPartitionTwoDirections()
    myNewJob = myJobDef.create()
    if p['numCpus']>1:
        myNewJob.setValues(numCpus=p['numCpus'],numDomains=p['numCpus'],multiprocessingMode=THREADS)
    myNewJob.setValues(memory=3, memoryUnits=GIGA_BYTES)
    mdb.saveAs(myNewJob.name)
    #-------------------------------------------------------
    return myNewJob,mdb
##################################################################################

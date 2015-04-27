# -*- coding: mbcs -*-
## classical python modules
import math
from types import *
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
def createHollowCylinderPart(center,innerRadius,outerRadius,height,name,model,angle=360):
    from abaqusConstants import THREE_D,DEFORMABLE_BODY
    myCercle = model.ConstrainedSketch(name+'_sketch',sheetSize=250.)
    #hollow cylinder = rectangle revolution
    myCercle.rectangle((center[0]+innerRadius,center[1]),(center[0]+outerRadius,center[1]+height))
    myCercle.ConstructionLine((0.,0.),(0.,1.))#revolution axis
    myCylinder = model.Part(name+'_part',dimensionality=THREE_D,type=DEFORMABLE_BODY)
    myCylinder.BaseSolidRevolve(myCercle,angle)
    return myCylinder
#-----------------------------------------------------
def setElementType(eleTypeString):
    from abaqusConstants import C3D8R,C3D8RH,ENHANCED 
    if eleTypeString=='C3D8RH': eleType = mesh.ElemType(C3D8RH, hourglassControl=ENHANCED)
    else:eleType = mesh.ElemType(C3D8R, hourglassControl=ENHANCED)
    return eleType   
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
def getDistanceBetweenCentres(centreA,centreB):
    dx = centreA[0]-centreB[0]
    dy = centreA[1]-centreB[1]
    dz = centreA[2]-centreB[2]
    distance = math.sqrt(dx*dx+dy*dy+dz*dz)
    return distance
#-----------------------------------------------------
class CylAnnulus:
    '''
    Class to define the geometry of a meshed cylindrical annulus with partitions to assign different properties around the circumference
    '''
    def __init__(self,abqModel,bottomFaces = list(),topFaces = list()):
        self.centre = (0.,0.,0.)
        self.innerRadius = 2.
        self.outerRadius = 3.
        self.discHeight = 2.
        self.NbLamellae = 1
        self.NbCuts = [1]
        self.isIncompressible = False        
        self.bottomFaces = bottomFaces
        self.topFaces = topFaces
        self.abqModel = abqModel
        self.punch = None

    def setCenter(self,centre):
        self.centre = centre
    def setInnerRadius(self,iRadius):
        self.innerRadius = iRadius
    def setOuterRadius(self,oRadius):
        self.outerRadius = oRadius
        assert (oRadius>self.innerRadius), "the outer radius, %d, has to be larger than the inner radius, %d"%(oRadius,self.iRadius)
    def setHeight(self,height):
        self.discHeight = height
    def setNbLamellae(self,nb):
        self.NbLamellae = nb
        assert type(nb) is IntType, "NbLamellae is not an integer: %r" % nb
        assert (nb >= 1), "NbLamellae needs to be a positive integer: %i" %nb
    def setNbCuts(self,cuts):
        self.NbCuts = cuts
    def setToIncompressible(self):
        self.isIncompressible = True
    def cutWithPunch(self,punchTool):
        self.punch = punchTool
        # try: self.abqModel.rootAssembly.instances[self.punch.name]
        # except: raise Exception('punch instance has not been defined to make cut')
        
    def create(self):
        # check parameter consistency
        assert (len(self.NbCuts) == self.NbLamellae), "nbCut is a list of number of cut for each lamellae, its length must be equal to NbLamellae!!"
        assert not any(360%i for i in self.NbCuts), "number of cuts per part must be a divider of 360!!"
        
        cutAnnulus = [[False]*self.NbCuts[n] for n in range(self.NbLamellae)]
        lamellarThickness = (self.outerRadius-self.innerRadius)/self.NbLamellae
        myAssembly = self.abqModel.rootAssembly
        if self.punch: punchInstance,punchPart = self.punch.create()
        self.innerFaces = list()
        self.innerFaces2 = list()
        self.outerFaces = list()
        self.outerFaces2 = list()
        self.midPoint = list()
        parts = list()
        for cyl in range(self.NbLamellae):
            #geometry
            angle = 360./self.NbCuts[cyl]
            cylinderName = 'annulus%d'%(cyl)
            r0 = self.innerRadius+lamellarThickness*cyl
            r1 = self.innerRadius+lamellarThickness*(cyl+1)
            cutLamella = False
            if self.punch:
                #check if creating annulusCut makes sense (ie check if there is indeed a cut to make with the dimensions given)
                D = getDistanceBetweenCentres((0,0,0),self.punch.centre)
                if D>r0-self.punch.radius:
                    cutLamella = True
            rm = (r1+r0)/2.
            thisPart = createHollowCylinderPart((0.,0.),r0,r1,self.discHeight,cylinderName,self.abqModel)
            bottomPoint = list()
            topPoint = list()
            outerPoint = list()
            outerPoint2 = list()
            middlePt2 = list()
            for arc in range(self.NbCuts[cyl]):
                alpha = angle*(arc+0.01)*math.pi/180
                alpha2 = angle*(arc+0.99)*math.pi/180
                middlePt = (r0*math.cos(alpha),self.discHeight/2.,r0*math.sin(alpha))
                middlePt2.append((r0*math.cos(alpha2),self.discHeight/2.,r0*math.sin(alpha2)))
                bottomPoint.append((rm*math.cos(alpha),0,rm*math.sin(alpha)))
                topPoint.append((rm*math.cos(alpha),self.discHeight,rm*math.sin(alpha)))
                self.midPoint.append(middlePt)
                outerPoint.append((r1*math.cos(alpha),self.discHeight/2,r1*math.sin(alpha)))
                outerPoint2.append((r1*math.cos(alpha2),self.discHeight/2,r1*math.sin(alpha2)))
                pt1 = thisPart.DatumPointByCoordinate(coords=(r0*math.cos(angle*(arc+1)*math.pi/180),0,r0*math.sin(angle*(arc+1)*math.pi/180)))
                pt2 = thisPart.DatumPointByCoordinate(coords=(r1*math.cos(angle*(arc+1)*math.pi/180),0,r1*math.sin(angle*(arc+1)*math.pi/180)))
                pt3 = thisPart.DatumPointByCoordinate(coords=(r1*math.cos(angle*(arc+1)*math.pi/180),self.discHeight,r1*math.sin(angle*(arc+1)*math.pi/180)))
                pt4 = thisPart.DatumPointByCoordinate(coords=(r0*math.cos(angle*(arc+1)*math.pi/180),self.discHeight,r0*math.sin(angle*(arc+1)*math.pi/180)))
                pickedCells = thisPart.cells.findAt((middlePt,))
                thisPart.PartitionCellByPatchNCorners(cell=pickedCells[0],cornerPoints=[thisPart.datums[pt1.id],
                thisPart.datums[pt2.id], thisPart.datums[pt3.id], thisPart.datums[pt4.id]])
                thisInstance = abaqusTools.createInstanceAndAddtoAssembly(thisPart,myAssembly,translate = self.centre)
                if cutLamella:
                    gamma = math.acos(self.punch.centre[0]/D)# angle locating the centre of the punch
                    beta = math.acos((r0*r0+D*D-self.punch.radius*self.punch.radius)/(2.*r0*D))# angle, from the centre of the punch to the intersection between punch and lamella
                    if (gamma+beta>alpha) and (gamma-beta>alpha): cutAnnulus[cyl][arc] = True
            if cutLamella:
                cutAnnulusName = 'cutAnnulus%d'%(cyl)
                thisInstance = myAssembly.InstanceFromBooleanCut(name=cutAnnulusName, instanceToBeCut=thisInstance, cuttingInstances=(punchInstance, ), originalInstances=SUPPRESS)
                myAssembly.makeIndependent(instances=(thisInstance, ))
                thisPart = self.abqModel.parts[cutAnnulusName]
                if self.NbLamellae>1:myAssembly.features[punchInstance.name].resume()

            ptMeshC = list()
            ptMeshW = list()
            for arc in range(self.NbCuts[cyl]):
                alpha = angle*(arc+0.01)*math.pi/180
                self.bottomFaces.append(thisInstance.faces.findAt((bottomPoint[arc],)))
                self.topFaces.append(thisInstance.faces.findAt((topPoint[arc],)))
                if cutLamella:
                    self.innerFaces2.append(thisInstance.faces.findAt((middlePt2[arc],)))
                    self.outerFaces2.append(thisInstance.faces.findAt((outerPoint2[arc],)))#outerPoint2[arc]
                else:
                    self.innerFaces2.append([])
                    self.outerFaces2.append([])#outerPoint2[arc]

                self.innerFaces.append(thisInstance.faces.findAt((self.midPoint[int(sum(self.NbCuts[0:cyl]))+arc],)))
                self.outerFaces.append(thisInstance.faces.findAt((outerPoint[arc],)))
                ptMeshC.append((r1*math.cos(alpha),0,r1*math.sin(alpha)))
                ptMeshC.append((r1*math.cos(alpha),self.discHeight,r1*math.sin(alpha)))
                ptMeshW.append((rm*math.cos(angle*arc*math.pi/180),0,rm*math.sin(angle*arc*math.pi/180)))
                ptMeshW.append((rm*math.cos(angle*arc*math.pi/180),self.discHeight,rm*math.sin(angle*arc*math.pi/180)))
            
            intEdge = thisInstance.edges.getSequenceFromMask(mask=('[#1 ]', ), )
            extEdge = thisInstance.edges.getSequenceFromMask(mask=('[#4 ]', ), )
            edge = list()
            ctrl = list()
            for n in range(2*self.NbCuts[cyl]):
                edge.append(thisInstance.edges.findAt((ptMeshW[n],)))
                ctrlValue = max(int(20/(self.NbLamellae)),3)
                ctrl.append(ctrlValue)#number of radial elements per lamellae
                edge.append(thisInstance.edges.findAt((ptMeshC[n],)))
                ctrlValue = int(100./self.NbCuts[cyl])#number of circumferential elements=100
                if self.punch:ctrlValue = int(ctrlValue/3)
                ctrl.append(ctrlValue)
            if self.isIncompressible:
                elemType=setElementType('C3D8RH')
            else:
                elemType=setElementType('C3D8R')

            abaqusTools.assignElemtypeAndMesh(thisInstance,myAssembly,elemType,control=ctrl,meshType='seedEdgeByNumber',edges=edge)
            ## SETS FOR OUTPUT ANALYSIS
            if cyl == 0:#one vertical edge on the most inner lamella
                intVerticalEdge = thisInstance.edges.getSequenceFromMask(mask=('[#1 ]', ), )
                myAssembly.Set(edges=intVerticalEdge, name='intVerticalSegment')
            if cyl == self.NbLamellae-1:#one vertical edge on the most outer lamella
                extVerticalEdge = thisInstance.edges.getSequenceFromMask(mask=('[#4 ]', ), )
                myAssembly.Set(edges=extVerticalEdge, name='extVerticalSegment')
            parts.append(thisPart)
        return parts,cutAnnulus

#-----------------------------------------------------
class CylNucleus:
    '''
    Class to define the geometry of a meshed cylindrical nucleus
    '''
    def __init__(self,abqModel,bottomFaces = list(),topFaces = list()):
        self.centre = (0.,0.,0.)
        self.radius = 2.
        self.discHeight = 2.
        self.isIncompressible = True
        self.bottomFaces = bottomFaces
        self.topFaces = topFaces
        self.abqModel = abqModel
        self.punch = None
        self.name = 'nucleus'
        
    def setCentre(self,centre):
        self.centre = centre
    def setRadius(self,radius):
        self.radius = radius
    def setHeight(self,height):
        self.discHeight = height
    def setToCompressible(self):
        self.isIncompressible = False
    def setName(self,name):
        self.name = name
    def cutWithPunch(self,punchTool):
        self.punch = punchTool
#        try: self.abqModel.rootAssembly.instances[self.punch.name]
#        except: raise Exception('punch instance has not been defined to make cut')

    def create(self):
        myAssembly = self.abqModel.rootAssembly
        #geometry
        rm = 0.95*self.radius
        thisPart = createHollowCylinderPart((0.,0.),0.,self.radius,self.discHeight,self.name,self.abqModel)
        bottomPoint = (rm*math.cos(math.pi),0,rm*math.sin(math.pi))
        topPoint = (rm*math.cos(math.pi),self.discHeight,rm*math.sin(math.pi))
        self.outerPoint = (self.radius*math.cos(math.pi),self.discHeight/2,self.radius*math.sin(math.pi))
        cutNucleus = False
        if self.punch:
            #check if creating annulusCut makes sense (ie check if there is indeed a cut to make with the dimensions given)
            D = getDistanceBetweenCentres((0,0,0),self.punch.centre) 
            if D<self.punch.radius+self.radius:
                cutNucleus = True  
                punchInstance,punchPart = self.punch.create()
        #instance and faces
        thisInstance = abaqusTools.createInstanceAndAddtoAssembly(thisPart,myAssembly,translate = self.centre)
        meshControl = 0.5
        if cutNucleus:
            thisInstance = myAssembly.InstanceFromBooleanCut(name='cutNucleus', instanceToBeCut=thisInstance, cuttingInstances=(punchInstance, ), originalInstances=SUPPRESS)
            myAssembly.makeIndependent(instances=(thisInstance, ))
            thisPart = self.abqModel.parts['cutNucleus']
            meshControl = 0.4
        self.bottomFaces.append(thisInstance.faces.findAt((bottomPoint,)))
        self.topFaces.append(thisInstance.faces.findAt((topPoint,)))
        #mesh
        if self.isIncompressible:
            elemType=setElementType('C3D8RH')
        else:
            elemType=setElementType('C3D8R')
        abaqusTools.assignElemtypeAndMesh(thisInstance,myAssembly,elemType,control=meshControl)
        return thisInstance,thisPart

#-----------------------------------------------------
class annulusMaterial:
    def __init__(self,matName,matType,model):
        self.matName = matName
        self.matType = matType
        self.abqModel = model
        self.matParam = (0.0189, 9.09e-4, 23.81/2., 1116.6, 0.)
        self.twoDirections = False
        
    def setMatParam(self,matParam):
        self.matParam = matParam
    def setToTwoDirections(self):
        self.twoDirections = True
    def define(self):
        myMat = self.abqModel.Material(name=self.matName)
        E,nu = getEandNu(self.matParam)
        if self.matType == 'Holzapfel':
            if self.matParam[1]==0.:# incompressible
                if self.twoDirections:
                    myMat.Hyperelastic(table=(self.matParam,),materialType=ANISOTROPIC,anisotropicType=HOLZAPFEL,behaviorType=INCOMPRESSIBLE,localDirections=2)
                else:
                    myMat.Hyperelastic(table=(self.matParam,),materialType=ANISOTROPIC,anisotropicType=HOLZAPFEL,behaviorType=INCOMPRESSIBLE,localDirections=1)
            else:
                if self.twoDirections:
                    myMat.Hyperelastic(table=(self.matParam,),materialType=ANISOTROPIC,anisotropicType=HOLZAPFEL,behaviorType=COMPRESSIBLE,localDirections=2)
                else:
                    myMat.Hyperelastic(table=(self.matParam,),materialType=ANISOTROPIC,anisotropicType=HOLZAPFEL,behaviorType=COMPRESSIBLE,localDirections=1)
        elif self.matType == 'Yeoh':
            if self.matParam[1]==0.:# incompressible
                myMat.Hyperelastic(testData=OFF, materialType=ISOTROPIC, type=YEOH, table=((E/(4*(1.+nu)), 23e-3, 0.024459, 0., 0., 0.), ),behaviorType=INCOMPRESSIBLE)
            else:
                myMat.Hyperelastic(testData=OFF, materialType=ISOTROPIC, type=YEOH, table=((E/(4*(1.+nu)), 23e-3, 0.024459, 6*(1-2.*nu)/E, 6*(1-2.*nu)/E, 6*(1-2.*nu)/E), ),behaviorType=COMPRESSIBLE)
        else:# neo Hookean
            if self.matParam[1]==0.:# incompressible
                myMat.Hyperelastic(testData=OFF,table=((E/(4*(1.+nu)),0.),),materialType=ISOTROPIC,type=NEO_HOOKE,behaviorType=INCOMPRESSIBLE)            
            else:
                myMat.Hyperelastic(testData=OFF,table=((E/(4*(1.+nu)),6*(1-2.*nu)/E),),materialType=ISOTROPIC,type=NEO_HOOKE,behaviorType=COMPRESSIBLE)            

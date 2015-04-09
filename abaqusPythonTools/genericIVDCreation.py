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
class CylAnnulus:
    '''
    Class to define the geometry of a meshed cylindrical annulus with partitions to assign different properties around the circumference
    '''
    def __init__(self,abqModel,bottomFaces = list(),topFaces = list()):
        self.centre = (0.,0.)
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
    def cutWithPunch(self,punchPart):
        self.punch = punchPart
        
    def create(self):
        # check parameter consistency
        assert (len(self.NbCuts) == self.NbLamellae), "nbCut is a list of number of cut for each lamellae, its length must be equal to NbLamellae!!"
        assert not any(360%i for i in self.NbCuts), "number of cuts per part must be a divider of 360!!"
        
        from abaqusConstants import CYLINDRICAL
        lamellarThickness = (self.outerRadius-self.innerRadius)/self.NbLamellae
        myAssembly = self.abqModel.rootAssembly

        self.innerFaces = list()
        self.outerFaces = list()
        self.midPoint = list()
        parts = list()
        for cyl in range(self.NbLamellae):
            #geometry
            angle = 360/self.NbCuts[cyl]
            cylinderName = 'annulus%d'%(cyl)
            r0 = self.innerRadius+lamellarThickness*cyl
            r1 = self.innerRadius+lamellarThickness*(cyl+1)
            rm = (r1+r0)/2.
            thisPart = createHollowCylinderPart(self.centre,r0,r1,self.discHeight,cylinderName,self.abqModel)
            bottomPoint = list()
            topPoint = list()
            outerPoint = list()
            for arc in range(self.NbCuts[cyl]):
                middlePt = (r0*math.cos(angle*(arc+.5)*math.pi/180),self.discHeight/2,r0*math.sin(angle*(arc+.5)*math.pi/180))
                bottomPoint.append((rm*math.cos(angle*(arc+.5)*math.pi/180),0,rm*math.sin(angle*(arc+.5)*math.pi/180)))
                topPoint.append((rm*math.cos(angle*(arc+.5)*math.pi/180),self.discHeight,rm*math.sin(angle*(arc+.5)*math.pi/180)))
                self.midPoint.append(middlePt)
                outerPoint.append((r1*math.cos(angle*(arc+.5)*math.pi/180),self.discHeight/2,r1*math.sin(angle*(arc+.5)*math.pi/180)))
                pt1 = thisPart.DatumPointByCoordinate(coords=(r0*math.cos(angle*(arc+1)*math.pi/180),0,r0*math.sin(angle*(arc+1)*math.pi/180)))
                pt2 = thisPart.DatumPointByCoordinate(coords=(r1*math.cos(angle*(arc+1)*math.pi/180),0,r1*math.sin(angle*(arc+1)*math.pi/180)))
                pt3 = thisPart.DatumPointByCoordinate(coords=(r1*math.cos(angle*(arc+1)*math.pi/180),self.discHeight,r1*math.sin(angle*(arc+1)*math.pi/180)))
                pt4 = thisPart.DatumPointByCoordinate(coords=(r0*math.cos(angle*(arc+1)*math.pi/180),self.discHeight,r0*math.sin(angle*(arc+1)*math.pi/180)))
                pickedCells = thisPart.cells.findAt((middlePt,))
                thisPart.PartitionCellByPatchNCorners(cell=pickedCells[0],cornerPoints=[thisPart.datums[pt1.id],
                thisPart.datums[pt2.id], thisPart.datums[pt3.id], thisPart.datums[pt4.id]])
            thisInstance = abaqusTools.createInstanceAndAddtoAssembly(thisPart,myAssembly)
            if self.punch:
                cuttingInstance = abaqusTools.createInstanceAndAddtoAssembly(self.punch,myAssembly)
                thisInstance = myAssembly.InstanceFromBooleanCut(name='cutNucleus', instanceToBeCut=thisInstance, cuttingInstances=(cuttingInstance, ), originalInstances=SUPPRESS)
            ptMeshC = list()
            ptMeshW = list()
            for arc in range(self.NbCuts[cyl]):
                self.bottomFaces.append(thisInstance.faces.findAt((bottomPoint[arc],)))
                self.topFaces.append(thisInstance.faces.findAt((topPoint[arc],)))
                self.innerFaces.append(thisInstance.faces.findAt((self.midPoint[int(sum(self.NbCuts[0:cyl]))+arc],)))
                self.outerFaces.append(thisInstance.faces.findAt((outerPoint[arc],)))
                ptMeshC.append((r1*math.cos(angle*(arc+.5)*math.pi/180),0,r1*math.sin(angle*(arc+.5)*math.pi/180)))
                ptMeshC.append((r1*math.cos(angle*(arc+.5)*math.pi/180),self.discHeight,r1*math.sin(angle*(arc+.5)*math.pi/180)))
                ptMeshW.append((rm*math.cos(angle*arc*math.pi/180),0,rm*math.sin(angle*arc*math.pi/180)))
                ptMeshW.append((rm*math.cos(angle*arc*math.pi/180),self.discHeight,rm*math.sin(angle*arc*math.pi/180)))
            
            intEdge = thisInstance.edges.getSequenceFromMask(mask=('[#1 ]', ), )
            extEdge = thisInstance.edges.getSequenceFromMask(mask=('[#4 ]', ), )
            edge = list()
            ctrl = list()
            for n in range(2*self.NbCuts[cyl]):
                edge.append(thisInstance.edges.findAt((ptMeshW[n],)))
                ctrl.append(max(int(20/(self.NbLamellae)),3))#number of radial elements per lamellae
                edge.append(thisInstance.edges.findAt((ptMeshC[n],)))
                ctrl.append(int(100./self.NbCuts[cyl]))#number of circumferential elements=80
            if self.isIncompressible:
                elemType=setElementType('C3D8RH')
            else:
                elemType=setElementType('C3D8R')
            abaqusTools.assignElemtypeAndMesh(thisInstance,myAssembly,elemType,control=ctrl,meshType='seedEdgeByNumber',edges=edge)
            ## SETS FOR OUTPUT ANALYSIS
            if cyl == 0:#one vertical edge on the most inner lamella
                intVerticalEdge = thisInstance.edges.getSequenceFromMask(mask=('[#1 ]', ), )
                myAssembly.Set(edges=intVerticalEdge, name='intVerticalSegment')
            if cyl == 0 or cyl == self.NbLamellae:#one vertical edge on the most outer lamella (which can be the most inner one when only one is defined!)
                extVerticalEdge = thisInstance.edges.getSequenceFromMask(mask=('[#4 ]', ), )
                myAssembly.Set(edges=extVerticalEdge, name='extVerticalSegment')
            parts.append(thisPart)
        return parts

#-----------------------------------------------------
class CylNucleus:
    '''
    Class to define the geometry of a meshed cylindrical nucleus
    '''
    def __init__(self,abqModel,bottomFaces = list(),topFaces = list()):
        self.centre = (0.,0.)
        self.radius = 2.
        self.discHeight = 2.
        self.isIncompressible = True
        self.bottomFaces = bottomFaces
        self.topFaces = topFaces
        self.abqModel = abqModel
        self.punch = None
        
    def setCenter(self,centre):
        self.centre = centre
    def setRadius(self,radius):
        self.radius = radius
    def setHeight(self,height):
        self.discHeight = height
    def setToCompressible(self):
        self.isIncompressible = False
    def cutWithPunch(self,punchPart):
        self.punch = punchPart

    def create(self):
        myAssembly = self.abqModel.rootAssembly
        #geometry
        rm = self.radius/2.
        thisPart = createHollowCylinderPart(self.centre,0.,self.radius,self.discHeight,'nucleus',self.abqModel)
        bottomPoint = (rm*math.cos(math.pi),0,rm*math.sin(math.pi))
        topPoint = (rm*math.cos(math.pi),self.discHeight,rm*math.sin(math.pi))
        self.outerPoint = (self.radius*math.cos(math.pi),self.discHeight/2,self.radius*math.sin(math.pi))
        #instance and faces
        thisInstance = abaqusTools.createInstanceAndAddtoAssembly(thisPart,myAssembly)
        if self.punch:
            cuttingInstance = abaqusTools.createInstanceAndAddtoAssembly(self.punch,myAssembly)
            thisInstance = myAssembly.InstanceFromBooleanCut(name='cutNucleus', instanceToBeCut=thisInstance, cuttingInstances=(cuttingInstance, ), originalInstances=SUPPRESS)

        self.bottomFaces.append(thisInstance.faces.findAt((bottomPoint,)))
        self.topFaces.append(thisInstance.faces.findAt((topPoint,)))
        #mesh
        if self.isIncompressible:
            elemType=setElementType('C3D8RH')
        else:
            elemType=setElementType('C3D8R')
        abaqusTools.assignElemtypeAndMesh(thisInstance,myAssembly,elemType,control=.5)
        return thisInstance,thisPart
#-----------------------------------------------------
class cylHole:
    '''
    Class to define the geometry of a cylinder punch
    '''
    def __init__(self,abqModel):
        self.centre = (0.,0.)
        self.radius = 2.
        self.height = 2.
        self.abqModel = abqModel
    def setCenter(self,centre):
        self.centre = centre
    def setRadius(self,radius):
        self.radius = radius
    def setHeight(self,height):
        self.height = height
    def create(self):
        #geometry
        thisPart = createHollowCylinderPart(self.centre,0.,self.radius,self.height,'hole',self.abqModel)
        return thisPart
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

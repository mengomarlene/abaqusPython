import abaqusPythonTools.extractors as ext
import abaqusPythonTools.valueExtractorClass as valueExtractor
import math
import numpy as np
import np.linalg as linalg
#
# !! only for quadrilateral meshes as ext.computeMeanOverElement assumes there are 4 nodes/IP
#
#-----------------------------------------------------
# LOCAL DIRECTIONS
#-----------------------------------------------------
def getFinalLD_1(odb,setName,sysC=None):
    values = valueExtractor.ValueExtractor(odb,setName)
    values.setField('LOCALDIR1')
    values.setComponant('LOCALDIR1_1')
    values.setCoordSystem(sysC)
    return values.getFinalValue_ElementNodal()
def getFinalLD_2(odb,setName,sysC=None):
    values = valueExtractor.ValueExtractor(odb,setName)
    values.setField('LOCALDIR1')
    values.setComponant('LOCALDIR1_2')
    values.setCoordSystem(sysC)
    return values.getFinalValue_ElementNodal()
def getFinalLD_3(odb,setName,sysC=None):
    values = valueExtractor.ValueExtractor(odb,setName)
    values.setField('LOCALDIR1')
    values.setComponant('LOCALDIR1_3')
    values.setCoordSystem(sysC)
    return values.getFinalValue_ElementNodal()
def getLD_1(odb,setName,sysC=None):
    values = valueExtractor.ValueExtractor(odb,setName)
    values.setField('LOCALDIR1')
    values.setComponant('LOCALDIR1_1')
    values.setCoordSystem(sysC)
    return values.getEvolution_ElementNodal()
def getLD_2(odb,setName,sysC=None):
    values = valueExtractor.ValueExtractor(odb,setName)
    values.setField('LOCALDIR1')
    values.setComponant('LOCALDIR1_2')
    values.setCoordSystem(sysC)
    return values.getEvolution_ElementNodal()
def getLD_3(odb,setName,sysC=None):
    values = valueExtractor.ValueExtractor(odb,setName)
    values.setField('LOCALDIR1')
    values.setComponant('LOCALDIR1_3')
    values.setCoordSystem(sysC)
    return values.getEvolution_ElementNodal()
#-----------------------------------------------------
def getFinalFiberDirection(odb,setName,sysC):
    LD1 = ext.computeMeanOverElement(getFinalLD_1(odb,setName,sysC))
    LD2 = ext.computeMeanOverElement(getFinalLD_2(odb,setName,sysC))
    LD3 = ext.computeMeanOverElement(getFinalLD_3(odb,setName,sysC))
    nbNodes = len(LD3)
    fiberDirectionVector = np.empty((3,nbNodes))
    fiberDirectionVector[0,:] = LD1
    fiberDirectionVector[1,:] = LD2
    fiberDirectionVector[2,:] = LD3
    return fiberDirectionVector
#-----------------------------------------------------
def getFinalLogStrain(odb,setName,sysC):
    E11 = ext.computeMeanOverElement(ext.getFinalE_11(odb,setName,sysC))
    E22 = ext.computeMeanOverElement(ext.getFinalE_22(odb,setName,sysC))
    E33 = ext.computeMeanOverElement(ext.getFinalE_33(odb,setName,sysC))
    E12 = ext.computeMeanOverElement(ext.getFinalE_12(odb,setName,sysC))
    E13 = ext.computeMeanOverElement(ext.getFinalE_13(odb,setName,sysC))
    E23 = ext.computeMeanOverElement(ext.getFinalE_23(odb,setName,sysC))
    nbNodes = len(E23)
    strainTensor = np.empty((3,3,nbNodes))
    strainTensor[0,0,] = E11
    strainTensor[1,1,] = E22
    strainTensor[2,2,] = E33
    strainTensor[0,1,] = E12
    strainTensor[0,2,] = E13
    strainTensor[1,2,] = E23
    strainTensor[1,0,] = E12
    strainTensor[2,0,] = E13
    strainTensor[2,1,] = E23
    return strainTensor
#-----------------------------------------------------
def getInvLeftCauchyGreen(strainTensorV):
    '''
    return B-1=V^-2 from V
    '''
    Bm1 = np.empty((3,3,int(strainTensorV.shape[2])))
    for node in range(int(strainTensorV.shape[2])):
        B = np.dot(strainTensorV[:,:,node],strainTensorV[:,:,node]) 
        Bm1[:,:,node] = linalg.inv(B)
    return Bm1
#-----------------------------------------------------
def getStrainV(logStrainV):
    '''
    return V from logV
    '''
    V = np.empty((3,3,int(logStrainV.shape[2])))
    for node in range(int(logStrainV.shape[2])):
        w,v = linalg.eig(logStrainV[:,:,node])
        ew = np.exp(w)
        V[:,:,node] = ew*np.inner(v,v)
    return V
#-----------------------------------------------------
#-----------------------------------------------------
def computeFiberStretch(odb,setName,sysC):
    direction = getFinalFiberDirection(odb,setName,sysC)#a vector (for each node)
    logVstrain = getFinalLogStrain(odb,setName,sysC)# a tensor (for each node)
    strainV = getStrainV(logVstrain)
    invLCG = getInvLeftCauchyGreen(strainV)
    stretch = list()
    for node in range(int(direction.shape[1])):
        invSquareStretch = np.dot(direction[:,node],np.dot(invLCG[:,:,node],direction[:,node]))
        stretch.append(math.sqrt(1./invSquareStretch))
    return stretch
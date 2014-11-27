import abaqusPythonTools.extractors as ext

#-----------------------------------------------------
def findCentreOfNodeSet(set):
    xMin = float("inf")
    yMin = float("inf")
    zMin = float("inf")
    xMax = -float("inf")
    yMax = -float("inf")
    zMax = -float("inf")
    for node in set.nodes[0]:
        coord = ext.getNodeCoord(node)
        if coord[0]<xMin:xMin=coord[0]
        elif coord[0]>xMax:xMax=coord[0]
        if coord[1]<yMin:yMin=coord[1]
        elif coord[1]>yMax:yMax=coord[1]
        if coord[2]<zMin:zMin=coord[2]
        elif coord[2]>zMax:zMax=coord[2]
    return ((xMin+xMax)/2.,(yMin+yMax)/2.,(zMin+zMax)/2.)
#-----------------------------------------------------
def createCylXYCoordSystem(assembly):
    from abaqusConstants import CYLINDRICAL
    return assembly.DatumCsysByThreePoints(name='cylXY',coordSysType=CYLINDRICAL, origin=(0,0,0),\
    point1=(1.0, 0.0, 0), point2=(0.0, 1.0, 0.0) )
#-----------------------------------------------------
def createCylXZCoordSystem(assembly):
    from abaqusConstants import CYLINDRICAL
    return assembly.DatumCsysByThreePoints(name='cylXZ',coordSysType=CYLINDRICAL, origin=(0,0,0),\
    point1=(1.0, 0.0, 0), point2=(0.0, 0.0, -1.0) )
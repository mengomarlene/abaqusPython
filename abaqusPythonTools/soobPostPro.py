import abaqusPythonTools.odbTools as odbTools
import abaqusPythonTools.extractors as ext
import os

def appliedDisplacementForceExtractor(odbName):
    keysToWrite = ['totalForce_pinnedFace','totalForce_movingFace','time']
    valuesToWrite = dict.fromkeys(keysToWrite, None)
    run = False
    for data in range(len(valuesToWrite)):
        file = valuesToWrite.keys()[data]+'.ascii'
        if (not os.path.isfile(file))\
        or (os.path.getmtime(file) < os.path.getmtime('exeCalls.txt'))\
        or (os.path.getmtime(file) < os.path.getmtime(__file__)):
            run = True
            break
    if run:
        print "running postPro on %s"%(odbName)
        myOdb = odbTools.openOdb(odbName)
        mySets =  myOdb.rootAssembly.nodeSets
        pinnedNodeSetName = list()
        movingNodeSetName = list()
        for nodeSet in mySets.keys():
            zMin = '_WITH_ZMIN'
            if nodeSet.endswith(zMin):pinnedNodeSetName.append(nodeSet)
            zMax = '_WITH_ZMAX'
            if nodeSet.endswith(zMax):movingNodeSetName.append(nodeSet)

        time = ext.getTime(myOdb)

        resultantForce_pin = [0]*len(time)
        for setName in pinnedNodeSetName:
            resForce = ext.getResF_3(myOdb,setName)
            for t in range(len(resultantForce_pin)):
                resultantForce_pin[t] += resForce[t]
        resultantForce_mov = [0]*len(time)
        for setName in movingNodeSetName:
            resForce = ext.getResF_3(myOdb,setName)
            for t in range(len(resultantForce_mov)):  
                resultantForce_mov[t] += resForce[t]

        valuesToWrite = dict(totalForce_pinnedFace=resultantForce_pin,totalForce_movingFace=resultantForce_mov,time=time)

        odbTools.writeValues(valuesToWrite)
        myOdb.close()

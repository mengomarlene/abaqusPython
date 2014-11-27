import abaqusPythonTools.odbTools as odbTools
import abaqusPythonTools.extractors as ext
import os
import abaqusPythonTools.geometricTools as geometricTools

def containedPressureExtractors(odbName):    
    keysToWrite = ['initCoord_intVerticalSegment','radialDisp_intVerticalSegment','axialDisp_intVerticalSegment',
    'tgtDisp_intVerticalSegment','initCoord_extVerticalSegment','radialDisp_extVerticalSegment','axialDisp_extVerticalSegment'
    'tgtDisp_extVerticalSegment','initCoord_topFace','axialDisp_topFace','tgtDisp_topFace','time']
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
        time = ext.getTime(myOdb)
        
        sysCyl = geometricTools.createCylXZCoordSystem(myOdb.rootAssembly)

        intInitCoord = ext.getNCoord(myOdb, 'intVerticalSegment', sysC=sysCyl)
        intRadialDispl = ext.getU_1(myOdb, 'intVerticalSegment', sysC=sysCyl)
        intAxialDispl = ext.getU_3(myOdb, 'intVerticalSegment', sysC=sysCyl)
        intTgtDispl = ext.getU_2(myOdb, 'intVerticalSegment', sysC=sysCyl)

        extInitCoord = ext.getNCoord(myOdb, 'extVerticalSegment', sysC=sysCyl)
        extRadialDispl = ext.getU_1(myOdb, 'extVerticalSegment', sysC=sysCyl)
        extAxialDispl = ext.getU_3(myOdb, 'extVerticalSegment', sysC=sysCyl)
        extTgtDispl = ext.getU_2(myOdb, 'extVerticalSegment', sysC=sysCyl)

        topInitCoord = ext.getNCoord(myOdb, 'topFaces', sysC=sysCyl)
        topAxialDispl = ext.getU_3(myOdb, 'topFaces', sysC=sysCyl)
        topTgtDispl = ext.getU_2(myOdb, 'topFaces', sysC=sysCyl)
        
        valuesToWrite = dict(initCoord_intVerticalSegment=intInitCoord, radialDisp_intVerticalSegment=intRadialDispl,
        axialDisp_intVerticalSegment=intAxialDispl,tgtDisp_intVerticalSegment=intTgtDispl,
        initCoord_extVerticalSegment=extInitCoord, radialDisp_extVerticalSegment=extRadialDispl,
        axialDisp_extVerticalSegment=extAxialDispl,tgtDisp_extVerticalSegment=extTgtDispl,
        initCoord_topFace=topInitCoord,axialDisp_topFace=topAxialDispl,tgtDisp_topFace=topTgtDispl,time=time)
     
        odbTools.writeValues(valuesToWrite)
        myOdb.close()

def containedDisplExtractors(odbName):    
    # keysToWrite = ['resForce_topFace','tgtDisp_topFace','time']
    keysToWrite = ['initCoord_intVerticalSegment','radialDisp_intVerticalSegment','axialDisp_intVerticalSegment',
    'tgtDisp_intVerticalSegment','initCoord_extVerticalSegment','radialDisp_extVerticalSegment','axialDisp_extVerticalSegment'
    'tgtDisp_extVerticalSegment','resForce_topFace','time']
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
        time = ext.getTime(myOdb)
        sysCyl = geometricTools.createCylXZCoordSystem(myOdb.rootAssembly)

        intInitCoord = ext.getNCoord(myOdb, 'intVerticalSegment', sysC=sysCyl)
        intRadialDispl = ext.getU_1(myOdb, 'intVerticalSegment', sysC=sysCyl)
        intAxialDispl = ext.getU_3(myOdb, 'intVerticalSegment', sysC=sysCyl)
        intTgtDispl = ext.getU_2(myOdb, 'intVerticalSegment', sysC=sysCyl)

        extInitCoord = ext.getNCoord(myOdb, 'extVerticalSegment', sysC=sysCyl)
        extRadialDispl = ext.getU_1(myOdb, 'extVerticalSegment', sysC=sysCyl)
        extAxialDispl = ext.getU_3(myOdb, 'extVerticalSegment', sysC=sysCyl)
        extTgtDispl = ext.getU_2(myOdb, 'extVerticalSegment', sysC=sysCyl)

        topResForce = ext.getResF_3(myOdb,'topFaces',sysC=sysCyl)
        
        # valuesToWrite = dict(resForce_topFace=topResForce,tgtDisp_topFace=topTgtDispl,time=time)
        valuesToWrite = dict(initCoord_intVerticalSegment=intInitCoord, radialDisp_intVerticalSegment=intRadialDispl,
        axialDisp_intVerticalSegment=intAxialDispl,tgtDisp_intVerticalSegment=intTgtDispl,
        initCoord_extVerticalSegment=extInitCoord, radialDisp_extVerticalSegment=extRadialDispl,
        axialDisp_extVerticalSegment=extAxialDispl,tgtDisp_extVerticalSegment=extTgtDispl,
        resForce_topFace=topResForce,time=time)
     
        odbTools.writeValues(valuesToWrite)
        myOdb.close()

def pressureExtractorsFromInp(odbName):
    keysToWrite = ['initCoord_AF','radialDisp_AF','axialDisp_AF','tgtDisp_AF',
    'initCoord_AF0','radialDisp_AF0','axialDisp_AF0','tgtDisp_AF0','time']
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
        time = ext.getTime(myOdb)
        
        myAssembly = myOdb.rootAssembly
        AFPartName = 'AF-1'
        AFInstance = myAssembly.instances[AFPartName] 
        sysCyl = geometricTools.createCylXZCoordSystem(myAssembly)
        
        extSet = 'extAxialSet'.upper()
        if extSet not in myAssembly.nodeSets.keys():
            import math
            nodes = AFInstance.nodes
            nodeList = list()
            for node in nodes:
                coord0 = node.coordinates
                R = math.sqrt(coord0[0]*coord0[0]+coord0[2]*coord0[2])
                theta = math.atan2(coord0[2],coord0[0])
                if (R > 23.9) and (-.02 < theta < .02 ):nodeList.append(node.label)
            myNodes = tuple(nodeList)
            myAssembly.NodeSetFromNodeLabels(name = extSet, nodeLabels = ((AFPartName,myNodes),)) 
        extInitCoord = ext.getNCoord(myOdb, extSet, sysC=sysCyl)
        extRadialDispl = ext.getU_1(myOdb, extSet, sysC=sysCyl)
        extAxialDispl = ext.getU_3(myOdb, extSet, sysC=sysCyl)
        extTgtDispl = ext.getU_2(myOdb, extSet, sysC=sysCyl)
        
        extSet0 = 'ext0AxialSet'.upper()
        if extSet0 not in myAssembly.nodeSets.keys():
            import math
            nodes = AFInstance.nodes
            nodeList = list()
            for node in nodes:
                coord0 = node.coordinates
                R = math.sqrt(coord0[0]*coord0[0]+coord0[2]*coord0[2])
                theta = math.atan2(coord0[2],coord0[0])
                if (R > 23.9) and (-.02+math.pi < theta < .02+math.pi ):nodeList.append(node.label)
            myNodes = tuple(nodeList)
            myAssembly.NodeSetFromNodeLabels(name = extSet0, nodeLabels = ((AFPartName,myNodes),)) 
        ext0InitCoord = ext.getNCoord(myOdb, extSet0, sysC=sysCyl)
        ext0RadialDispl = ext.getU_1(myOdb, extSet0, sysC=sysCyl)
        ext0AxialDispl = ext.getU_3(myOdb, extSet0, sysC=sysCyl)
        ext0TgtDispl = ext.getU_2(myOdb, extSet0, sysC=sysCyl)
              
        valuesToWrite = dict(initCoord_AF=extInitCoord,radialDisp_AF=extRadialDispl,
        axialDisp_AF=extAxialDispl,tgtDisp_AF=extTgtDispl,initCoord_AF0=ext0InitCoord,radialDisp_AF0=ext0RadialDispl,
        axialDisp_AF0=ext0AxialDispl,tgtDisp_AF0=ext0TgtDispl,time=time) 
        odbTools.writeValues(valuesToWrite)
        myOdb.close()
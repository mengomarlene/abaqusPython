odbToolbox = r"D:\myWork\procedures\postPro4Abq_VC"
import sys
sys.path.append(odbToolbox)
import postProTools.odbTools as odbTools
import postProTools.extractors as ext
import abaqusPythonTools.geometricTools as geoTools
import os

def getCylDatum(myOdb):
    from abaqusConstants import CYLINDRICAL
    mySets =  myOdb.rootAssembly.nodeSets
    for setName in mySets.keys():
        if setName.endswith('_WITH_YMIN') or setName.endswith('PLATE'):
            center = geoTools.findCentreOfNodeSet(mySets[setName.upper()])
            datum = myOdb.rootAssembly.DatumCsysByThreePoints(name='cylSystem', coordSysType=CYLINDRICAL, origin=center, point1=(center[0]+1.,center[1],center[2]), point2=(center[0],center[1]+1.,center[2]))
            return datum

def appliedDisplExtractorsHemiDisc(odbName):
    keysToWrite = ['time','topResForce','bottomResForce']
    keysToWrite.append('initCoord')
    keysToWrite.append('radialDisp')
    keysToWrite.append('axialDisp')
    keysToWrite.append('tgtDisp')
    valuesToWrite = dict.fromkeys(keysToWrite, None)
    
    run = False
    for data in valuesToWrite.keys():
        file = data+'.ascii'
        if (not os.path.isfile(file))\
        or (os.path.getmtime(file) < os.path.getmtime('exeCalls.txt'))\
        or (os.path.getmtime(file) < os.path.getmtime(__file__)):
            run = True
            break

    if run:
        print "running postPro on %s"%(odbName)
        myOdb = odbTools.openOdb(odbName)
        
        myAssembly = myOdb.rootAssembly
        #create node set from surface
        mainPart = myAssembly.instances['PART-1-1']
        extSetName = 'EXTERNALANNULUS'
        if extSetName not in myAssembly.nodeSets.keys():
            #try:
            mySurface = mainPart.surfaces[extSetName]
            nodeList = list()
            for e in mySurface.elements:
                nodeList.extend([nodeLbl for nodeLbl in e.connectivity if nodeLbl not in nodeList])
            myNodes = tuple(nodeList)
            extSet = myAssembly.NodeSetFromNodeLabels(name = extSetName, nodeLabels = (('PART-1-1',myNodes),)) 
        else:extSet=myAssembly.nodeSets[extSetName]
            #except:raise Exception('I run out of a try')

        cylSystem = getCylDatum(myOdb)
        valuesToWrite['time'] = ext.getTime(myOdb)
        valuesToWrite['topResForce'] = ext.getResF(myOdb,'ns_topEndPlate_with_zMax',sysC=cylSystem)
        valuesToWrite['bottomResForce'] = ext.getResF(myOdb,'ns_bottomEndPlate_with_zMin',sysC=cylSystem)

        valuesToWrite['initCoord'] = ext.getNCoord(myOdb, extSet, sysC=cylSystem)
        valuesToWrite['radialDisp'] = ext.getU_1(myOdb, extSet, sysC=cylSystem)
        valuesToWrite['tgtDisp'] = ext.getU_2(myOdb, extSet, sysC=cylSystem)
        valuesToWrite['axialDisp'] = ext.getU_3(myOdb, extSet, sysC=cylSystem)    

        odbTools.writeValues(valuesToWrite)
        myOdb.close()
        
def appliedDisplExtractors(odbName):
    keysToWrite = ['time','topResForce','bottomResForce']
    keysToWrite.append('initCoord')
    keysToWrite.append('radialDisp')
    keysToWrite.append('axialDisp')
    keysToWrite.append('tgtDisp')
    valuesToWrite = dict.fromkeys(keysToWrite, None)
    
    run = False
    for data in valuesToWrite.keys():
        file = data+'.ascii'
        if (not os.path.isfile(file))\
        or (os.path.getmtime(file) < os.path.getmtime('exeCalls.txt'))\
        or (os.path.getmtime(file) < os.path.getmtime(__file__)):
            run = True
            break

    if run:
        print "running postPro on %s"%(odbName)
        myOdb = odbTools.openOdb(odbName)
        
        myAssembly = myOdb.rootAssembly
        #create node set from surface
        mainPart = myAssembly.instances['PART-1-1']
        extSetName = 'EXTERNALANNULUS'
        if extSetName not in myAssembly.nodeSets.keys():
            mySurface = mainPart.surfaces[extSetName]
            nodeList = list()
            for e in mySurface.elements: nodeList.extend([nodeLbl for nodeLbl in e.connectivity if nodeLbl not in nodeList])
            myNodes = tuple(nodeList)
            extSet = myAssembly.NodeSetFromNodeLabels(name = extSetName, nodeLabels = (('PART-1-1',myNodes),)) 
        else:
            try:
                extSet=myAssembly.nodeSets[extSetName]
            except: raise Exception('FIND SURFACE')

        cylSystem = getCylDatum(myOdb)
        valuesToWrite['time'] = ext.getTime(myOdb)
        valuesToWrite['topResForce'] = ext.getResF(myOdb,'NS_TOPPLATE_WITH_BACKGROUND',sysC=cylSystem)
        valuesToWrite['bottomResForce'] = ext.getResF(myOdb,'NS_BOTTOMPLATE_WITH_BACKGROUND',sysC=cylSystem)

        valuesToWrite['initCoord'] = ext.getNCoord(myOdb, extSet, sysC=cylSystem)
        valuesToWrite['radialDisp'] = ext.getU_1(myOdb, extSet, sysC=cylSystem)
        valuesToWrite['tgtDisp'] = ext.getU_2(myOdb, extSet, sysC=cylSystem)
        valuesToWrite['axialDisp'] = ext.getU_3(myOdb, extSet, sysC=cylSystem)    

        odbTools.writeValues(valuesToWrite)
        myOdb.close()
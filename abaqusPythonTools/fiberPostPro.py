import abaqusPythonTools.odbTools as odbTools
import abaqusPythonTools.extractors as ext
import abaqusPythonTools.fiberExtractors as fExt
import os
import abaqusPythonTools.geometricTools as geometricTools

def fiberStretch(odbName):    
    keysToWrite = ['initCoord_intVerticalSegment','fiberStretch_intVerticalSegment',
    'initCoord_extVerticalSegment','fiberStretch_extVerticalSegment']
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
        sysCyl = geometricTools.cylXZCoordSystem(myOdb.rootAssembly)

        intInitCoord = ext.getNCoord(myOdb, 'intVerticalSegment', sysC=sysCyl)
        intFiberStretch = fExt.computeFiberStretch(myOdb, 'intVerticalSegment', sysC=sysCyl)

        extInitCoord = ext.getNCoord(myOdb, 'extVerticalSegment', sysC=sysCyl)
        extFiberStretch = fExt.computeFiberStretch(myOdb, 'extVerticalSegment', sysC=sysCyl)
       
        valuesToWrite = dict(initCoord_intVerticalSegment=intInitCoord,fiberStretch_intVerticalSegment=intFiberStretch,
        initCoord_extVerticalSegment=extInitCoord,fiberStretch_extVerticalSegment=extFiberStretch)
     
        odbTools.writeValues(valuesToWrite)
        myOdb.close()
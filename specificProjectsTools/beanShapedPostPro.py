odbToolbox = r"D:\myWork\procedures\postPro4Abq_VC"
import sys
sys.path.append(odbToolbox)
import postProTools.odbTools as odbTools
import postProTools.extractors as ext
import os
import abaqusPythonTools.geometricTools as geometricTools
    
def appliedPressureExtractors(odbName):    
    sets = ['edgeXMax','edgeXMaxInt','edgeXMin','edgeXMinInt','edgeYMax','edgeYMaxInt','edgeYMin','edgeYMinInt']
    keysToWrite = ['time','topAxialDispl']
    for set in sets:
        keysToWrite.append('initCoord_%s'%set)
        keysToWrite.append('radialDisp_%s'%set)
        keysToWrite.append('axialDisp_%s'%set)
        keysToWrite.append('tgtDisp_%s'%set)
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
        sysCyl = geometricTools.cylXYCoordSystem(myOdb.rootAssembly)
        valuesToWrite['time'] = ext.getTime(myOdb)
        valuesToWrite['topAxialDispl'] = ext.getU_3(myOdb, 'zMax', sysC=sysCyl)    
        for set in sets:
            valuesToWrite['initCoord_%s'%set] = ext.getNCoord(myOdb, set, sysC=sysCyl)
            valuesToWrite['radialDisp_%s'%set] = ext.getU_1(myOdb, set, sysC=sysCyl)
            valuesToWrite['tgtDisp_%s'%set] = ext.getU_2(myOdb, set, sysC=sysCyl)
            valuesToWrite['axialDisp_%s'%set] = ext.getU_3(myOdb, set, sysC=sysCyl)
            
        odbTools.writeValues(valuesToWrite)
        myOdb.close()

def appliedDisplExtractors(odbName):    
    sets = ['edgeXMax','edgeXMaxInt','edgeXMin','edgeXMinInt','edgeYMax','edgeYMaxInt','edgeYMin','edgeYMinInt']
    keysToWrite = ['time','topResForce','bottomResForce']
    for set in sets:
        keysToWrite.append('initCoord_%s'%set)
        keysToWrite.append('radialDisp_%s'%set)
        keysToWrite.append('axialDisp_%s'%set)
        keysToWrite.append('tgtDisp_%s'%set)
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
        sysCyl = geometricTools.cylXYCoordSystem(myOdb.rootAssembly)
        valuesToWrite['time'] = ext.getTime(myOdb)
        valuesToWrite['topResForce'] = ext.getResF(myOdb,'zMax',sysC=sysCyl)
        valuesToWrite['bottomResForce'] = ext.getResF(myOdb,'zMin',sysC=sysCyl)
        for set in sets:
            valuesToWrite['initCoord_%s'%set] = ext.getNCoord(myOdb, set, sysC=sysCyl)
            valuesToWrite['radialDisp_%s'%set] = ext.getU_1(myOdb, set, sysC=sysCyl)
            valuesToWrite['tgtDisp_%s'%set] = ext.getU_2(myOdb, set, sysC=sysCyl)
            valuesToWrite['axialDisp_%s'%set] = ext.getU_3(myOdb, set, sysC=sysCyl)    

        odbTools.writeValues(valuesToWrite)
        myOdb.close()

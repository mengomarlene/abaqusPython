import abaqusPythonTools.odbTools as odbTools
import abaqusPythonTools.extractors as ext
import os


def containedDisplExtractors(odbName):    
    keysToWrite = ['radialDisp_intFace','resForce_intFace','radialDisp_outFace','resForce_outFace','time']
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

        intRadialDispl = ext.getU_3(myOdb, 'innerFace')
        extRadialDispl = ext.getU_3(myOdb, 'outerFace')

        inResForce = ext.getResF(myOdb,'innerFace')
        outResForce = ext.getResF(myOdb,'outerFace')
        
        valuesToWrite = dict(radialDisp_intFace=intRadialDispl,radialDisp_outFace=extRadialDispl,resForce_intFace=inResForce,resForce_outFace=outResForce,time=time)
     
        odbTools.writeValues(valuesToWrite)
        myOdb.close()

def optiStiffnessExtractors(odbName):    

    print "running postPro on %s"%(odbName)
    myOdb = odbTools.openOdb(odbName)
    time = ext.getTime(myOdb)
    extDispl = ext.getU_3(myOdb, 'outerFace')
    extDiplsList = [displ[0] for displ in extDispl]
    outForce = ext.getRF_3(myOdb,'outerFace')
    extForceList = [force[0] for force in outForce]
    eMax = max(extDiplsList)
    import numpy as np
    extShort = np.linspace(0.,eMax,200)
    shortForce = np.interp(extShort, extDiplsList, extForceList)
    n0=5
    linearExt = extShort[n0:]
    linearLoad = shortForce[n0:]
    zI = np.polyfit(linearExt, linearLoad, 1)
    odbTools.writeValuesOpti(zI[0])
    myOdb.close()
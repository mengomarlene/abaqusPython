import abaqusPythonTools.odbTools as odbTools
import abaqusPythonTools.contactExtractors as cExt
import abaqusPythonTools.extractors as ext
import os
import numpy as np

def matrixStiffnessExtractor(odbName,param):
    keysToWrite = ['matrixStiffness']
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
        thisNb = param['nbParts']
        area = param['height']*param['width']
        lamThickness = param['length']/thisNb
        c10 = param['holzapfelParameters'][0]
        d = param['holzapfelParameters'][1]
        #elastic equivalent for the full material, initial fibre stiffness
        if d==0.: nu = 0.499
        else: nu = (3-2*c10*d)/(6+2*d*c10)
        E = 4*(1+nu)*c10

        myOdb = odbTools.openOdb(odbName)
        extDispl = ext.getFinalU_3(myOdb, 'outerFace')
        outForce = ext.getFinalResF_3(myOdb,'outerFace')
        masterName = 'MASTER1'
        slaveName = 'SLAVE1'
        copen = cExt.getFinalCOpening(myOdb,masterName,slaveName)
        totalCoheOpen = np.mean(copen)*(thisNb-1)
        matrixOpen = (max(extDispl)-totalCoheOpen)/thisNb
        matrixStiffness = [outForce/(area*matrixOpen),E/lamThickness]
        valuesToWrite = dict(matrixStiffness=matrixStiffness)    
        odbTools.writeValues(valuesToWrite)
        myOdb.close()

def contactStiffnessExtractors(odbName):    
    keysToWrite = ['contactStiffness']
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
        masterName = 'MASTER1'
        slaveName = 'SLAVE1'
        copen = cExt.getFinalCOpening(myOdb,masterName,slaveName)
        cpress = cExt.getFinalCPressure(myOdb,masterName,slaveName)
        contactStiffness = np.mean(cpress)/np.mean(copen)#[cpress[node]/copen[node] for node in range(len(copen))]
        valuesToWrite = dict(contactStiffness=contactStiffness)    
        odbTools.writeValues(valuesToWrite)
        myOdb.close()
    
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
    myOdb = odbTools.openOdb(odbName)
    time = ext.getTime(myOdb)
    extDispl = ext.getFinalU_3(myOdb, 'outerFace')
    outForce = ext.getFinalResF_3(myOdb,'outerFace')
    stiffness = 0.
    if abs(outForce)>1e-8 and abs(outForce)<1e8:stiffness=outForce/extDispl[0]
    odbTools.writeValuesOpti(stiffness)
    myOdb.close()

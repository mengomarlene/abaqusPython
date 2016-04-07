odbToolbox = r"D:\myWork\procedures\postPro4Abq_VC"
import sys
sys.path.append(odbToolbox)
import postProTools.odbTools as odbTools
import postProTools.extractors as ext
import postProTools.contactExtractors as cExt
import os
import numpy as np

def matrixStiffnessExtractor(odbName):
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
        myOdb = odbTools.openOdb(odbName)
        thisNb = len(myOdb.parts.keys())
        totalCoheOpen = 0
        slip1 = [0.]
        slip2 = [0.]
        for i in range(thisNb-1):
            masterName = 'MASTER%d'%(i+1)
            slaveName = 'SLAVE%d'%(i+1)
            masterSurface = myOdb.rootAssembly.surfaces[masterName]
            copen = cExt.getFinalCOpening(myOdb,masterName,slaveName)
            slip1.append(max(ext.getFinalU_1(myOdb,odbTools.getNodeSetFromSurface(myOdb,masterSurface))))
            slip2.append(max(ext.getFinalU_2(myOdb,odbTools.getNodeSetFromSurface(myOdb,masterSurface))))
            totalCoheOpen += max(copen)
        extDispl = np.mean(ext.getFinalU_3(myOdb,'outerFace'))
        surfStress13 = max(ext.getFinalS_13(myOdb,'outerFace'))
        surfStress23 = max(ext.getFinalS_23(myOdb,'outerFace'))
        surfStress33 = np.mean(ext.getFinalS_33(myOdb,'outerFace'))
        slip1.append(max(ext.getFinalU_1(myOdb,'outerFace')))
        slip2.append(max(ext.getFinalU_2(myOdb,'outerFace')))
        matrixOpen = (extDispl-totalCoheOpen)/thisNb#elongation of each part if it is uniform
        valuesToWrite = dict(matrixStiffness=[surfStress33/matrixOpen,surfStress13/max(np.diff(slip1)),surfStress23/max(np.diff(slip2))])    
        odbTools.writeValues(valuesToWrite)
        myOdb.close()
        
def stiffnessesExtractor(odbName):
    matrixStiffnessExtractor(odbName)
    contactStiffnessExtractors(odbName)
        
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
        cslip1 = cExt.getFinalCSlip1(myOdb,masterName,slaveName)
        cshear1 = cExt.getFinalCShearStress1(myOdb,masterName,slaveName)
        cslip2 = cExt.getFinalCSlip2(myOdb,masterName,slaveName)
        cshear2 = cExt.getFinalCShearStress2(myOdb,masterName,slaveName)
        contactStiffness = [-min(cpress)/max(copen),max(cshear1)/max(cslip1),max(cshear2)/max(cslip2)]#[-cpress[node]/copen[node] for node in range(len(copen))]#cpress negative in tension
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

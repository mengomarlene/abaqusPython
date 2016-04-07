odbToolbox = r"D:\myWork\procedures\postPro4Abq_VC"
import sys
sys.path.append(odbToolbox)
import postProTools.odbTools as odbTools
import postProTools.extractors as ext
import os    

def lamellarRectanglePressure(odbName):    
    keysToWrite = ['rightInitCoord','rightU1','rightU2','topInitCoord','topU1','topU2','botInitCoord','botU1','botU2','time']
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

        rightInitCoord = ext.getNCoord(myOdb, 'right')
        rightU1 = ext.getU_1(myOdb, 'right')
        rightU2 = ext.getU_2(myOdb, 'right')

        leftInitCoord = ext.getNCoord(myOdb, 'left')
        leftU1 = ext.getU_1(myOdb, 'left')
        leftU2 = ext.getU_2(myOdb, 'left')
        
        topInitCoord = ext.getNCoord(myOdb, 'top')
        topU1 = ext.getU_1(myOdb, 'top')
        topU2 = ext.getU_2(myOdb, 'top')
        
        botInitCoord = ext.getNCoord(myOdb, 'bottom')
        botU1 = ext.getU_1(myOdb, 'bottom')
        botU2 = ext.getU_2(myOdb, 'bottom')

        valuesToWrite = dict(rightInitCoord=rightInitCoord,rightU1=rightU1,rightU2=rightU2,
        leftInitCoord=leftInitCoord,leftU1=leftU1,leftU2=leftU2,
        topInitCoord=topInitCoord,topU1=topU1,topU2=topU2,
        botInitCoord=botInitCoord,botU1=botU1,botU2=botU2,
        time=time)
     
        odbTools.writeValues(valuesToWrite)
        myOdb.close()

def lamellarRectangleDisp(odbName):    
    keysToWrite = ['resForce','topInitCoord','topU1','topU2','botInitCoord','botU1','botU2','time']
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

        resForce = ext.getResF2D(myOdb,'left')
        resTopForce = ext.getResF2D(myOdb,'top')

        rightInitCoord = ext.getNCoord(myOdb, 'right')
        rightU1 = ext.getU_1(myOdb, 'right')
        rightU2 = ext.getU_2(myOdb, 'right')

        leftInitCoord = ext.getNCoord(myOdb, 'left')
        leftU1 = ext.getU_1(myOdb, 'left')
        leftU2 = ext.getU_2(myOdb, 'left')
        
        topInitCoord = ext.getNCoord(myOdb, 'top')
        topU1 = ext.getU_1(myOdb, 'top')
        topU2 = ext.getU_2(myOdb, 'top')
        
        botInitCoord = ext.getNCoord(myOdb, 'bottom')
        botU1 = ext.getU_1(myOdb, 'bottom')
        botU2 = ext.getU_2(myOdb, 'bottom')

        valuesToWrite = dict(rightInitCoord=rightInitCoord,rightU1=rightU1,rightU2=rightU2,
        leftInitCoord=leftInitCoord,leftU1=leftU1,leftU2=leftU2,
        resForce=resForce,resTopForce=resTopForce,
        topInitCoord=topInitCoord,topU1=topU1,topU2=topU2,
        botInitCoord=botInitCoord,botU1=botU1,botU2=botU2,
        time=time)
     
        odbTools.writeValues(valuesToWrite)
        myOdb.close()
        
def lamellarDispOpti(odbName):    
    print "running postPro on %s"%(odbName)
    myOdb = odbTools.openOdb(odbName)

    resForce = ext.getResF_1(myOdb,'left')
    time = ext.getTime(myOdb)
    
    odbTools.writeValuesOpti(zip(time,resForce))
    myOdb.close()

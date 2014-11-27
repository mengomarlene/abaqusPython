import abaqusPythonTools.odbTools as odbTools
import abaqusPythonTools.extractors as ext
import os    

def section5Disp(odbName):    
    keysToWrite = ['resForce','rightInitCoord','rightU1','rightU2','time']
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
        setName = 'INPLANE5_INSTANCE.SF_INPLANE5_WITH_SECTIONNED6'
        if '02' in odbName: setName = 'SECTIONED2_INSTANCE.SF_SECTIONED2_WITH_INPLANE1'
        print "running postPro on %s"%(odbName)
        myOdb = odbTools.openOdb(odbName)
        time = ext.getTime(myOdb)

        resForce = ext.getResF2D(myOdb,setName)

        rightInitCoord = ext.getNCoord(myOdb, setName)
        rightU1 = ext.getU_1(myOdb, setName)
        rightU2 = ext.getU_2(myOdb, setName)

        valuesToWrite = dict(rightInitCoord=rightInitCoord,rightU1=rightU1,rightU2=rightU2,
        resForce=resForce, time=time)
     
        odbTools.writeValues(valuesToWrite)
        myOdb.close()


def displ2OptiTt01(odbName):    
    print "running postPro on %s"%(odbName)
    import math
    myOdb = odbTools.openOdb(odbName)
    myAssembly = myOdb.rootAssembly
    # PRODUCE NODE SET ON THE NODES I EXTRACT COORDINATES FROM.
    newSet = 'extractedDisplacement'.upper()

    myInstances = [myAssembly.instances['SECTIONED3_INSTANCE'],myAssembly.instances['SECTIONED4_INSTANCE'],myAssembly.instances['SECTIONED5_INSTANCE'],
    myAssembly.instances['INPLANE3_INSTANCE'],myAssembly.instances['INPLANE4_INSTANCE']]
    #myInstances = [myAssembly.instances['SECTIONED2_INSTANCE'],myAssembly.instances['SECTIONED3_INSTANCE'],myAssembly.instances['SECTIONED4_INSTANCE'],myAssembly.instances['SECTIONED5_INSTANCE'],
    #myAssembly.instances['INPLANE1_INSTANCE'],myAssembly.instances['INPLANE3_INSTANCE'],myAssembly.instances['INPLANE4_INSTANCE']]#points     #points order (I,J,A,B,C,D,E,F,G,H)x2	    
    expPointsCoord = [[(0.606,1.0208),(0.6956,0.5452),(0.6975,0.10976)],[(0.7466,0.8459),(0.71216,0.4332),(0.7911,0.3266),(0.99157,0.1497)],[(1.1335,0.17328)],
    [(0.606,1.0208),(0.6956,0.5452),(0.6975,0.10976),(0.7466,0.8459),(0.71216,0.4332),(0.7911,0.3266),(0.99157,0.1497)],[(1.1335,0.17328)]]
#    expPointsCoord = [[(0.3802,0.0808),(0.2947,1.2368)],[(0.606,1.0208),(0.6956,0.5452),(0.6975,0.10976)],[(0.7466,0.8459),(0.71216,0.4332),(0.7911,0.3266),(0.99157,0.1497)],[(1.1335,0.17328)],
#    [(0.3802,0.0808),(0.2947,1.2368)],[(0.606,1.0208),(0.6956,0.5452),(0.6975,0.10976),(0.7466,0.8459),(0.71216,0.4332),(0.7911,0.3266),(0.99157,0.1497)],[(1.1335,0.17328)]]
    if newSet not in myAssembly.nodeSets.keys():
        nodeList = list()
        for i,instance in enumerate(myInstances):
            points = {}
            for node in instance.nodes:
                points[node.label] = list(node.coordinates)
            for ptNo in range(len(expPointsCoord[i])):
                shortList = list()
                for key, value in points.iteritems():
                    if (0.95*expPointsCoord[i][ptNo][0] < value[0] < 1.05*expPointsCoord[i][ptNo][0]) and (0.95*expPointsCoord[i][ptNo][1] < value[1] < 1.05*expPointsCoord[i][ptNo][1]):
                        shortList.append((instance.name.replace('instance','Geo'),(key,)))
                nodeList.append(shortList[0])
        myNodes = tuple(nodeList)
        myAssembly.NodeSetFromNodeLabels(name = newSet, nodeLabels = myNodes)
    displ = ext.getFinalU(myOdb,newSet)
    
    odbTools.writeValuesOpti(displ)
    myOdb.close()
    
def displ2OptiTt02(odbName):    
    print "running postPro on %s"%(odbName)
    import math
    myOdb = odbTools.openOdb(odbName)
    myAssembly = myOdb.rootAssembly
    # PRODUCE NODE SET ON THE NODES I EXTRACT COORDINATES FROM.
    newSet = 'extractedDisplacement'.upper()
    myInstances = [myAssembly.instances['SECTIONED2_INSTANCE'],myAssembly.instances['SECTIONED3_INSTANCE'],myAssembly.instances['SECTIONED4_INSTANCE'],
    myAssembly.instances['INPLANE2_INSTANCE'],myAssembly.instances['INPLANE3_INSTANCE'],myAssembly.instances['INPLANE4_INSTANCE']]  
    #points order ([J],[A,B,C,D],[E,F,G,H,I],[J,A,B],[G,H],[C,D,E,F,I])
    A = (0.501,1.693)
    B = (0.492,0.)
    C = (0.67,1.758)
    D = (0.727,0.)
    E = (0.798,1.795)
    F = (0.869,0.)
    G = (0.9,1.791)
    H = (0.894,0.)
    I = (0.890,0.812)
    J = (0.321,0.552)
    expPointsCoord = [[J],[A,B,C,D],[E,F,G,H,I],[J,A,B],[G,H],[C,D,E,F,I]]
    if newSet not in myAssembly.nodeSets.keys():
        nodeList = list()
        for ins,instance in enumerate(myInstances):
            points = {}
            for node in instance.nodes:
                points[node.label] = list(node.coordinates)
            for ptNo in range(len(expPointsCoord[ins])):
                shortList = list()
                for key, value in points.iteritems():
                    if (0.9*expPointsCoord[ins][ptNo][0] <= value[0] <= 1.1*expPointsCoord[ins][ptNo][0]) and (0.9*expPointsCoord[ins][ptNo][1] <= value[1] <= 1.1*expPointsCoord[ins][ptNo][1]):
                        shortList.append((instance.name.replace('instance','Geo'),(key,)))
                nodeList.append(shortList[0])
        myNodes = tuple(nodeList)
        myAssembly.NodeSetFromNodeLabels(name = newSet, nodeLabels = myNodes)
    displ = ext.getFinalU(myOdb,newSet)
    
    odbTools.writeValuesOpti(displ)
    myOdb.close()

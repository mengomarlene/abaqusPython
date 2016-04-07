# -*- coding: mbcs -*-
odbToolbox = r"D:\myWork\procedures\postPro4Abq_VC"
import sys
sys.path.append(odbToolbox)
import postProTools.odbTools as odbTools

def writeVtk(vtkFile,nodeCoord,eleConnection,eleType,cdata = None,pdata = None,cdataName=None,pdataName=None):
    nbNodes = len(nodeCoord)
    nbElements = len(eleConnection)
    with open(vtkFile, 'w') as file:
        file.write('# vtk DataFile Version 2.0\n')
        file.write('Reconstructed Abaqus Field Data\n')
        file.write('ASCII\n\n')
        file.write('DATASET UNSTRUCTURED_GRID\n')
        file.write('POINTS %i float\n' % (nbNodes))
        file.writelines(' '.join('%f'%(j) for j in i) + '\n' for i in nodeCoord)
        file.write('\nCELLS %i %i\n' % (nbElements, nbElements + sum(len(i) for i in eleConnection)))#tot nb ele, tot nb info
        file.writelines('%i '%(len(i))+' '.join('%i'%(j) for j in i) + '\n' for i in eleConnection)
        file.write('\nCELL_TYPES %i\n' % (nbElements))
        file.writelines("%i\n" % item  for item in eleType)
        if pdata:
            file.write('\nPOINT_DATA %i' % (nbNodes))
            file.write('\nSCALARS %s float 1\n'%pdataName)
            file.write('LOOKUP_TABLE default\n')
            file.writelines("%f\n" % item  for item in pdata)
        if cdata:
            file.write('\nCELL_DATA %i' % (nbElements))
            file.write('\nSCALARS %s float 1\n'%cdataName)
            file.write('LOOKUP_TABLE default\n')
            file.writelines("%f\n" % item  for item in cdata)
            
def dataField(odbFile,fieldName,notWantedParts=[],notWantedEleSets=[]):
    # Extract ABAQUS ODB into VTK unstructured grid data format
    nbNodes = 0
    nbElements = 0
    nodeCoord = list()
    eleConnection = list()
    cellType = list()
    cellField = list()
    # Open the odb
    myOdb = odbTools.openOdb(odbFile)
    stepName = myOdb.steps.keys()[-1]
    frames = myOdb.steps[stepName].frames
    theField = frames[-1].fieldOutputs['S'].getScalarField(invariant=fieldName)
    # Isolate the instances, get the number of nodes and elements
    for instanceName in myOdb.rootAssembly.instances.keys():
        if instanceName not in notWantedParts:
            myInstance = myOdb.rootAssembly.instances[instanceName]
            numNodes = len(myInstance.nodes)
            #Get the initial nodal coordinates
            initialCoords = list()
            nodes = myInstance.nodes
            for node in nodes:
                coord0 = node.coordinates
                initialCoords.append((coord0[0], coord0[1], coord0[2]))
            #Isolate the displacement field
            displacements = frames[-1].fieldOutputs['U'].getSubset(region=myInstance).values
            #Add displacements to the initial coordinates
            for nd in range(numNodes):
               x = initialCoords[nd][0]+displacements[nd].data[0]
               y = initialCoords[nd][1]+displacements[nd].data[1]
               z = initialCoords[nd][2]+displacements[nd].data[2]
               nodeCoord.append((x, y, z))
            print "read %d nodes coordinates"%(numNodes)
            offset = nbNodes
            for setName in [myInstance.elementSets.keys(),' ALL ELEMENTS']:
                if setName not in notWantedEleSets:
                    elSet = myInstance.elementSets[setName]
                    numElements = 0
                    for el in elSet.elements:
                        ##Get the element connectivity
                        print el.faces
                        connectivity = el.connectivity
                        eleConnection.append([offset-1+i for i in connectivity])
                        if len(connectivity) == 8:  cellType.append(12)
                        elif len(connectivity) == 4:  cellType.append(10)
                        else: raise Exception('unknown element %d of connectivity %d'%(el.label,len(connectivity)))
                        ##Isolate the field
                        theElField = theField.getSubset(region=el).values
                        cellField.append(theElField[0].data)
                        numElements += 1
                    print "read %d element connexion and scalar field"%(numElements)
                    nbElements += numElements
            nbNodes += numNodes
    myOdb.close()
    return nodeCoord,eleConnection,cellType,cellField
    
def materialField(odbFile,notWantedParts=[],notWantedEleSets=[]):
    # Extract ABAQUS ODB into VTK unstructured grid data format
    nbNodes = 0
    nbElements = 0
    nodeCoord = list()
    eleConnection = list()
    cellType = list()
    cellField = list()
    # Open the odb
    myOdb = odbTools.openOdb(odbFile)
    stepName = myOdb.steps.keys()[-1]
    frames = myOdb.steps[stepName].frames
    # Isolate the instances, get the number of nodes and elements
    for instanceName in myOdb.rootAssembly.instances.keys():
        if instanceName not in notWantedParts:
            myInstance = myOdb.rootAssembly.instances[instanceName]
            numNodes = len(myInstance.nodes)
            #Get the initial nodal coordinates
            initialCoords = list()
            nodes = myInstance.nodes
            for node in nodes:
                coord0 = node.coordinates
                initialCoords.append((coord0[0], coord0[1], coord0[2]))
            #Isolate the displacement field
            displacements = frames[-1].fieldOutputs['U'].getSubset(region=myInstance).values
            #Add displacements to the initial coordinates
            for nd in range(numNodes):
               x = initialCoords[nd][0]+displacements[nd].data[0]
               y = initialCoords[nd][1]+displacements[nd].data[1]
               z = initialCoords[nd][2]+displacements[nd].data[2]
               nodeCoord.append((x, y, z))
            print "read %d nodes coordinates"%(numNodes)
            offset = nbNodes
            for setName in myInstance.elementSets.keys():
                if setName not in notWantedEleSets:
                    elSet = myInstance.elementSets[setName]
                    sectionName = 'Section-ASSEMBLY_'+instanceName+'_'+setName #default scanIP Name
                    materialName = myOdb.sections[sectionName].material
                    young = myOdb.materials[materialName].elastic.table[0][0]
                    numElements = 0
                    for el in elSet.elements:
                        ##Get the element connectivity
                        connectivity = el.connectivity
                        eleConnection.append([offset-1+i for i in connectivity])
                        if len(connectivity) == 8:  cellType.append(12)
                        elif len(connectivity) == 4:  cellType.append(10)
                        else: raise Exception('unknown element %d of connectivity %d'%(el.label,len(connectivity)))
                        ##Isolate the field
                        cellField.append(young)
                        numElements += 1
                    print "read %d element connexion and young's modulus"%(numElements)
                    nbElements += numElements
            nbNodes += numNodes
    myOdb.close()
    return nodeCoord,eleConnection,cellType,cellField
    
def dataVMField(odbFile,notWantedParts=[],notWantedEleSets=[]):
    from abaqusConstants import MISES
    return dataField(odbFile,MISES,notWantedParts,notWantedEleSets) 

def dataPField(odbFile,notWantedParts=[],notWantedEleSets=[]):
    from abaqusConstants import PRESS
    return dataField(odbFile,PRESS,notWantedParts,notWantedEleSets)

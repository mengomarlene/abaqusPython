from abaqus import mdb

class JobDefinition:
    def __init__(self,modelName):
        self.name = modelName
        self.scratch = '.'
        self.isFibrous = False
        self.fibreInputType = 'default'
        self.directions = None
        self.matNames = None
        self.twoDirections = False
        
    def setScratchDir(self,scratch):
        self.scratch = scratch
    def setToFibrous(self):
        self.isFibrous = True
    def setFibreInputType(self,type='default'):
        self.fibreInputType = type
    def setPartitionTwoDirections(self):
        self.twoDirections = True
    def fibreDirections(self,directions):
        self.directions = directions
    def setMatNames(self,matNames):
        self.matNames = matNames
    
    def create(self):
        from abaqusConstants import OFF,PERCENTAGE
        myJob = mdb.Job(model=self.name, name=self.name)
        myJob.writeInput(consistencyChecking=OFF)
        if self.isFibrous:
            #################################################################################
            # LONG WAY TO INTRODUCE LOCAL DIRECTIONS... WAITING TO FIND SOMETHING BETTER!!!##
            # -write inp file, modify it to add fiber orientation, run job on new inp file-##
            #################################################################################
            if self.fibreInputType == 'fromSip':
                inputFile = introduceFiberDirectionFromSipFile(self.matNames,self.directions,self.name)
            elif self.fibreInputType == 'partition':
                inputFile = introduceFiberDirectionPartition(self.matNames,self.directions,self.name,self.twoDirections)
            elif self.fibreInputType == 'twoDirections':
                inputFile = introduceTwoFiberDirections(self.directions,self.name)
            elif self.fibreInputType == 'twoDirectionsZVert':
                inputFile = introduceTwoFiberDirectionsZVert(self.directions,self.name)
            else:
                inputFile = introduceFiberDirection(self.directions,self.name)
            newJobName = self.name+'FibresIn'
            ## !! cannot create newModel with newInputfile and newJob on newModel as ModelFromInputFile does NOT keep fibre orientation
            ## ==> this is probably going to be a problem to do a restart if needed...
            myNewJob = mdb.JobFromInputFile(newJobName,inputFileName=inputFile)
        else:
            myNewJob = myJob
        myNewJob.setValues(getMemoryFromAnalysis=True, memory=60, memoryUnits=PERCENTAGE, scratch=self.scratch)
        return myNewJob
#-----------------------------------------------------
def introduceTwoFiberDirectionsZVert(fiberDirections,jobName):
    #ok only if input file for which the orientation is cae built
    """
    inputs :
    *one orientation
    *the original inp file name (jobName)
    output : name of new inp file
    """
    print "reading inp file - start"
    inpFile = open(jobName+'.inp', 'r')
    lines = inpFile.readlines()
    inpFile.close()
    orientationLine = list()#gives the lines of the *ORIENTATION key
    for i,line in enumerate(lines):
        if line.startswith('*Orientation'):
            orientationLine.append(i)
    print "reading inp file - done"
    print "writing inp file - start"
    for mat,lineNb in enumerate(orientationLine):   
        oldLine = lines[lineNb]
        newLine = oldLine[0:-1]+',local directions=2\n'
        lines[lineNb] = newLine
        lines[lineNb+2] += '%f,%f,%f\n'%(fiberDirections[mat][0],fiberDirections[mat][1],fiberDirections[mat][2])
        lines[lineNb+2] += '%f,%f,%f\n'%(-fiberDirections[mat][0],fiberDirections[mat][1],fiberDirections[mat][2])
    newInputFileName = jobName+'FibresIn.inp'
    newInpFile = open(newInputFileName, 'w')
    newInpFile.writelines(lines)
    newInpFile.close()
    print "writing inp file - done"
    return newInputFileName
#-----------------------------------------------------
def introduceTwoFiberDirections(fiberDirections,jobName):
    #ok only if input file for which the orientation is cae built
    """
    inputs :
    *one orientation
    *the original inp file name (jobName)
    output : name of new inp file
    """
    print "reading inp file - start"
    inpFile = open(jobName+'.inp', 'r')
    lines = inpFile.readlines()
    inpFile.close()
    orientationLine = list()#gives the lines of the *ORIENTATION key
    for i,line in enumerate(lines):
        if line.startswith('*Orientation'):
            orientationLine.append(i)
    print "reading inp file - done"
    print "writing inp file - start"
    for mat,lineNb in enumerate(orientationLine):   
        oldLine = lines[lineNb]
        newLine = oldLine[0:-1]+',local directions=2\n'
        lines[lineNb] = newLine
        lines[lineNb+2] += '%f,%f,%f\n'%(fiberDirections[mat][0],fiberDirections[mat][1],fiberDirections[mat][2])
        lines[lineNb+2] += '%f,%f,%f\n'%(fiberDirections[mat][0],fiberDirections[mat][1],-fiberDirections[mat][2])
    newInputFileName = jobName+'FibresIn.inp'
    newInpFile = open(newInputFileName, 'w')
    newInpFile.writelines(lines)
    newInpFile.close()
    print "writing inp file - done"
    return newInputFileName
#-----------------------------------------------------
def introduceFiberDirection(fiberDirections,jobName):
    #ok only if input file for which the orientation is cae built
    """
    inputs :
    *a list of orientations (assuming only one orientation of fiber but can easily be extended). 
    !!!! ASSUMES the orientations are written in the same order the materials are !!!
    *the original inp file name (jobName)
    output : name of new inp file
    """
    print "reading inp file - start"
    inpFile = open(jobName+'.inp', 'r')
    lines = inpFile.readlines()
    inpFile.close()
    orientationLine = list()#gives the lines of the *ORIENTATION key
    for i,line in enumerate(lines):
        if line.startswith('*Orientation'):
            orientationLine.append(i)
    print "reading inp file - done"
    print "writing inp file - start"
    for mat,lineNb in enumerate(orientationLine):   
        oldLine = lines[lineNb]
        newLine = oldLine[0:-1]+',local directions=1\n'
        lines[lineNb] = newLine
        lines[lineNb+2] += '%f,%f,%f\n'%(fiberDirections[mat][0],fiberDirections[mat][1],fiberDirections[mat][2])
    newInputFileName = jobName+'FibresIn.inp'
    newInpFile = open(newInputFileName, 'w')
    newInpFile.writelines(lines)
    newInpFile.close()
    print "writing inp file - done"
    return newInputFileName
#-----------------------------------------------------
def introduceFiberDirectionPartition(materialNames,fiberDirections,jobName,twoDirections=False):
    #ok only if input file for which the orientation is cae built
    """
    inputs :
    *a list of  the names given to the *MATERIAL keys for which fiber orientation are needed
    (that's a way to find the name of the *ORIENTATION key that need to be changed as there is no
    way while writting your inp file with abaqus python to choose a name for this keys)
    *the corresponding orientations (assuming only one orientation of fiber but can easily be extended).
    *the original inp file name (jobName)
    output : name of new inp file
    """
    print "reading inp file - start"
    inpFile = open(jobName+'.inp', 'r')
    lines = inpFile.readlines()
    inpFile.close()
    solidSectionLine = list()
    for i,line in enumerate(lines):
        if (line.startswith('*Solid Section')):
            solidSectionLine.append(i)
    print "reading inp file - done"
    print "writing inp file - start"
    for mat in range(len(materialNames)):
        idx = -1-mat
        for lineNb in solidSectionLine:	
            oldLine = lines[lineNb-4]#this is why the comment at the beginning of the function exists...
            if (materialNames[idx] in lines[lineNb]) and (not oldLine.endswith(',local directions=1\n')):
                if twoDirections:
                    newLine = oldLine[0:-1]+',local directions=2\n'
                    lines[lineNb-4] = newLine
                    lines[lineNb-2] += '%f,%f,%f\n'%(fiberDirections[mat][0],fiberDirections[mat][1],fiberDirections[mat][2])
                    lines[lineNb-2] += '%f,%f,%f\n'%(fiberDirections[mat][0],fiberDirections[mat][1],-fiberDirections[mat][2])
                else:
                    newLine = oldLine[0:-1]+',local directions=1\n'
                    lines[lineNb-4] = newLine
                    lines[lineNb-2] += '%f,%f,%f\n'%(fiberDirections[idx][0],fiberDirections[idx][1],fiberDirections[idx][2])
    newInputFileName = jobName+'FibresIn.inp'
    newInpFile = open(newInputFileName, 'w')
    newInpFile.writelines(lines)
    newInpFile.close()
    print "writing inp file - done"
    return newInputFileName
#-----------------------------------------------------
def introduceFiberDirectionFromSipFile(materialNames,fiberDirections,jobName):
    #NOT ok if orientation is cae built!!
    """
    inputs :
    *a list of  the names given to the *MATERIAL keys for which fiber orientation are needed
    *the corresponding orientations (assuming only one orientation of fiber but could easily be extended).
    *the original inp file name (jobName)
    output : name of new inp file
    """
    print "reading inp file - start"
    inpFile = open(jobName+'.inp', 'r')
    lines = inpFile.readlines()
    inpFile.close()
    matList = list()
    orientList = list()
    oriDefList = list()
    oriLineList = list()
    oriLineAndMatList = list()
    for lineNb,line in enumerate(lines):
        if (line.startswith('*Shell Section')) or (line.startswith('*Solid Section')):
            if 'orientation' in line:
                lineInfo=line.split(',')[1:]
                for info in lineInfo:
                    if 'material' in info: 
                        matList.append(info.split('=')[-1].strip())#strip removes whitespace and end of line charachters
                    elif 'orientation' in info: 
                        orientList.append(info.split('=')[-1].strip())
        elif (line.startswith('*Orientation')):
            lineInfo=line.split(',')[1:]
            for info in lineInfo:
                if 'name' in info: 
                    oriDefList.append(info.split('=')[-1].strip())
                    oriLineList.append(lineNb)
    print "writing inp file - start"
    for oriIdx,oriDefLine in enumerate(oriLineList):
        idx=orientList.index(oriDefList[oriIdx])
        oriLineAndMatList.append((oriDefLine,matList[idx].strip()))
    from operator import itemgetter
    listOfOriLineMatCouples = sorted(oriLineAndMatList,key=itemgetter(0), reverse=True)#sort list of line and mat in reverse order
    for oriLineMatCouple in listOfOriLineMatCouples:
        idxMat = materialNames.index(oriLineMatCouple[1])
        oldLine = lines[oriLineMatCouple[0]]
        newLine = oldLine[0:-1]+',local directions=1\n'
        lines[oriLineMatCouple[0]] = newLine
        lines[oriLineMatCouple[0]+2] += '%f,%f,%f\n'%(fiberDirections[idxMat][0],fiberDirections[idxMat][1],fiberDirections[idxMat][2])
    newInputFileName = jobName+'FibresIn.inp'
    newInpFile = open(newInputFileName, 'w')
    newInpFile.writelines(lines)
    newInpFile.close()
    print "writing inp file - done"
    return newInputFileName
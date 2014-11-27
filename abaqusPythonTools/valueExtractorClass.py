#import odbAccess

class ValueExtractor:
    """Class ValueExtractor - extract odb values on a set
    ValueExtractor(odb,set)#set can be a string or a set object
    Methods:
        setField(fieldKey) - the field to extract, default is displacement
        setComponent(componentLabel) - the field component, no default
        setInvariant(invariant) - the field invariant, no default
        setCoordSystem(sysC) - a coordinate system (sysC is a datum) in which the field is extracted, default is cartesian

        getEvolution_Nodal()
        getEvolution_ElementNodal()
        getEvolution_ElementIP()
        getFinalValue_Nodal()
        getFinalValue_ElementNodal()
        getFinalValue_ElementIP()
    """
    def __init__(self,odb,setName):
        self.odb = odb
        self.setName = setName#either a string or a set object
        self.fieldKey = 'U'
        self.componentLabel = None
        self.invariant = None
        self.sysC = None
        self.stepName = None
    #-----------------------------------------------------
    def setField(self,fieldKey):
        self.fieldKey = fieldKey
    def setComponent(self,componentLabel):
        self.componentLabel = componentLabel
    def setInvariant(self,invariant):
        self.invariant = invariant
    def setCoordSystem(self,sysC):
        self.sysC = sysC#a datum 
    def setStepName(self,stepName):
        self.stepName = stepName#a datum 
    #-----------------------------------------------------
    def getEvolution_Nodal(self):
        return self.__getEvolution()
    def getEvolution_ElementNodal(self):
        return self.__getEvolution(position='EL_N')
    def getEvolution_ElementIP(self):
        return self.__getEvolution(position='EL_IP')
    def getFinalValue_Nodal(self):
        return self.__getFinalValue()
    def getFinalValue_ElementNodal(self):
        return self.__getFinalValue(position='EL_N')
    def getFinalValue_ElementIP(self):
        return self.__getFinalValue(position='EL_IP')
    #-----------------------------------------------------
    #-----------------------------------------------------
    def __getEvolution(self,position=None):
        if self.stepName is None:self.stepName = self.odb.steps.keys()[-1]
        frames = self.odb.steps[self.stepName].frames
        values = self.__getValues(frameNo=frames,position=position)
        value = list()
        for frame in range(len(frames)):
            try: value.append([ptValue.data for ptValue in values[frame]])
            except: value.append([data for data in values[frame]])
        return value
    #-----------------------------------------------------
    def __getFinalValue(self,position=None):
        if self.stepName is None:self.stepName = self.odb.steps.keys()[-1]
        values = self.__getValues(position=position)
        return values
    #-----------------------------------------------------
    def __getValues(self,frameNo=-1,position=None):
        try:
           value = [self.__getValues(frameNb,position) for frameNb in range(len(frameNo))]
        except(TypeError):
            frame = self.odb.steps[self.stepName].frames[frameNo]#
            theField = frame.fieldOutputs[self.fieldKey]
            if self.sysC is not None:
                theField = theField.getTransformedField(datumCsys=self.sysC)
            if self.componentLabel is not None:theField = theField.getScalarField(componentLabel=self.componentLabel)
            elif self.invariant is not None:theField = theField.getScalarField(invariant=self.invariant)
            try:#setName is a string
                assembly = self.odb.rootAssembly
                if 'INSTANCE'  in self.setName:#set name is a part set
                    iName = self.setName.split('.')[0]
                    iSetName = self.setName.split('.')[1]
                    subset = assembly.instances[iName].nodeSets[iSetName.upper()]
                else:#set name is an assembly set
                    subset = assembly.nodeSets[self.setName.upper()]
            except(TypeError):#setName is a set object
                subset = self.setName
            if position == 'EL_IP':
                from abaqusConstants import INTEGRATION_POINT
                theFieldOnSet = theField.getSubset(region=subset,position=INTEGRATION_POINT)
                value = [ptValue.data for ptValue in theFieldOnSet.values]
            elif position == 'EL_N':
                from abaqusConstants import ELEMENT_NODAL
                theFieldOnSet = theField.getSubset(region=subset,position=ELEMENT_NODAL)
                value = [ptValue.data for ptValue in theFieldOnSet.values]
            else:# nodal field
                value = list()
                theFieldOnSet = theField.getSubset(region=subset)
                value = [ptValue.data for ptValue in theFieldOnSet.values]
                #if len(subset.nodes) >1: value = [ptValue.data for ptValue in theFieldOnSet.values]
                #else: value.append(theFieldOnSet.values[0].data)
        return value
class Interactions:
#HARD CONTACT AND NODE-TO-SURFACE METHOD DOES NOT CONVERGE!!!!!
#node-to-surface necessary for cohesive behavior
#--> use penalty method in all cases!!!
    def __init__(self,model):
        self.abqModel = model
        self.name = 'interface'
        self.master = None
        self.slave = None
        self.Tie = False
        self.allowSep = False
        self.normalStiffness = 10000.
        self.Friction = 'Frictionless'
        self.frictionCoef = 0.1
        self.Cohesive = False
        self.useCoheDefault = True
        self.cohePenalties = (100.0, 100.0, 100.0) #Knn, Kss, Ktt values if the default abaqus behaviour is not used
    
    def setMasterSlave(self,master,slave):
        self.master = master
        self.slave = slave
    
    def setName(self,iName):
        self.name = iName

    def setInteractionToTie(self):
        self.Tie = True
    
    def setNormalStiffness(self,stiffness):
        self.normalStiffness = stiffness
        
    def setSeparationAllowed(self):
        self.allowSep = True

    def setFrictionBehaviour(self,fBehaviour,fCoef=0.1):
        if fBehaviour not in ['Friction','Frictionless','Rough']: raise Exception("unkown friction behaviour - choose between 'Friction', or 'Frictionless', and 'Rough'")
        else: 
            self.Friction = fBehaviour
            self.frictionCoef = fCoef

    def setCohesiveBehaviour(self,useDefaultBehaviour=True,penalties=(1000.0, 1000.0, 1000.0)):
        self.Cohesive = True
        self.useCoheDefault = useDefaultBehaviour
        if not useDefaultBehaviour: self.cohePenalties = penalties

    def createInteraction(self):
        if not (self.master and self.slave): raise Exception('master and slave couples MUST be defined with the setMasterSlave function')
        from abaqusConstants import HARD,OFF,PENALTY,LINEAR,FRICTIONLESS,ROUGH,FRACTION,AUTOMATIC,SURFACE_TO_SURFACE,NODE_TO_SURFACE,FINITE,OMIT,OVERCLOSED
        if self.Tie: self.abqModel.Tie(name=self.name,master=self.master,slave=self.slave)
        else:
            iPropName = self.Friction
            if self.Cohesive:
                iPropName+='Cohe'
            try:
                self.abqModel.interactionProperties[iPropName]
            except:
                contact = self.abqModel.ContactProperty(iPropName)
                contact.NormalBehavior(pressureOverclosure=LINEAR, contactStiffness=10000.0,)
                #contact.NormalBehavior(pressureOverclosure=HARD, contactStiffness=self.normalStiffness, stiffnessBehavior=LINEAR, constraintEnforcementMethod=PENALTY)
                if self.Friction == 'Frictionless': contact.TangentialBehavior(formulation=FRICTIONLESS)
                elif self.Friction == 'Friction': contact.TangentialBehavior(formulation=PENALTY,table=((self.frictionCoef, ), ),maximumElasticSlip=FRACTION,fraction=0.005)
                elif self.Friction == 'Rough': contact.TangentialBehavior(formulation=ROUGH)
                if self.Cohesive:
                    if self.useCoheDefault: contact.CohesiveBehavior()
                    else: contact.CohesiveBehavior(defaultPenalties=OFF, table=(self.cohePenalties, ))
                #elif not self.allowSep: contact.normalBehavior.setValues(allowSeparation=OFF)
            if self.Cohesive:        
                self.abqModel.SurfaceToSurfaceContactStd(name=self.name,createStepName='Initial',master=self.master,slave=self.slave,sliding=FINITE, enforcement=NODE_TO_SURFACE, interactionProperty=iPropName, initialClearance=OMIT, adjustMethod=OVERCLOSED)
            else:
                self.abqModel.SurfaceToSurfaceContactStd(name=self.name,createStepName='Initial',master=self.master,slave=self.slave,sliding=FINITE,enforcement=SURFACE_TO_SURFACE, surfaceSmoothing=AUTOMATIC,interactionProperty=iPropName, initialClearance=OMIT, adjustMethod=OVERCLOSED)

    def changeInteraction(self):
        from abaqusConstants import OFF,HARD,PENALTY,LINEAR,FRICTIONLESS,ROUGH,FRACTION,SURFACE_TO_SURFACE,FINITE,NODE_TO_SURFACE,OMIT,OVERCLOSED
        if self.Tie:
            if not (self.master and self.slave): raise Exception('master and slave couples MUST be defined with the setMasterSlave function')
            else: self.abqModel.Tie(name=self.name,master=self.master,slave=self.slave)
        else:
            contact = self.abqModel.interactionProperties[self.name]
            contact.NormalBehavior(pressureOverclosure=LINEAR, contactStiffness=10000.0,)
            #contact.NormalBehavior(pressureOverclosure=HARD, contactStiffness=self.normalStiffness, stiffnessBehavior=LINEAR, constraintEnforcementMethod=PENALTY)
            if self.Friction == 'Frictionless':contact.TangentialBehavior(formulation=FRICTIONLESS)
            elif self.Friction == 'Friction': contact.TangentialBehavior(formulation=PENALTY,table=((self.frictionCoef, ), ),maximumElasticSlip=FRACTION,fraction=0.005)
            elif self.Friction == 'Rough': contact.TangentialBehavior(formulation=ROUGH)
            if self.Cohesive:
                self.abqModel.interactions[self.name+'-1'].setValues(sliding=FINITE, enforcement=NODE_TO_SURFACE)
                if self.useCoheDefault: contact.CohesiveBehavior()
                else: contact.CohesiveBehavior(defaultPenalties=OFF, table=(self.cohePenalties, ))
            else:
                #if not self.allowSep: contact.normalBehavior.setValues(allowSeparation=OFF)
                self.abqModel.interactions[self.name+'-1'].setValues(sliding=FINITE, enforcement=SURFACE_TO_SURFACE, initialClearance=OMIT, adjustMethod=OVERCLOSED)
            
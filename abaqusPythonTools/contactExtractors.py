import abaqusPythonTools.valueExtractorClass as valueExtractor
#fieldOutputs.keys = 
# 'CNORMF   ASSEMBLY_SLAVE1/ASSEMBLY_MASTER1', 'COPEN    ASSEMBLY_SLAVE1/ASSEMBLY_MASTER1',
# 'CPRESS   ASSEMBLY_SLAVE1/ASSEMBLY_MASTER1', 'CSHEAR1  ASSEMBLY_SLAVE1/ASSEMBLY_MASTER1', 
# 'CSHEAR2  ASSEMBLY_SLAVE1/ASSEMBLY_MASTER1', 'CSHEARF  ASSEMBLY_SLAVE1/ASSEMBLY_MASTER1', 
# 'CSLIP1   ASSEMBLY_SLAVE1/ASSEMBLY_MASTER1', 'CSLIP2   ASSEMBLY_SLAVE1/ASSEMBLY_MASTER1',
#-----------------------------------------------------
# COPEN
#-----------------------------------------------------
def getFinalCOpening(odb,masterName,slaveName):
    values = valueExtractor.ContactValueExtractor(odb,masterName,slaveName)
    return values.getFinalValue()
#-----------------------------------------------------
def getCOpening(odb,masterName,slaveName):
    values = valueExtractor.ContactValueExtractor(odb,masterName,slaveName)
    return values.getEvolution()
#-----------------------------------------------------
# CPRESS
#-----------------------------------------------------
def getFinalCPressure(odb,masterName,slaveName):
    values = valueExtractor.ContactValueExtractor(odb,masterName,slaveName)
    values.setField('CPRESS')
    return values.getFinalValue()
#-----------------------------------------------------
def getCPressure(odb,masterName,slaveName):
    values = valueExtractor.ContactValueExtractor(odb,masterName,slaveName)
    values.setField('CPRESS')
    return values.getEvolution()
#-----------------------------------------------------
# CNORMF -- not extracted by default for contact
#-----------------------------------------------------
def getFinalCNormalForce(odb,masterName,slaveName):
    values = valueExtractor.ContactValueExtractor(odb,masterName,slaveName)
    values.setField('CNORMF')
    return values.getFinalValue()
#-----------------------------------------------------
def getCNormalForce(odb,masterName,slaveName):
    values = valueExtractor.ContactValueExtractor(odb,masterName,slaveName)
    values.setField('CNORMF')
    return values.getEvolution()
#-----------------------------------------------------
# CSHEAR1
#-----------------------------------------------------
def getFinalCShearStress1(odb,masterName,slaveName):
    values = valueExtractor.ContactValueExtractor(odb,masterName,slaveName)
    values.setField('CSHEAR1')
    return values.getFinalValue()
#-----------------------------------------------------
def getCShearStress1(odb,masterName,slaveName):
    values = valueExtractor.ContactValueExtractor(odb,masterName,slaveName)
    values.setField('CSHEAR1')
    return values.getEvolution()
#-----------------------------------------------------
# CSHEAR2
#-----------------------------------------------------
def getFinalCShearStress2(odb,masterName,slaveName):
    values = valueExtractor.ContactValueExtractor(odb,masterName,slaveName)
    values.setField('CSHEAR2')
    return values.getFinalValue()
#-----------------------------------------------------
def getCShearStress2(odb,masterName,slaveName):
    values = valueExtractor.ContactValueExtractor(odb,masterName,slaveName)
    values.setField('CSHEAR2')
    return values.getEvolution()
#-----------------------------------------------------
# CSHEARF -- not extracted by default for contact
#-----------------------------------------------------
def getFinalCShearForce(odb,masterName,slaveName):
    values = valueExtractor.ContactValueExtractor(odb,masterName,slaveName)
    values.setField('CSHEARF')
    return values.getFinalValue()
#-----------------------------------------------------
def getCShearForce(odb,masterName,slaveName):
    values = valueExtractor.ContactValueExtractor(odb,masterName,slaveName)
    values.setField('CSHEARF')
    return values.getEvolution()
#-----------------------------------------------------
# CSLIP1
#-----------------------------------------------------
def getFinalCSlip1(odb,masterName,slaveName):
    values = valueExtractor.ContactValueExtractor(odb,masterName,slaveName)
    values.setField('CSLIP1')
    return values.getFinalValue()
#-----------------------------------------------------
def getCSlip1(odb,masterName,slaveName):
    values = valueExtractor.ContactValueExtractor(odb,masterName,slaveName)
    values.setField('CSLIP1')
    return values.getEvolution()
#-----------------------------------------------------
# CSLIP2
#-----------------------------------------------------
def getFinalCSlip2(odb,masterName,slaveName):
    values = valueExtractor.ContactValueExtractor(odb,masterName,slaveName)
    values.setField('CSLIP2')
    return values.getFinalValue()
#-----------------------------------------------------
def getCSlip2(odb,masterName,slaveName):
    values = valueExtractor.ContactValueExtractor(odb,masterName,slaveName)
    values.setField('CSLIP2')
    return values.getEvolution()

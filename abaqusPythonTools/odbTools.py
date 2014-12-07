
#-----------------------------------------------------
def openOdb(odbName):
    if not odbName.endswith('.odb'):odbName+='.odb'
    import odbAccess
    return odbAccess.openOdb(path=odbName)
#-----------------------------------------------------
def writeValuesOpti(valueList):
    import os
    datFile = open('output.ascii', 'w')
    try:
        for x,y in valueList:
            datFile.write( "%f %f\n" % (x,y) )
    except(TypeError): #there is shorter than that but can't be bothered!!!
        try:
            for value in valueList:
                datFile.write( "%f\n" % value)
        except(TypeError):datFile.write( "%f\n" % valueList)
    datFile.close()
#-----------------------------------------------------
def writeValues(listDict):
    import os
    for key in listDict.keys():
        datFile = open(key+'.ascii', 'w')
        try:
            for value in listDict[key]:
                try:
                    datFile.writelines( "%f " % item for item in value )
                    datFile.writelines( "\n" )
                except(TypeError):
                    datFile.writelines( "%f\n" % value ) 
        except(TypeError):
            value = listDict[key]
            try:
                datFile.writelines( "%f " % item for item in value )
                datFile.writelines( "\n" )
            except(TypeError):
                datFile.writelines( "%f\n" % value ) 
        datFile.close()


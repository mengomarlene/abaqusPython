"""
"""
# if called with runAbaqus.py: add the root directory to the abaqus search path
import sys
sys.path.append(sys.argv[-1])
import toolbox

def postPro(jobName):
    import abaqusPythonTools.beanShapedPostPro as beanShapedPostPro
    beanShapedPostPro.appliedDisplExtractors(jobName)

__modpath__ = toolbox.modulePath(postPro)

def getParameters(_p={}):
    import abaqusPythonTools.beanShaped as beanShaped
    param = {}
    param['modelName'] = toolbox.getFileName(__modpath__)
    param['interfaceType'] = 'CohesiveFriction' #'Frictionless', 'Friction'
    param['matType'] = 'Holzapfel'#or 'Holzapfel' or 'neoHooke'
    param.update(_p)
    return beanShaped.getParameters(param)

if __name__ == '__main__':
    import abaqusPythonTools.abaqusTools as abaqusTools
    import abaqusPythonTools.beanShaped as beanShaped
    job,mdb = beanShaped.createAnalysis(getParameters())
    #abaqusTools.runAnalysis(job)
    mdb.close()

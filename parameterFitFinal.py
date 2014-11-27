import os
import toolbox

verbose = False
saveIntermediateValues = True
NFeval = 0
NIter = 0

def computeFEData(p,modelScript):
    import subprocess
    #define worksapce
    baseName = os.path.dirname(os.path.abspath(__file__))
    workspace = toolbox.getWorkspace(modelScript,baseName)
    if not(os.path.isdir(workspace)):
        try:
            os.makedirs(workspace)
        except WindowsError:
            print("file(s) probably locked!\n")
    # run abaqus analysis (function of parameters p) in workspace
    os.chdir(workspace)
    if verbose: print "running abaqus cae on %s"%(toolbox.getFileName(modelScript))
    cmd = 'abaqus cae noGUI=%s'%(modelScript)
    paramString = ' '.join(map(str,p))
    cmd += ' -- %s %s > %s 2>&1'%(str(baseName),paramString,'exeCalls.txt')
    if verbose: print 'cmd= ',cmd
    pCall1 = subprocess.call(cmd, shell=True)
    # if pCall1:#the abaqus model has not terminated properly on not started at all for that matter
        # writeErrorFile(workspace,modelScript,p,pCall1)
        # raise Exception("!! something has gone wrong, check notRun.txt")
        # return 0
    # else:
    os.chdir(baseName)
    # run abaqus postPro -- this is the part where I did not find a way to work on a different workspace for each abaqus run
    cmd = 'abaqus python runAbaqus.py postPro %s'%(modelScript)
    pCall2 = subprocess.call(cmd, shell=True)
    if pCall2:#the post pro function has ot run properly
        writeErrorFile(workspace,modelScript,p,pCall1,pCall2)
        raise Exception("!! something has gone wrong, check notRun.txt")
        return 0
    else:
        # if the post-pro function has run, read the results in an array format
        feOutputFile = os.path.join(workspace,'output.ascii')
        with open(feOutputFile, 'r') as file:   
            output = zip(*(map(float,line.split()) for line in file))
        return output

def writeErrorFile(workspace,modelScript,p,pCall1,pCall2='not run yet'):
        feErrorFile = os.path.join(workspace,'notRun.txt')
        global NFeval
        with open(feErrorFile, 'w') as file:
            file.write('running abaqus cae on %s returned %s\n'%(toolbox.getFileName(modelScript), pCall1))
            file.write('running post pro on %s returned %s\n'%(toolbox.getFileName(modelScript), pCall2))
            file.write('parameter inputs: %s\n'%(p))
            file.write('run number: %s\n'%(NFeval))

def plotValues(fittedValues, modelScript, expData):
    baseName = os.path.dirname(os.path.abspath(__file__))
    workspace = toolbox.getWorkspace(modelScript,baseName)
    os.chdir(workspace)
    figFilePng = os.path.join(workspace,'fittedResults.png')
    figFilePdf = os.path.join(workspace,'fittedResults.pdf')
    import matplotlib.pyplot as plt
    plt.plot(expData[0],expData[1],'o',fittedValues[0],fittedValues[1],'x')
    plt.legend(['Data', 'Fit'])
    plt.title('Least-squares fit to data')
    plt.savefig(figFilePng, bbox_inches='tight')
    plt.savefig(figFilePdf, bbox_inches='tight')
    if not verbose:plt.show()
    return fittedValues

def plotIntermediateValues(feData, expData, no='final'):
    import matplotlib.pyplot as plt
    plt.figure()
    plt.plot(expData[0],expData[1],'o',feData[0],feData[1],'x')
    plt.legend(['Data', 'Fit'])
    plt.title('Least-squares fit to data - function evaluation nb %i'%no)
    plt.savefig('fit_%i.png'%no, bbox_inches='tight')
    plt.savefig('fit_%i.pdf'%no, bbox_inches='tight')

def saveValues(p, feData, value, no='final'):
    baseName = os.path.dirname(os.path.abspath(__file__))
    feDataFile = os.path.join(baseName,'verboseValues_%i.ascii'%no)
    with open(feDataFile, 'w') as file:
        file.write('run number: %s\n'%(no))
        file.write('parameter inputs: %s\n'%(p))
        file.write('least square error %s\n'%value)
        file.write('\n'.join('%f %f' % x for x in zip(*feData)))

def interpolateResults(data,xi):
    import scipy.interpolate as interpolate
    f = interpolate.interp1d(data[0],data[1])
    yi = f(xi)
    return yi

def residuals(p, modelScript, expData, withBounds=False):
    ''' residuals(p, expData) computes the diff (in a least square sense) between experimental data and FE data (function of p)
        p: set of parameters to optimize
        expData: experimental data to fit, should be a 2D array (x,y)
    '''
    # compute FE data function of parameters only - should return a 2D array (x,y) of floats
    # ---------------
    feData = computeFEData(p,modelScript)
    #
    import numpy as np
    #try to get next four lines in one with zip??
    diff = list()
    for n in range(len(feData)):
        for m in range(len(feData[n])):
            diff.append(expData[n][m] - feData[n][m])
    lstSq = 0
    for value in diff:
        lstSq+= value**2/(len(feData[0])*len(feData))
    global NFeval
    NFeval += 1
    if saveIntermediateValues: 
        saveValues(p, feData, lstSq, NFeval)
    if withBounds:
        return lstSq
    else:
        return np.resize(diff,len(p))

def callbackF(p):
    global NIter,NFeval
    NIter += 1
    if verbose:
        print 'Nb Iteration: %i, Nb Evaluation: %i, parameter inputs: %s\n'%(NIter,NFeval,p)
    baseName = os.path.dirname(os.path.abspath(__file__))
    callbackFile = os.path.join(baseName,'callbackValues_%i.ascii'%NIter)
    with open(callbackFile, 'w') as file:
        file.write('iteration number: %i\n'%(NIter))
        file.write('evaluation number: %i\n'%(NFeval))
        file.write('parameter inputs: %s\n'%(p))
    
def getOptiParam(p0, modelScript, expData, optiParam, pBounds=None):
    if pBounds is None:
        from scipy.optimize import leastsq
        pLSQ,covP,info,msg,ier = leastsq(residuals, p0, args=(modelScript, expData), full_output=True, maxfev=optiParam['maxEval'], epsfcn=optiParam['epsfcn'], ftol=optiParam['ftol'])
        if verbose: print msg
        fVal = info['fvec']
        d = {}
        d['funcalls']=info['nfev']
        d['nit'] = None
        d['grad'] = info['fjac']
        if ier in [1,2,3,4]:
            d['warnflag'] = 0
        else:
            d['warnflag'] = 2
        d['task']=msg
    else:
        from scipy.optimize import fmin_l_bfgs_b
        withBounds=True
        import numpy as np
        factorTol = optiParam['ftol']/np.finfo(float).eps
        pLSQ,fVal,d = fmin_l_bfgs_b(residuals, p0, args=(modelScript, expData, withBounds), approx_grad=True, bounds=pBounds, factr=factorTol, epsilon = optiParam['epsfcn'], disp=True, maxiter=optiParam['maxEval'],callback=callbackF)
        if verbose: print d
    return pLSQ,fVal,d

def main(p0, expData, modelScript, options={}, pBounds=None):
    optiParam = {}
    optiParam['maxEval']=10
    optiParam['epsfcn']=.1
    optiParam['ftol']=1e-8
    optiParam.update(options)
    return getOptiParam(p0, modelScript, expData, optiParam, pBounds)

if __name__ == "__main__":
    dir = os.path.join(os.getcwd(),'optimisation')
    dataFile = os.path.join(dir,'expData.ascii')
    feModel = os.path.join(dir,'rectangleOpti.py')
    p0 = [0.5,30.]
    #read data file
    with open(dataFile, 'r') as file:
        expData = zip(*(map(float,line.split()) for line in file))
    #run optimisation
    p,fVal,info = parameterFit.main(p0, expData, feModel)
    print p, info
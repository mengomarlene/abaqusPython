import parameterFit1Parr,toolbox
import os,sys
import shutil
sys.path.append(os.path.dirname(os.getcwd()))

mainDir = os.path.join(os.path.dirname(os.getcwd()),'Sami')
feModelDir = os.path.join(mainDir,'calibrationFilesOvine')
expDir = r'C:\Users\menmmen\Documents\othersWork\Sami_GSFactor_ovine\stiffnessData'

optiParam = {}
optiParam['maxEval'] = 20 # max number of function evaluation in the optimisation process !!there is more than one evalutation per iteration as the jacobian as to be computed!!
optiParam['epsfcn'] = .005 # step taken to compute the jacobian by a finite difference method
optiParam['ftol'] = 1e-6 # tolerance on the function value

bounds = (0.001,0.02)

#perform optimisation -- hex mesh
GSFactor,fVal,info = parameterFit1Parr.main(expDir, feModelDir, pBounds=bounds, options=optiParam)
Nfev = info['funcalls']
Mess = info['task']
NIte = info['nIte']
os.rename("verboseValues_%i.ascii"%NIte,"hexFinalValues.ascii")

# change file from hex mesh to mix mesh
for path, subdirs, names in os.walk(feModelDir):
    for name in names:
        if name is not '__init__.py' and (name.split('.')[-1] == 'py'):
            try:
                filePath = os.path.join(path, name)
                workspace = toolbox.getWorkspace(filePath)
                shutil.rmtree(workspace, ignore_errors=True)
                with open(filePath) as f:
                    newText=f.read().replace('HexMesh', 'MixMesh')
                with open(filePath, "w") as f:
                    f.write(newText)
            except:
                print 'warning: "%s" cannot be edited' % filePath
                continue    

#perform optimisation -- mix mesh
GSFactor,fVal,info = parameterFit1Parr.main(expDir, feModelDir, pBounds=bounds, options=optiParam)
Nfev = info['funcalls']
Mess = info['task']
NIte = info['nIte']
os.rename("verboseValues_%i.ascii"%NIte,"mixFinalValues.ascii")

# change file from mix mesh to tet mesh
for path, subdirs, names in os.walk(feModelDir):
    for name in names:
        if name is not '__init__.py' and (name.split('.')[-1] == 'py'):
            try:
                filePath = os.path.join(path, name)
                workspace = toolbox.getWorkspace(filePath)
                shutil.rmtree(workspace, ignore_errors=True)
                with open(filePath) as f:
                    newText=f.read().replace('MixMesh', 'TetMesh')
                with open(filePath, "w") as f:
                    f.write(newText)
            except:
                print 'warning: "%s" cannot be edited' % filePath
                continue    

#perform optimisation -- tet mesh
GSFactor,fVal,info = parameterFit1Parr.main(expDir, feModelDir, pBounds=bounds, options=optiParam)
Nfev = info['funcalls']
Mess = info['task']
NIte = info['nIte']
os.rename("verboseValues_%i.ascii"%NIte,"tetFinalValues.ascii")


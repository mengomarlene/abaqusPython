import parameterFitFinal
import os

dir = os.path.join(os.getcwd(),'2DModels')
subdir = os.path.join(dir,'tt0101nobridgesFull')
dataFile = os.path.join(subdir,'tt01MeasuredDisplacement.ascii')
feModel = os.path.join(subdir,'optiCustomCoheFNeoHooke.py')
p0 = [.5,.5]#,0.]#Knn,Ktt,friction coef
bounds = [(1e-2,1e2),(1e-2,1e2)]#,(0.,1.)]

optiParam = {}
optiParam['maxEval'] = 40 # max number of function evaluation in the optimisation process !!there is more than one evalutation per iteration as the jacobian as to be computed!!
optiParam['epsfcn'] = .0001 # step taken to compute the jacobian by a finite difference method
optiParam['ftol'] = 1e-8 # tolerance on the function value

#read data file
expData = [[],[]]
with open(dataFile, 'r') as file:
    lines = file.readlines()
    for line in lines: 
        lineData = map(float,line.split())
        expData[0].append(lineData[0]/2.)
        expData[1].append(lineData[1]/2.)
    #expData = zip(*(map(float,line.split()) for line in file.readlines()))

#perform optimisation
p,fVal,info = parameterFitFinal.main(p0, expData, feModel, options=optiParam, pBounds=bounds)

#plot results
import numpy as np
if bounds is None:
    nx = len(fVal)
    xi = np.linspace(min(expData[0]), max(expData[0]), nx)
    intExp = parameterFitFinal.interpolateResults(expData,xi)
    feData = [xi,intExp+fVal]
else:
    feData = parameterFitFinal.computeFEData(p,feModel)
ss_err = (np.array(fVal)**2).sum()
ss_tot = ((np.array(expData[1])-np.array(expData[1]).mean())**2).sum()
rsquared = 1-(ss_err/ss_tot)
print info
print "rsquare fit : ",rsquared
parameterFitFinal.plotValues(feData, feModel, expData)

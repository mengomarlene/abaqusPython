import parameterFit
import os
mainDir = os.path.join(os.path.dirname(os.getcwd()),'myModels')
expDir = dir = os.path.join(mainDir,'HexModelsOfRadialTests')
feModelDir = os.path.join(expDir,'cohesiveOpti')

optiParam = {}
optiParam['maxEval'] = 40 # max number of function evaluation in the optimisation process !!there is more than one evalutation per iteration as the jacobian as to be computed!!
optiParam['epsfcn'] = .1 # step taken to compute the jacobian by a finite difference method
optiParam['ftol'] = 1e-6 # tolerance on the function value

# coheValues = (1.,10.,100.,1000.)
# output = list()
# for value in coheValues:
    # res = parameterFit.residuals([value,value], feModelDir, expDir, modelType='Int')
    # output.append(res)
# minValue = coheValues[output.index(min(output))]
# p0 = [minValue,minValue]
# bounds = [(minValue/2.,minValue*5.),(minValue/2.,minValue*5.)]

coheValue = 0.24/(3.98/10.5) #mean testing length = 3.98, mean nb of lamellae = 10.5; C10 = 0.04 ==> E = .24
p0 = [coheValue,coheValue]
bounds = [(coheValue/100.,coheValue*5.),(coheValue/100.,coheValue*5.)]
#perform optimisation
p,fVal,info = parameterFit.main(p0, expDir, feModelDir, pBounds=bounds,options=optiParam, modelType='int')

#plot results
# import numpy as np
# if bounds is None:
    # nx = len(fVal)
    # xi = np.linspace(min(expData[0]), max(expData[0]), nx)
    # intExp = parameterFitFinal.interpolateResults(expData,xi)
    # feData = [xi,intExp+fVal]
# else:
    # feData = parameterFitFinal.computeFEData(p,feModel)
# ss_err = (np.array(fVal)**2).sum()
# ss_tot = ((np.array(expData[1])-np.array(expData[1]).mean())**2).sum()
# rsquared = 1-(ss_err/ss_tot)
# print info
# print "rsquare fit : ",rsquared
# parameterFitFinal.plotValues(feData, feModel, expData)

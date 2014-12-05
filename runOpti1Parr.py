import parameterFit1Parr
import os

expDir = dir = os.path.join(os.getcwd(),'HexModelsOfRadialTests')
feModelDir = os.path.join(expDir,'cohesiveOpti1')

optiParam = {}
optiParam['maxEval'] = 40 # max number of function evaluation in the optimisation process !!there is more than one evalutation per iteration as the jacobian as to be computed!!
optiParam['epsfcn'] = .1 # step taken to compute the jacobian by a finite difference method
optiParam['ftol'] = 1e-6 # tolerance on the function value

bounds = (10.,1e4)

#perform optimisation
p,fVal,info = parameterFit1Parr.main(expDir, feModelDir, pBounds=bounds, options=optiParam, modelType='Int')
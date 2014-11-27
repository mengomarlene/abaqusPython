# -*- coding: mbcs -*-
#TO USE ONLY IF VTK IS INSTALLED... run with python whose version has vtk installed

#1-odb File location
odbPath = 'D:/myWork/FEModels/workspace/discFomMRIModels_displBondedHolzapfel/displBondedHolzapfelFibresIn.odb'
notWantedParts = []#['PART-2-1']#if none then write []

#2-vtk new file location
vtkFile = 'D:/myWork/FEModels/workspace/discFomMRIModels_displBondedHolzapfel/displBondedHolzapfelFibresIn.vtk'

#3-field to write (only 1 field)
'''
 - name to give to the output field - must NOT contain spaces
 - must contain VM for output VM stress - must contain pressure for P output
 - other field can be implemented in pythonTools\vtkTools AND abaqusPythonTools\abaqusVTKTools (see last 2 functions)
''' 
fieldName = "VM_Stress"

#NO NEED TO CHANGE ANYTHING BEYOND HERE

display = True

import os
vizu = False
vtkFile.replace('/',os.sep)
odbPath.replace('/',os.sep)
if not(os.path.isfile(vtkFile)):
    from pythonTools.vtkTools import produceVTKFileNoElSet
    vizu = produceVTKFileNoElSet(odbPath,vtkFile,fieldName,notWantedParts)
# if vizu or display:
from pythonTools.vtkTools import displayUGridWithField
displayUGridWithField(vtkFile,fieldName)
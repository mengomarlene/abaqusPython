# -*- coding: mbcs -*-

#1-odb File location
odbPath = 'D:/myWork/FEModels/workspace/discFomMRIModels_displBondedHolzapfel/displBondedHolzapfelFibresIn.odb'
notWantedParts = []#['PART-2-1']#if none then write []
notWantedEleSets = []#['PT_LOWERE_POT','PT_UPPER_POT']#if none then write []

#2-vtk new file location
vtkFile = 'D:/myWork/FEModels/workspace/discFomMRIModels_displBondedHolzapfel/displBondedHolzapfelFibresIn.vtk'

#NO NEED TO CHANGE ANYTHING BEYOND HERE
import os
vtkFile.replace('/',os.sep)
odbPath.replace('/',os.sep)
from pythonTools.vtkTools import produceVTKFileMaterial
vizu = produceVTKFileMaterial(odbPath,vtkFile,notWantedParts,notWantedEleSets)

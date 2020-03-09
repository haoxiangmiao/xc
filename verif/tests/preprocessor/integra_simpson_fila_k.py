# -*- coding: utf-8 -*-
import xc_base
import geom
import xc
from solution import predefined_solutions
from model import predefined_spaces
from materials import typical_materials
import integra_simpson as isimp

__author__= "Luis C. Pérez Tato (LCPT)"
__copyright__= "Copyright 2014, LCPT"
__license__= "GPL"
__version__= "3.0"
__email__= "l.pereztato@gmail.com"

# Problem type
feProblem= xc.FEProblem()
preprocessor=  feProblem.getPreprocessor
nodes= preprocessor.getNodeHandler
modelSpace= predefined_spaces.SolidMechanics3D(nodes)
# Define materials
elast= typical_materials.defElasticMaterial(preprocessor, "elast",3000)


seedElemHandler= preprocessor.getElementHandler.seedElemHandler
seedElemHandler.defaultMaterial= "elast"
seedElemHandler.dimElem= 3 # Dimension of element space
seedElemHandler.defaultTag= 1 #Tag for the next element.
truss= seedElemHandler.newElement("Truss",xc.ID([0,0]))
truss.sectionArea= 10.0
unifGrids= preprocessor.getMultiBlockTopology.getUniformGrids
uGrid= unifGrids.newUniformGrid()

uGrid.org= geom.Pos3d(0.0,3.0,0.0)
uGrid.Lx= 1
uGrid.Ly= 3
uGrid.Lz= 1
uGrid.nDivX= 0
uGrid.nDivY= 3
uGrid.nDivZ= 0

total= preprocessor.getSets.getSet("total")
total.genMesh(xc.meshDir.I)

abscissae= []
gridNodes= uGrid.getNodeLayers
nNodes= uGrid.nDivY+1
for k in range(1,nNodes+1):
  n= gridNodes.getAtIJK(1,1,k)
  abscissae.append(n.getInitialPos3d.y)


def func(y):
  return y-1.0

#pesos= uGrid.getSimpsonWeights("k",'y-1.0',1,1,10)
pesos= isimp.getSimpsonWeights(abscissae,func,10)
suma= pesos[0]+pesos[1]+pesos[2]+pesos[3]

import os
from miscUtils import log_messages as lmsg
fname= os.path.basename(__file__)
if abs(suma-(9/8.0+3+4+19/8.0))<1e-5:
  print "test ",fname,": ok."
else:
  lmsg.error(fname+' ERROR.')




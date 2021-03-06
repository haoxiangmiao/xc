# -*- coding: utf-8 -*-
''' Shear checking of a reinforced concrete section.
    Some results are compared with those of the exercise ER-CS-01 from
    www.areadecalculo.com. According to EHE-08».
'''
from __future__ import division


from misc import scc3d_testing_bench
from solution import predefined_solutions

from materials.ehe import EHE_materials
from materials.ehe import EHE_limit_state_checking
import xc_base
import geom
import xc
from solution import predefined_solutions
from model import predefined_spaces
from materials import typical_materials
import math

__author__= "Luis C. Pérez Tato (LCPT) and Ana Ortega (AOO)"
__copyright__= "Copyright 2015, LCPT and AOO"
__license__= "GPL"
__version__= "3.0"
__email__= "l.pereztato@gmail.com"

width= 0.3 # Section width expressed in meters.
depth= 0.4 # Section depth expressed in meters.
cover= 0.05 # Concrete cover expressed in meters.
areaBarra=4e-4

NDato= -400e3 # Axial force for shear checking.
MyDato= 1e5 # Bending moment for shear checking.
MzDato= 1e3 # Bending moment for shear checking.

numBarras= 3

''' 
print "numBarras= ",numBarras
   '''

feProblem= xc.FEProblem()
preprocessor=  feProblem.getPreprocessor
# Materials definition
materialHandler= preprocessor.getMaterialHandler

concr= EHE_materials.HA25
concr.alfacc=0.85    #f_maxd= 0.85*fcd concrete long term compressive strength factor (normally alfacc=1)
concrMatTag25= concr.defDiagD(preprocessor)
tagB500S= EHE_materials.B500S.defDiagD(preprocessor)

respT= typical_materials.defElasticMaterial(preprocessor, "respT",1e10) # Torsion response.
respVy= typical_materials.defElasticMaterial(preprocessor, "respVy",1e6) # Shear response in y direction.
respVz= typical_materials.defElasticMaterial(preprocessor, "respVz",1e3) # Shear response in y direction.
geomSecHA= preprocessor.getMaterialHandler.newSectionGeometry("geomSecHA")
regions= geomSecHA.getRegions
rg= regions.newQuadRegion(EHE_materials.HA25.nmbDiagD)
rg.nDivIJ= 10
rg.nDivJK= 10
rg.pMin= geom.Pos2d(-width/2.0,-depth/2.0)
rg.pMax= geom.Pos2d(width/2.0,depth/2.0)
reinforcement= geomSecHA.getReinfLayers
reinforcementInf= reinforcement.newStraightReinfLayer(EHE_materials.B500S.nmbDiagD)
reinforcementInf.numReinfBars= numBarras
reinforcementInf.barArea= areaBarra
reinforcementInf.p1= geom.Pos2d(cover-width/2.0,cover-depth/2.0) # bottom layer.
reinforcementInf.p2= geom.Pos2d(width/2.0-cover,cover-depth/2.0)
reinforcementSup= reinforcement.newStraightReinfLayer(EHE_materials.B500S.nmbDiagD)
reinforcementSup.numReinfBars= numBarras
reinforcementSup.barArea= areaBarra
reinforcementSup.p1= geom.Pos2d(cover-width/2.0,depth/2.0-cover) # top layer.
reinforcementSup.p2= geom.Pos2d(width/2.0-cover,depth/2.0-cover)

secHA= materialHandler.newMaterial("fiberSectionShear3d","secHA")
fiberSectionRepr= secHA.getFiberSectionRepr()
fiberSectionRepr.setGeomNamed("geomSecHA")
secHA.setupFibers()
secHA.setRespVyByName("respVy")
secHA.setRespVzByName("respVz")
secHA.setRespTByName("respT")

scc3d_testing_bench.sectionModel(preprocessor, "secHA")


# Constraints
modelSpace= predefined_spaces.getStructuralMechanics3DSpace(preprocessor)
modelSpace.fixNode000_000(1)

# Loads definition
loadHandler= preprocessor.getLoadHandler

lPatterns= loadHandler.getLoadPatterns

#Load modulation.
ts= lPatterns.newTimeSeries("constant_ts","ts")
lPatterns.currentTimeSeries= "ts"
#Load case definition
lp0= lPatterns.newLoadPattern("default","0")
lp0.newNodalLoad(2,xc.Vector([NDato,0,0,0,MyDato,MzDato]))
lp1= lPatterns.newLoadPattern("default","1")
lp1.newNodalLoad(2,xc.Vector([NDato,0,0,0,MzDato/10.0,MyDato/10.0]))
lp2= lPatterns.newLoadPattern("default","2")
lp2.newNodalLoad(2,xc.Vector([NDato,0,0,0,0,0]))

#We add the load case to domain.
lPatterns.addToDomain(lp0.name)


# Solution procedure
analisis= predefined_solutions.simple_newton_raphson(feProblem)
analOk= analisis.analyze(10)
if(analOk!=0):
  print "Error!; failed to converge."
  exit()



concreteSectionShearParams= EHE_limit_state_checking.ShearController('ULS_shear')



elements= preprocessor.getElementHandler
ele1= elements.getElement(1)
scc= ele1.getSection()
concreteSectionShearParams.calcVuEHE08(scc,"",EHE_materials.HA25,EHE_materials.B500S,NDato,math.sqrt(MyDato**2+MzDato**2),0,0)


Vu2A= concreteSectionShearParams.Vu2


loadHandler= preprocessor.getLoadHandler.removeFromDomain("0") # Quitamos la carga.
preprocessor.resetLoadCase()
loadHandler= preprocessor.getLoadHandler.addToDomain("1") # Añadimos la otra carga.


analOk= analisis.analyze(10)
if(analOk!=0):
  print "Error!; failed to converge."
  exit()


concreteSectionShearParams.calcVuEHE08(scc,"",EHE_materials.HA25,EHE_materials.B500S, 0,0,0,0)

Vu2B= concreteSectionShearParams.Vu2


loadHandler= preprocessor.getLoadHandler.removeFromDomain("1") # Quitamos la carga.
preprocessor.resetLoadCase()
loadHandler= preprocessor.getLoadHandler.addToDomain("2") # Añadimos la otra carga.


analOk= analisis.analyze(10)
if(analOk!=0):
  print "Error!; failed to converge."
  exit()


concreteSectionShearParams.calcVuEHE08(scc,"",EHE_materials.HA25,EHE_materials.B500S, 0,0,0,0)

Vu2C= concreteSectionShearParams.Vu2


''' Instead of taking Vu2= 127.638 kN as stated in the reference
document, we take 117.052 kN, that's because here we take into account
the axial force in the reinforcement so average stress in the web
is smaller. '''
Vu2ATeor= 117.052e3
ratio1= ((Vu2A-Vu2ATeor)/Vu2ATeor)
Vu2BTeor= 90906.4
ratio2= ((Vu2B-Vu2BTeor)/Vu2BTeor)
Vu2CTeor= 98923
ratio3= ((Vu2C-Vu2CTeor)/Vu2CTeor)


'''
print "Vu2A= ",Vu2A/1e3," kN"
print "Vu2ATeor= ",Vu2ATeor/1e3," kN"
print "ratio1= ",ratio1
print "\nVu2B= ",Vu2B/1e3," kN"
print "Vu2BTeor= ",Vu2BTeor/1e3," kN"
print "ratio2= ",ratio2
print "\nVu2C= ",Vu2C/1e3," kN"
print "Vu2CTeor= ",Vu2CTeor/1e3," kN"
print "ratio3= ",ratio3
 '''


import os
from misc_utils import log_messages as lmsg
fname= os.path.basename(__file__)
if (abs(ratio1)<1e-5) & (abs(ratio2)<0.03) & (abs(ratio3)<1e-5):
  print "test ",fname,": ok."
else:
  lmsg.error(fname+' ERROR.')

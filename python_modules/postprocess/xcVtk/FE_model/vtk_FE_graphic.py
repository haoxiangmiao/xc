# -*- coding: utf-8 -*-
''' Graphics of the finite element model.
'''

from __future__ import division
from __future__ import print_function

__author__= "Luis C. Pérez Tato (LCPT) , Ana Ortega (AO_O) "
__copyright__= "Copyright 2016, LCPT, AO_O"
__license__= "GPL"
__version__= "3.0"
__email__= "l.pereztato@ciccp.es, ana.ortega@ciccp.es "

import sys
import vtk
from misc_utils import log_messages as lmsg
import xc_base
from vtk_utils import utils_vtk
from postprocess.xcVtk import vtk_graphic_base
from postprocess.xcVtk.fields import local_axes_vector_field as lavf
import random as rd 
import xc

class RecordDefDisplayEF(vtk_graphic_base.RecordDefDisplay):
    ''' Define the parameters to configure the output device.
    '''
    def __init__(self):
        super(RecordDefDisplayEF,self).__init__()
        self.nodes= None
        self.gridMapper= None
        
    def VtkDefineElementsActor(self, reprType,field,color=xc.Vector([rd.random(),rd.random(),rd.random()])):
        ''' Define the actor to display elements

        :param reprType: type of representation ("points", "wireframe" or
               "surface")
        :param field: field to be repreresented
        :param color: RGB color to represent the elements (defaults to random
                      color)
        '''
        if(field):
            field.setupOnGrid(self.gridRecord.uGrid)
        self.gridMapper= vtk.vtkDataSetMapper()
        self.gridMapper.SetInputData(self.gridRecord.uGrid)
        if(field):
            field.setupOnMapper(self.gridMapper)
        elemActor= vtk.vtkActor()
        elemActor.SetMapper(self.gridMapper)
        elemActor.GetProperty().SetColor(color[0],color[1],color[2])

        if(reprType=="points"):
            elemActor.GetProperty().SetRepresentationToPoints()
        elif(reprType=="wireframe"):
            elemActor.GetProperty().SetRepresentationToWireFrame()
        elif(reprType=="surface"):
            elemActor.GetProperty().SetRepresentationToSurface()
        else:
            lmsg.error("Representation type: '"+ reprType+ "' unknown.")
        self.renderer.AddActor(elemActor)
        if(field):
            field.creaColorScaleBar()
            self.renderer.AddActor2D(field.scalarBar)

    def VtkDefineNodesActor(self, radius):
        '''Define the actor to display nodes.

        :param radius: radius of the sphere used as symbol to represent nodes.
        '''
        sphereSource= vtk.vtkSphereSource()
        sphereSource.SetRadius(radius)
        sphereSource.SetThetaResolution(5)
        sphereSource.SetPhiResolution(5)

        markNodes= vtk.vtkGlyph3D()
        markNodes.SetInputData(self.gridRecord.uGrid)
        markNodes.SetSourceData(sphereSource.GetOutput())
        markNodes.ScalingOff()
        markNodes.OrientOff()

        mappNodes= vtk.vtkPolyDataMapper()
        mappNodes.SetInputData(markNodes.GetOutput())
        visNodes= vtk.vtkActor()
        visNodes.SetMapper(mappNodes)
        visNodes.GetProperty().SetColor(rd.random(),rd.random(),rd.random())
        self.renderer.AddActor(visNodes)

    def VtkLoadElemMesh(self,field,defFScale=0.0,eigenMode=None):
        '''Load the element mesh

        :param field: scalar field to be represented
        :param defFScale: factor to apply to current displacement of nodes 
                  so that the display position of each node equals to
                  the initial position plus its displacement multiplied
                  by this factor. In case of modal analysis, the displayed 
                  position of each node equals to the initial position plus
                  its eigenVector multiplied by this factor.
                  (Defaults to 0.0, i.e. display of initial/undeformed shape)
        :param eigenMode: eigenvibration mode if we want to display the deformed 
                 shape associated with it when a modal analysis has been carried out. 
                 Defaults to None: no modal analysis.

        '''
        # Define grid
        self.nodes= vtk.vtkPoints()
        self.gridRecord.uGrid= vtk.vtkUnstructuredGrid()
        self.gridRecord.uGrid.SetPoints(self.nodes)
        eSet= self.gridRecord.xcSet
        eSet.numerate()
        self.gridRecord.uGrid.name= eSet.name+'_grid'
        # Scalar values.
        nodeSet= eSet.nodes
        if(field):
            arr= field.fillArray(nodeSet)
            field.creaLookUpTable()      
        # Load nodes in vtk
        setNodes= eSet.nodes
        if eigenMode==None:
            for n in setNodes:
                pos= n.getCurrentPos3d(defFScale)
                self.nodes.InsertPoint(n.getIdx,pos.x,pos.y,pos.z)
        else:
            for n in setNodes:
                pos= n.getEigenPos3d(defFScale,eigenMode)
                self.nodes.InsertPoint(n.getIdx,pos.x,pos.y,pos.z)
         # Load elements in vtk
        setElems= eSet.elements
        for e in setElems:
            vertices= xc_base.vector_int_to_py_list(e.getIdxNodes)
            vtx= vtk.vtkIdList()
            for vIndex in vertices:
                vtx.InsertNextId(vIndex)
            if(e.getVtkCellType!= vtk.VTK_VERTEX):
                self.gridRecord.uGrid.InsertNextCell(e.getVtkCellType,vtx)
        setConstraints= eSet.getConstraints
        for c in setConstraints:
            if(hasattr(c,'getIdxNodes')):
                vertices= xc_base.vector_int_to_py_list(c.getIdxNodes)
                vtx= vtk.vtkIdList()
                for vIndex in vertices:
                    vtx.InsertNextId(vIndex)
                if(c.getVtkCellType!= vtk.VTK_VERTEX):
                    self.gridRecord.uGrid.InsertNextCell(c.getVtkCellType,vtx)

    def defineMeshScene(self, field,defFScale=0.0,eigenMode=None,color=xc.Vector([rd.random(),rd.random(),rd.random()])):
        '''Define the scene for the mesh

        :param field: scalar field to be represented
        :param defFScale: factor to apply to current displacement of nodes 
                    so that the display position of each node equals to
                    the initial position plus its displacement multiplied
                    by this factor. (Defaults to 0.0, i.e. display of 
                    initial/undeformed shape)
        '''
        self.VtkLoadElemMesh(field,defFScale,eigenMode)
        self.renderer= vtk.vtkRenderer()
        self.renderer.SetBackground(self.bgRComp,self.bgGComp,self.bgBComp)
        self.VtkDefineNodesActor(0.002)
        self.VtkDefineElementsActor("surface",field,color)
        self.renderer.ResetCamera()

        #Implement labels.
        # if(self.gridRecord.entToLabel=="elementos"):
        #   VtkDibujaIdsElementos(self.renderer)
        # elif(self.gridRecord.entToLabel=="nodes"):
        #   vtk_define_mesh_nodes.VtkDibujaIdsNodes(self.renderer)
        # else:
        #   print("Entity: ", self.gridRecord.entToLabel, " unknown.")

    def FEmeshGraphic(self,setToDisplay,caption= '',cameraParameters= vtk_graphic_base.CameraParameters('XYZPos'),defFScale=0.0):
        ''' Graphic of the FE mesh

        :param setToDisplay:   XC set of elements to be displayed
        :param caption: text to write in the graphic
        :param cameraParameters: camera parameters (position, orientation,...).
        :param defFScale: factor to apply to current displacement of nodes 
                   so that the display position of each node equals to
                   the initial position plus its displacement multiplied
                   by this factor. (Defaults to 0.0, i.e. display of 
                   initial/undeformed shape)
        '''
        lmsg.warning('FEmeshGraphic DEPRECATED use displayFEMesh.')
        self.cameraParameters= cameraParameters
        self.displayFEMesh(setToDisplay,caption,defFScale)

    def displayFEMesh(self,setToDisplay,caption= '',defFScale=0.0):
        ''' Graphic of the FE mesh

        :param setToDisplay:   XC set of elements to be displayed
        :param caption: text to write in the graphic
        :param defFScale: factor to apply to current displacement of nodes 
                   so that the display position of each node equals to
                   the initial position plus its displacement multiplied
                   by this factor. (Defaults to 0.0, i.e. display of 
                   initial/undeformed shape)
        '''
        self.setupGrid(setToDisplay)
        self.displayGrid(caption)
        
    def displayLocalAxes(self,setToDisplay,caption= 'local axis', vectorScale=1.0, fileName= None, defFScale= 0.0):
        '''vector field display of the loads applied to the chosen set of elements in the load case passed as parameter

        :param setToDisplay:   set of elements to be displayed (defaults to total set)
        :param caption:        text to display in the graphic 
        :param vectorScale:    factor to apply to the vectors length in the representation
        :param fileName: file name to store the image. If none -> window on screen.
        :param defFScale: factor to apply to current displacement of nodes 
                   so that the display position of each node equals to
                   the initial position plus its displacement multiplied
                   by this factor. (Defaults to 0.0, i.e. display of 
                   initial/undeformed shape)
        '''
        self.setupGrid(setToDisplay)
        vField=lavf.LocalAxesVectorField(setToDisplay.name+'_localAxes',vectorScale)
        vField.dumpVectors(setToDisplay)
        self.defineMeshScene(None) 
        vField.addToDisplay(self)
        self.displayScene(caption)

    def displayStrongWeakAxis(self,setToDisplay,caption= 'strong and weak axis', vectorScale=1.0):
        '''vector field display of the loads applied to the chosen set of elements in the load case passed as parameter

        :param setToDisplay:   set of elements to be displayed (defaults to total set)
        :param caption:        text to display in the graphic 
        :param vectorScale:    factor to apply to the vectors length in the representation
        '''
        self.setupGrid(setToDisplay)
        vField=lavf.StrongWeakAxisVectorField(setToDisplay.name+'_strongWeakAxis',vectorScale)
        vField.dumpVectors(setToDisplay)
        self.defineMeshScene(None) 
        vField.addToDisplay(self)
        self.displayScene(caption)

    def defineMeshActorsSet(self,elemSet,field,defFScale,nodeSize):
        self.setupGrid(elemSet)
        if elemSet.color.Norm()==0:
            elemSet.color=xc.Vector([rd.random(),rd.random(),rd.random()])
        self.VtkLoadElemMesh(field,defFScale,eigenMode=None)
        self.VtkDefineNodesActor(nodeSize)
        self.VtkDefineElementsActor("surface",field,elemSet.color)

    def displayMesh(self, xcSets, field= None, diagrams= None, caption= '',fileName= None,defFScale=0.0,nodeSize=0.01,scaleConstr=0.2):
        '''Display the finite element mesh 

        :param xcSets: set or list of sets to be displayed
        :param field: scalar field to show (optional)
        :param diagrams: diagrams to show (optional)
        :param caption: text to display in the graphic.
        :param fileName: name of the graphic file to create (if None -> screen window).
        :param defFScale: factor to apply to current displacement of nodes 
                    so that the display position of each node equals to
                    the initial position plus its displacement multiplied
                    by this factor. (Defaults to 0.0, i.e. display of 
                    initial/undeformed shape)
        :param nodeSize: size of the points that represent nodes (defaults to
                    0.01)
        :param scaleConstr: scale of SPConstraints symbols (defaults to 0.2)
        '''
        self.renderer= vtk.vtkRenderer()
        self.renderer.SetBackground(self.bgRComp,self.bgGComp,self.bgBComp)
        if type(xcSets)==list:
            for s in xcSets:
                self.defineMeshActorsSet(s,field,defFScale,nodeSize)
                self.displaySPconstraints(s,scaleConstr)
        else:
            self.defineMeshActorsSet(xcSets,field,defFScale,nodeSize)
            self.displaySPconstraints(xcSets,scaleConstr)
        self.renderer.ResetCamera()
        if(diagrams):
            for d in diagrams:
                self.appendDiagram(d)
        self.displayScene(caption,fileName)

    def displayLoadOnNode(self, nod, color, force, moment, fScale,defFScale=0.0):
        '''Display loads on one node

         :param nod: node instance
         :param color: color
         :param force: force (displayed as a single arrow)
         :param moment: moment (displayed as a double arrow)
         :param fScale: scaling factor (forces and moments)
         :param defFScale: factor to apply to current displacement of nodes 
                    so that the display position of each node equals to
                    the initial position plus its displacement multiplied
                    by this factor. (Defaults to 0.0, i.e. display of 
                    initial/undeformed shape)
         '''
        #actorName= baseName+"%04d".format(nod.tag) # Node tag.
        pos= nod.getCurrentPos3d(defFScale)
        absForce= force.Norm()
        if(absForce>1e-6):
            utils_vtk.drawVtkSymb('arrow',self.renderer,color,pos,force,fScale*absForce)
        absMoment= moment.Norm()
        if(absMoment>1e-6):
            utils_vtk.drawVtkSymb('doubleArrow',self.renderer,color,pos,moment,fScale*absMoment)

    def displayNodalLoads(self, preprocessor, loadPattern, color, fScale):
        '''Display the all nodal loads defined in a load pattern

        :param preprocessor: preprocessor
        :param loadPattern: load pattern
        :param color: color of the symbols (arrows)
        :param fScale: factor to apply to current displacement of nodes 
               so that the display position of each node equals to
               the initial position plus its displacement multiplied
               by this factor. (Defaults to 0.0, i.e. display of 
               initial/undeformed shape)
        '''
        loadPattern.addToDomain()
        loadPatternName= loadPattern.getProp("dispName")
        lIter= loadPattern.loads.getNodalLoadIter
        load= lIter.next()
        while not(load is None):
            actorName= "flecha"+loadPatternName+"%04d".format(load.tag) # Tag force.
            nodeTag= load.getNodeTag
            node= preprocessor.getNodeHandler.getNode(nodeTag)
            force= load.getForce
            moment= load.getMoment
            self.displayLoadOnNode(node, color,force,moment,fScale)    
            load= lIter.next()
        loadPattern.removeFromDomain()


    def displayElementPunctualLoad(self, preprocessor, pLoad,loadPattern, renderer, color, force, fScale):
        '''Display punctual loads on elements
        '''
        xForce= pLoad.getElems()
        eleTags= pLoad.elementTags
        loadPatternName= loadPattern.getProp("dispName")
        actorName= "flechaP"+loadPatternName+"%04d".format(tag) # Tag force.
        for tag in eleTags:
            ele= preprocessor.getElementHandler.getElement(tag)
            actorName+= "%04d".format(tag) # Tag elemento.
            pos= ele.point(xForce)
            utils_vtk.drawVtkSymb('arrow',self.renderer,color,pos,force,fScale)

    def displayElementUniformLoad(self, preprocessor, unifLoad,loadPattern, color, force, fScale):
        loadPatternName= loadPattern.getProp("dispName")
        actorName= "flechaU"+loadPatternName+"%04d".format(unifLoad.tag)
        eleTags= unifLoad.elementTags
        for tag in eleTags:
            ele= preprocessor.getElementHandler.getElement(tag)
            actorName+= "%04d".format(tag) # Tag elemento.
            lmsg.error('displayElementUniformLoad not implemented.')
            # points= ele.getPoints(3,1,1,True)
            # i= 0
            # for capa in points:
            #   for pos in capa: 
            #     print pos
            #     utils_vtk.drawArrow(self.renderer,color,pos,force,fScale*force.Norm())
            #     i+= 1

    def displayElementalLoads(self, preprocessor,loadPattern, color, fScale):
        loadPattern.addToDomain()
        eleLoadIter= loadPattern.loads.getElementalLoadIter
        eleLoad= eleLoadIter.next()
        lmsg.error('displayElementalLoads not implemented.')
        # while not(eleLoad is None):
        #   force= eleLoad.getGlobalForces()
        #   categoria= eleLoad.category
        #   if(categoria=="uniform"):
        #     self.displayElementUniformLoad(preprocessor, eleLoad,loadPattern,color,force,fScale)
        #   else:
        #     self.displayElementPunctualLoad(preprocessor, eleLoad,loadPattern,color,force,fScale)
        # loadPattern.removeFromDomain()

    def displayLoads(self, preprocessor, loadPattern):
        clrVectores= loadPattern.getProp("color")
        fScaleVectores= loadPattern.getProp("scale")
        self.displayElementalLoads(preprocessor, loadPattern,clrVectores,fScaleVectores)
        self.displayNodalLoads(preprocessor, loadPattern,clrVectores,fScaleVectores)

    def appendDiagram(self,diagram):
        diagram.addDiagramToScene(self)

    def displaySPconstraints(self, setToDisplay,scale):
        ''' Display single point constraints.

        :param setToDisplay: set to be displayed
        :param scale: scale for SPConstraints symbols.
        '''
        prep= setToDisplay.getPreprocessor
        nodInSet= setToDisplay.nodes.getTags()
        elementAvgSize= setToDisplay.elements.getAverageSize(False)
        #direction vectors for each DOF
        vx,vy,vz=[1,0,0],[0,1,0],[0,0,1]
        DOFdirVct=(vx,vy,vz,vx,vy,vz)
        spIter= prep.getDomain.getConstraints.getSPs
        sp= spIter.next()
        while sp:
            nod=sp.getNode
            if nod.tag in nodInSet:
                dof= sp.getDOFNumber
                if dof < 3: # This is not true in 2D problems.
                    utils_vtk.drawVtkSymb(symbType='cone',renderer=self.renderer, RGBcolor=[0,0,1], vPos=nod.getInitialPos3d, vDir=DOFdirVct[dof], scale=scale*elementAvgSize)
                else:
                    utils_vtk.drawVtkSymb(symbType='shaftkey',renderer=self.renderer, RGBcolor=[0,1,0], vPos=nod.getInitialPos3d, vDir=DOFdirVct[dof], scale=scale*elementAvgSize)
            sp= spIter.next()
        return
                    
def VtkCargaIdsNodes(recordGrid):
    '''Not yet implemented.'''
    VtkCreaStrArraySetData(recordGrid.setName,"nodes","etiqNod","tag")()
    nmbUGrid.GetPointData().SetStrings(etiqNod)

def VtkDibujaIdsNodes(recordGrid, renderer):
    '''Display node labels (not implemented yet)'''
    ids= vtk.vtkIdFilter()
    ids.SetInput(recordGrid.uGrid)
    ids.CellIdsOff()
    ids.PointIdsOff()

    VtkCargaIdsNodes(recordGrid)

    visPts= vtk.vtkSelectVisiblePoints()
    visPts.SetInput("ids")
    visPts.SetRenderer(renderer)
    visPts.SelectionWindowOff()

    #Create the mapper to display the point ids.  Specify the format to
    #   use for the labels.  Also create the associated actor.
    ldm= vtk.vtkLabeledShStrMapper()
    ldm.SetInput("visPts")
    ldm.LabelTextProperty().SetColor(0.1,0.1,0.1)
    nodeLabels= vtk.vtkActor2D().SetMapper(ldm)
    renderer.AddActor2D(nodeLabels)

def VtkDibujaIdsElementos(ids):
    '''Dibuja las etiquetas de los elementos. Not implemented yet.'''
    cc= vtk.vtkCellCenters()
    vtk.SetInput(ids) #  Centroides de las celdas. 

    visCells= vtk.vtkSelectVisiblePoints()
    visCells.SetInput(cc)
    visCells.SetRenderer("renderer")
    visCells.SelectionWindowOff()

    #Create the mapper to display the cell ids.  Specify the format to
    # use for the labels.  Also create the associated actor.

    cellMapper= vtk.vtkLabeledShStrMapper
    cellMapper.SetInput(visCells)
    cellMapper.LabelTextProperty().SetColor(0,0,0.9)

    cellLabels= vtk.vtkActor2D()
    cellLabels.SetMapper(cellMapper)

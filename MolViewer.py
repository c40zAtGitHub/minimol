#a one window molecule plotter
#ball and stick only
#single bond only
#use visp
#fully interactive

#supported type: .xyz
#input - atom type, atom coord, connectivity
#output - a window displaying the molecules
#   including - colored atoms, element symbol (text), bond, atom index(text)

#stuff need to be stored in a save file 
#   element color
#   element symbol
import numpy as np
from vispy import app, scene
from vispy.app import KeyEvent,MouseEvent

from vispy.util.keys import CONTROL

from minimol.ConnectivityGen import genConnectivity
#from minimol.ElementData import vdWRadii
from minimol.Styles.AtomStyles import VDWStyle
from minimol.Styles.BondStyles import PrimitiveStyle as PBondStyle
#from .Settings import elementColor




class MolViewer(app.Canvas):
    def __init__(self,atomCoords,atomCons=None):
        self.atomCoords = atomCoords #list of tuples of (element,x,y,z)
        if atomCons is None:
            self.connectivity = genConnectivity(atomCoords,thresh=0.75)
        else:
            self.connectivity = atomCons

        self.selectedAtoms = []
        
        #setup the scene and camera
        self.canvas = scene.SceneCanvas(keys='interactive', size=(600, 600), show=True) #where the molecule is plotted
        self.view = self.canvas.central_widget.add_view()
        self.view.camera = scene.cameras.ArcballCamera(fov=0)
        self.view.camera.scale_factor = 4
        #scale factor to be determined?
        print(self.view.camera.get_state())
        #print(dir(self.view.camera))

        #this does not seem to work
        #better put everything in one array
        # #indices for drawing
        # acIndices = {}
        # for ac in self.atomCoords:
        #     element,x,y,z = ac
        #     coord = np.array([x,y,z])
        #     try:
        #         acIndices[element].append(coord)
        #     except KeyError:
        #         acIndices[element] = [coord]
        # self._acIndices = acIndices

        #setup event handling connections
        self.canvas.events.mouse_press.connect(self._recordCurEventPos)
        self.canvas.events.mouse_release.connect(self.onClick)
        self.canvas.events.mouse_wheel.connect(self.onMouseWheel)
        self.canvas.events.resize.connect(self.onResize)

        #prepare drawing styles
        #VDWStyle - the radius of the sphere is based on the scaled vdw radius of element
        self._vdwScale = 0.25
        self.atomStyle = VDWStyle(scale=self._vdwScale)
        #Primitive bond style: gray cylinders
        self.bondStyle = PBondStyle(radius=0.1)
        self._preparePlotData()
        self.drawMolecule()

        #prepare data for atom selection
        self._updateAtomProjection()

        

    #properties
    @property
    def title(self):
        return self.canvas.title
    
    @title.setter
    def title(self,newTitle):
        self.canvas.title = newTitle

    def _preparePlotData(self):
        #preprocess data used for plottting
        #prepare atoms
        nAtom = len(self.atomCoords)
        self._coordData = np.zeros((nAtom,3))
        self._colorData = np.zeros((nAtom,3))
        self._edgeSizeData = np.zeros(nAtom)
        self._edgeColor = (0.9725,0.9882,0.5137)
        self._radiusData = np.zeros(nAtom)
        for i in range(nAtom):
            ac = self.atomCoords[i]
            ele,x,y,z = ac
            self._coordData[i] = [x,y,z]
            self._colorData[i] = self.atomStyle.color(ele)
            self._radiusData[i] = self.atomStyle.radius(ele)




    def drawMolecule(self):
        self.drawAtoms()
        self.drawSingleBonds()

    def drawAtoms(self):
        #draw each element an individual series
        # for element in self._acIndices.keys():
        #     coords = np.array(self._acIndices[element])
        #     color = self.atomStyle.color(element)
        #     radius = self.atomStyle.radius(element)
        #     vis = scene.visuals.Markers(
        #         pos = coords,
        #         size = radius,
        #         face_color = color,
        #         spherical=True,    
        #     )
        #     vis.parent = self.view.scene
        self._atomVis = scene.visuals.Markers(scaling= True,spherical= True)
        self._setAtomData()
        self._atomVis.parent = self.view.scene

    def _setAtomData(self):
        self._atomVis.set_data(
            pos         = self._coordData,
            face_color  = self._colorData,
            size        = self._radiusData*2, #the DIAMETER of the balls !!!!
            edge_color  = self._edgeColor,
            edge_width  = self._edgeSizeData,

        )


    def drawSingleBonds(self):
        #draw each connection as single bond
        self._bondVis = []
        for bond in self.connectivity:
            r0 = self._coordData[bond[0]]
            r1 = self._coordData[bond[1]]
            #print(r0,r1)
            bvis = scene.visuals.Tube(
                np.array([r0,r1]), #the start and the end of the bound
                radius = self.bondStyle.radius,
                color = self.bondStyle.color,
                tube_points = 32,
                #edge_width=0
            )
            bvis.parent = self.view.scene
            self._bondVis.append(bvis)

    def drawBonds(self,bonds,bondOrders):
        pass

    def redrawMolecule(self):
        self._setAtomData()
    
    #selection related events
    def selectAtom(self,atom):
        self.selectedAtoms.append(atom)
        self.selectedAtoms.sort()
        self._edgeSizeData[atom]=0.05
        self._setAtomData()

    def deselectAtom(self,atom):
        self.selectedAtoms.remove(atom)
        self._edgeSizeData[atom]=0.0
        self._setAtomData()

    def deselectAll(self):
        self.selectedAtoms.clear()
        self._edgeSizeData = np.zeros(len(self.atomCoords))
        self._setAtomData()

    def _selectedAtomIndex(self,eventPos):
        #a canvas to atomVisual transformation 
        #whose map method converts world coordinate to canvas coordinate
        #whose imap method converts canvas coordinate to world coordinate
        #c2a_transform = self._atomVis.get_transform("visual","canvas")
        
        
        #eventPos - the position of the click
        #print(eventPos)
        #the transformed coordinate is in (4D) homogeneous coordinate
        #and is thus truncated.

        distances = np.linalg.norm(self._canvasCoordData - eventPos, axis=1)
        #print(distances)
        #print(self._canvasRadiusData)
        closest_indices = np.where(distances < self._canvasRadiusData)[0]
        #print(closest_indices)
        if closest_indices.size == 0:
            return None
        else:
            closest_z = [(i,self._canvasZData[i]) for i in closest_indices]
            closest_z.sort(key=lambda x:x[1])
            return closest_z[0][0]

        
    def _recordCurEventPos(self,event):
        #print("start mouse event at {}".format(event.pos))
        self._downPos = np.array(event.pos)

    def _updateAtomProjection(self):
        #get transformation between the canvas and the world coordinate
        vcTransform = self._atomVis.get_transform("visual","canvas")
        #get the atoms' projected coordinates on the canvas
        self._canvasCoordData = np.array([vcTransform.map(acoord)[:2] for acoord in self._coordData])
        #print(self._canvasCoordData)

        #determine the verticle order of the atoms along the camera
        #   find camera direction
        #       fetch the first 3 elements in the 3rd column of the matrix
        cameraProjMat = self.view.camera.transform.matrix
        cameraDir = np.array([cameraProjMat[0,2],
                              cameraProjMat[1,2],
                              cameraProjMat[2,2]])
        cameraDir /= np.linalg.norm(cameraDir)
        #   calculate projection
        self._canvasZData = np.array([np.dot(r,cameraDir) for r in self._coordData])

        #get the projected radii of the atoms
        self._canvasRadiusData = np.zeros(len(self._radiusData))
        psudoCenter = vcTransform.map(np.array([0.0,0.0,0.0]))
        psudoCenter = psudoCenter[:3]/psudoCenter[3]
        #print("psudoCenter:",psudoCenter)
        for i in range(len(self._radiusData)):
            psudoCoord = vcTransform.map(np.array([self._radiusData[i],0.0,0.0]))
            #print("psudoCoord:",psudoCoord)
            psudoCoord = psudoCoord[:3]/psudoCoord[3]
            cRadius = np.linalg.norm(psudoCoord-psudoCenter)
            self._canvasRadiusData[i] = cRadius
        #print(self._canvasRadiusData)
        #print("projection updated")
        


    #event handling
    def onClick(self,event: MouseEvent):
        #ignore the operation if the mouse is dragging
        #single click - deselect all atoms and select an atom
        #single click on a blank area - deselect all atoms
        #ctrl + single click - select/deselect an atom without deselect all atoms
        curPos = np.array(event.pos)
        if np.linalg.norm(curPos-self._downPos) > 0:
            #this is a dragged event
            #the projection of the atoms on the canvas should be updated
            self._updateAtomProjection()
            return

        #print(event.modifiers)
        try:
            controlPressed = (event.modifiers[0] == 'Control')
        except IndexError:
            controlPressed = False
        #print(controlPressed)
        atom2bSelected = self._selectedAtomIndex(event.pos)


        if atom2bSelected is None:
                #the single click occurs at a blank area
                self.deselectAll()
                

        elif controlPressed:
            if atom2bSelected in self.selectedAtoms:
                #the atom has been selected and needs to be deselected
                self.deselectAtom(atom2bSelected)
            else:
                #the atom 2b selected is not selected
                self.selectAtom(atom2bSelected)

        else:
            self.deselectAll()
            self.selectAtom(atom2bSelected)

        #print(self.selectedAtoms)



    def onClickTest(self,event):
        curPos = np.array(event.pos)
        print("end mouse event at {}".format(curPos))
        mmove = np.linalg.norm(curPos-self._downPos)
        print(mmove)
        if mmove > 0:
            #this is a dragged event
            self._updateAtomProjection()
            return
        #this belongs to onClick as well
        atom2bSelected = self._selectedAtomIndex(event.pos)
        print("Atom {} 2b selected".format(atom2bSelected))
        #pass

    def onMouseWheel(self,event):
        self._updateAtomProjection()

    def onResize(self,event):
        self._updateAtomProjection()



import numpy as np
from vispy import scene
from vispy.app import MouseEvent
from vispy.util.keys import CONTROL

#default styles and setup
from .Defaults import dftBondGenerator
from .Defaults import dftAtomStyle,dftBondStyle
from .Defaults import dftHighlightColor,dftHighlightMargin



class MolWindow(scene.SceneCanvas):
    def __init__(self,
                 atomCoords = None,
                 bonds = None,
                 size = (800,600), #size of the widget
                 ):
        """
        The mini molecular viewer widget

        input:
        atomCoords: list of (element,x,y,z) tuples | None
        bonds     : list of 
                    (bAtom1Index,bAtom2Index,bOrder) tuples | 
                    (bAtom1Index,bAtom2Index) tuples| None
        size      : the size of the widget in px
        """
        super().__init__(keys='interactive',
                         size=size)
        #unlock to add new attributes
        self.unfreeze()

        #attribute placeholders
        self.nAtom = 0
        
        #data array for atom drawing
        self._aElements = None
        self._aCoords   = None
        self._aColors   = None
        self._aRadii    = None
        #data array for bonds
        self._bonds = None

        #visuals for atom/bond plotting
        self._atomVis = None
        self._bondVis = None

        #data array for atom selection
        self._selectedAtoms = [] #   indices of selected atoms
        self._asMargin  = None

        #[A]tom [C]oordinate [P]rojection arrays
        #record location,radius and z-index of the atoms
        #projected on the view's canvas
        self._acpView = None    
        self._acpCamera = None
        self._acpRadii = None

        #the coordinate of the mouse button press
        self._downPos = None

        #   view and camera
        self.view = self.central_widget.add_view()
        self.view.camera = scene.cameras.ArcballCamera(fov=0)
        self.view.camera.scale_factor = 4

        #drawing styles
        self._atomStyle = dftAtomStyle
        self._bondStyle = dftBondStyle

        #selection styles
        self._highlightColor = dftHighlightColor
        self._highlightMargin = dftHighlightMargin

        #flags indicating wheter the atom and bond plotting
        #data have been initialized
        self._atomInited = False
        self._bondInited = False
        
        #every variable used is set by here
        self.freeze()

        #initialize atom and bond data/visualization
        self.atomCoords = atomCoords
        if bonds is None:
            bonds = dftBondGenerator(atomCoords)
        self.bonds = bonds
        
        #initialize method bindings to mouse events
        self.events.mouse_press.connect(self.onMousePress)
        self.events.mouse_release.connect(self.onClick)
        self.events.mouse_wheel.connect(self.onMouseWheel)
        self.events.resize.connect(self.onResize)
      
    #(private) data preparation process
    def _setAtomData(self,atomCoords):
        nAtom = len(atomCoords)
        self.nAtom = nAtom
        
        #data array for atom plotting
        self._aElements = []
        self._aCoords   = np.zeros((nAtom,3))
        self._aColors   = np.zeros((nAtom,3))
        self._aRadii    = np.zeros(nAtom)
        
        #data array for atom selection
        self._asMargin  = np.zeros(nAtom)

        #unpack atomCoords
        for i in range(nAtom):
            ele,x,y,z = atomCoords[i]
            #   unzip elements for labeling
            self._aElements.append(ele)
            #   unzip coord data
            self._aCoords[i] = [x,y,z]
            #   prepare color data based on element type
            self._aColors[i] = self._atomStyle.color(ele)
            #   prepare radius data based on element type
            self._aRadii[i]  = self._atomStyle.radius(ele)

        if self.nAtom > 0:
            self._atomInited = True
        else:
            self._atomInited = False


    #(private) init plotting object methods
    def _setAtomVisuals(self):
        if self._atomInited is True:
            if self._atomVis is None:
                self._atomVis = scene.visuals.Markers(scaling= True,spherical= True)
                self._atomVis.parent = self.view.scene

            self._atomVis.set_data(
                pos            = self._aCoords,
                face_color     = self._aColors,
                size           = self._aRadii*2, #size is the DIAMETER of the balls !!!!
                edge_color     = self._highlightColor,
                edge_width     = self._asMargin
            )

    def _setBondVisuals(self):
        #for now, just print single bonds
        if self._bondInited is True:
            self._setSingleBondVisuals()

    def _setSingleBondVisuals(self):
        #draw each connection as single bond
        if self._bondVis is None:
            self._bondVis = []
        else:
            for vis in self._bondVis:
                vis.visible = False
            self._bondVis.clear()
                
        
            #self._bondVis.clear()
        for bond in self._bonds:
            r0 = self._aCoords[bond[0]]
            r1 = self._aCoords[bond[1]]
            bvis = scene.visuals.Tube(
                np.array([r0,r1]), #the start and the end of the bound
                radius = self._bondStyle.radius,
                color = self._bondStyle.color,
                tube_points = self._bondStyle.resolution,
            )
            bvis.parent = self.view.scene
            self._bondVis.append(bvis)

    #(private) plot updating method
    def _updateAtomSelection(self):
        if self._atomInited is True:
            
            #print(self._asMargin)
            self._atomVis.set_data(
                pos            = self._aCoords,  #pos has to be provided otherwise set_data does not work
                face_color     = self._aColors,
                size           = self._aRadii*2, #size is the DIAMETER of the balls !!!!
                edge_color     = self._highlightColor,
                edge_width     = self._asMargin,
            )

    def _recordCurEventPos(self,event):
        #record the current position of the input event
        #part of the function to distinguish between
        #single click and click-drag operations
        #using the pos difference of press and release events
        self._downPos = np.array(event.pos)


    def _updateACP(self,updateRadii=True):
        #calculate and cache the Atom Coordinates Projection on the View (acpView)
        #and along the Camera's direction (acpCamera)
        #the vdw radii in pixels is recorded in acpRadii (important in zoom in)
        #the acpView and acpCamera is used in determining selected atom(s) by mouse click

        #input
        #updateRadii - flag indicating whether _acpRadii is updated
        #               can be set False when scaling is not involved
        #               setting it True will ensure the consistency of the acp
        #               but with extra cpu cost.
        
        if self._atomInited is True:
            #get transformation between the canvas and the world coordinate
            vcTransform = self._atomVis.get_transform("visual","canvas")
            #get the atoms' projected coordinates on the canvas
            self._acpView = np.array([vcTransform.map(ac)[:2] for ac in self._aCoords])

            #determine the z direction order of the atoms along the camera
            cameraProjMat = self.view.camera.transform.matrix
            cameraDir = np.array([cameraProjMat[0,2],
                                cameraProjMat[1,2],
                                cameraProjMat[2,2]])
            cameraDir /= np.linalg.norm(cameraDir)

            #calculate the atom coordinates projection on the camera (acpCamera)
            self._acpCamera = np.array([np.dot(r,cameraDir) for r in self._aCoords])


            if updateRadii is True:
                #update the vdW radii of atoms in px
                self._acpRadii = np.zeros(self.nAtom)
                acpCenter = vcTransform.map(np.array([0.0,0.0,0.0]))
                acpCenter = acpCenter[:3]/acpCenter[3] #convert (x,y,z,w) to (x/w,y/w,z/w)

                for i in range(self.nAtom):
                    acpCoord = vcTransform.map(np.array([self._aRadii[i],0.0,0.0]))
                    acpCoord = acpCoord[:3]/acpCoord[3] #convert from (x,y,z,w) to (x/w,y/w,z/w)

                    cRadius = np.linalg.norm(acpCoord-acpCenter)
                    self._acpRadii[i] = cRadius

    # atom selection related methods
    def _selectedAtomIndex(self,eventPos):
        #determine the atom being selected by the mouse click
        #input:
        #   eventPos - the 2d position of the mouse click on the widget

        #Algorithm:
        #1. determine the atom(s) in the view that covers the position of the click
        #   1.1 cover is defined by |r_atom-r_click| < r_vdw * vdw_scale_factor
        #2. if more than one atom hits, select the one at the top of the view
        #   2.1 top is defined by the smallest (most negative) projection on the camera's direction

        distances = np.linalg.norm(self._acpView - eventPos, axis=1)
        closest_indices = np.where(distances < self._acpRadii)[0]

        if closest_indices.size == 0:
            return None
        else:
            closest_z = [(i,self._acpCamera[i]) for i in closest_indices]
            closest_z.sort(key=lambda x:x[1])
            return closest_z[0][0]
    
    def selectAtom(self,atom):
        if self._atomInited is True:
            self._selectedAtoms.append(atom)
            self._selectedAtoms.sort()
            self._asMargin[atom]=self._highlightMargin
            self._updateAtomSelection()

    def deselectAtom(self,atom):
        if self._atomInited is True:
            self._selectedAtoms.remove(atom)
            self._asMargin[atom]=0.0
            self._updateAtomSelection()

    def resetSelection(self):
        if self._atomInited is True:
            self._selectedAtoms.clear()
            self._asMargin = np.zeros(self.nAtom)
            self._updateAtomSelection()

    #properties
    @property
    def atomCoords(self):
        #form the original list of (ele,x,y,z) tuples
        acoords = [(self._aElements[i],*self._aCoords[i]) for i in range(self.nAtom)]
        return acoords

    @atomCoords.setter
    def atomCoords(self,newAtomCoords):
        if newAtomCoords is None:
            newAtomCoords = []
            
        self._setAtomData(newAtomCoords)
        self._setAtomVisuals()
        self.resetSelection()

        newBonds = dftBondGenerator(self.atomCoords)
        self.bonds = newBonds
        self._updateACP()


    @property
    def bonds(self):
        return self._bonds

    @bonds.setter
    def bonds(self,newBonds):
        #newBonds     : list of 
        #               (bAtom1Index,bAtom2Index,bOrder) tuples | 
        #               (bAtom1Index,bAtom2Index) tuples| None
        if newBonds is None:
            self._bonds = []
            self._bondInited = False

        elif len(newBonds) == 0:
            #empty list
            self._bonds = newBonds
            self._bondInited = False

        elif len(newBonds[0]) == 2:
            #only the atom indices are provided
            #the bond order is set to 1.0
            self._bonds = [(b[0],b[1],1.0) for b in newBonds]
            self._bondInited = True

        else:
            self._bonds = newBonds
            self._bondInited = True

        self._setBondVisuals()

    @property
    def selectedAtoms(self):
        return self._selectedAtoms
    @selectedAtoms.setter
    def selectedAtoms(self,newSelectedAtoms):
        self.resetSelection()
        for atom in newSelectedAtoms:
            self.selectAtom(atom)

    #event binding methods
    def onClick(self,event: MouseEvent):
        curPos = np.array(event.pos)
        if np.linalg.norm(curPos-self._downPos) > 0:
            #this is a dragged event
            #the atom coordinate projection should be updated
            #since camera rotations only, the acpRadii does not need updating
            self._updateACP(updateRadii=False)
            return
        
        try:
            controlPressed = (event.modifiers[0] == CONTROL)
        except IndexError:
            #no key is pressed
            controlPressed = False
        atom2bSelected = self._selectedAtomIndex(event.pos)

        if atom2bSelected is None:
                #the single click occurs at a blank area
                self.resetSelection() 

        elif controlPressed:
            if atom2bSelected in self.selectedAtoms:
                #the atom has been selected and needs to be deselected
                self.deselectAtom(atom2bSelected)
            else:
                #the atom 2b selected is not selected
                self.selectAtom(atom2bSelected)

        else:
            self.resetSelection()
            self.selectAtom(atom2bSelected)

    def onMousePress(self,event: MouseEvent):
        self._recordCurEventPos(event)

    def onMouseWheel(self,event: MouseEvent):
        self._updateACP()

    def onResize(self,event: MouseEvent):
        self._updateACP()

    #camera linkage related methods
    @property
    def camera(self):
        return self.view.camera

    def linkViewer(self,otherViewer):
        self.camera.link(otherViewer.camera)

    def isLinkedTo(self,otherViewer):
        #Cheat a little bit and use the
        #_linked_cameras internal dictionary
        return (otherViewer.camera in self.camera._linked_cameras)

    def unlinkViewer(self,otherViewer):
        #Cheat a little bit and modify the
        #_linked_cameras internal dictionary
        if self.isLinkedTo(otherViewer):
            del self.camera._linked_cameras[otherViewer.camera]

        if otherViewer.isLinkedTo(self):
            del otherViewer.camera._linked_cameras[self.camera]

    def unlinkAllViewers(self):
        #Cheat a little bit and modify the
        #_linked_cameras internal dictionary
        for cam in self.camera._linked_cameras.keys():
            del cam._linked_cameras[self.camera]
        self.camera._linked_cameras.clear()
            
        

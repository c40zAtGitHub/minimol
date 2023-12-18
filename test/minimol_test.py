from minimol import MolViewer
from vispy import app
import numpy as np
if __name__=='__main__':
    #read test molecule from MEA.xyz
    with open("MEA.xyz") as f:
        fc = f.read()

    fclines = fc.splitlines()
    molecule = []
    for line in fclines[2:]:
        ele,x,y,z = line.split()
        atom = (ele,float(x),float(y),float(z))
        molecule.append(atom)
    #print(molecule)
    bonds = [(0,1),(0,2),(0,3),(0,9),(3,4),(3,5),(3,6),(6,7),(6,8),
             (9,10)]

    #cviewer = MolViewer(molecule)
    #cviewer.title = "Coordinate of 1.0"
    #cameraDir = cviewer.view.camera.transform.matrix
    #print(cameraDir)
    #print(dir(cviewer.view.camera.transforms))
    #transform = cviewer._atomVis.transforms.get_transform('visual','canvas')
    #print(transform)
    #print(transform.imap(np.array([375,300])))

    viewer = MolViewer(molecule,atomCons=bonds)
    viewer.title = "Molecule 1"
    #print(viewer.connectivity)
    viewer.selectAtom(0)
    #viewer.deselectAtom(0)
    #print(dir(viewer._atomVis))
    #viewer.redrawMolecule()
    #viewer2 = MolViewer(molecule,atomCons=bonds)
    #viewer2.title = "Molecule 2"
    #viewer.view.camera.link(viewer2.view.camera)
    app.run()

    

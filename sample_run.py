#A sample test file to get minimol running
#the molecule in the demo is methylethanolamine
#For alpha 0.1 version, you can do dragging operations as is done in most molecule visualization software
#Atom selection is also supported.


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
    bonds = [(0,1),(0,2),(0,3),(0,9),(3,4),(3,5),(3,6),(6,7),(6,8),
             (9,10)]

    viewer = MolViewer(molecule,atomCons=bonds)
    viewer.title = "Methylethanolamine"
    app.run()

    

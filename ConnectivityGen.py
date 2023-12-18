import numpy as np

from minimol.ElementData import atomSymbols,vdWRadii

def genConnectivity(atomCoords,thresh=1.0):
    #atomCoords - a list of tuples of (element,x,y,z)
    nAtom = len(atomCoords)
    conAtoms = []

    #prepare the entry data for iteration
    aElement = []
    aCoords = []
    for acEntry in atomCoords:
        ele,x,y,z = acEntry
        coord = np.array([x,y,z])
        aElement.append(ele)
        aCoords.append(coord)

    for i in range(nAtom):
        for j in range(i+1,nAtom):
            rij = np.linalg.norm(aCoords[j]-aCoords[i])
            vdWi = vdWRadii[aElement[i]]
            vdWj = vdWRadii[aElement[j]]
            vdWSum = vdWi + vdWj
            if rij < thresh * vdWSum:
                conAtoms.append((i,j))
    return conAtoms
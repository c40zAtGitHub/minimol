import numpy as np

from .ElementData import atomSymbols,vdWRadii
from .ElementData.BondLength import singleBondLength

def genSingleBondByBLength(atomCoords):
    thresh = 1.02
    if atomCoords is None:
        return []
    nAtom = len(atomCoords)
    bonds = []

    #prepare the entry data for iteration
    aElement = [ac[0] for ac in atomCoords]
    aCoords = [np.array(ac[1:]) for ac in atomCoords]

    #do something to determine bond connection
    for i in range(nAtom):
        for j in range(i+1,nAtom):
            rij = np.linalg.norm(aCoords[j]-aCoords[i])
            eindex_i = atomSymbols.index(aElement[i]) + 1
            eindex_j = atomSymbols.index(aElement[j]) + 1
            emin = min(eindex_i,eindex_j)
            emax = max(eindex_i,eindex_j)
            try:
                eqBLength = singleBondLength[(emin,emax)]
            except KeyError:
                #if no data, no bond
                continue
            if rij < thresh * eqBLength:
                bonds.append((i,j,1.0))
    return bonds
    

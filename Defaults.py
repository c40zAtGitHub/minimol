#default means of data processing and plotting

from .ConnectivityGen import genSingleBondByBLength
from .Styles.AtomStyles import VDWStyle
from .Styles.BondStyles import PrimitiveStyle

#default way of generating connections between bonds
dftBondGenerator = lambda coords:genSingleBondByBLength(coords)

#default way of plotting atoms
#spheres of 0.25x the vdw radius of the element
dftAtomStyle = VDWStyle(scale=0.25)

#default way of plotting bonds
#cylinder of 0.1 radius
dftBondStyle = PrimitiveStyle(radius=0.1)


#selection related styles
dftHighlightColor = (0.9725,0.9882,0.5137) #light yellow
#dftHighlightColor = (1.0,1.0,1.0) #white
dftHighlightMargin = 0.05


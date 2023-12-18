#The van der Waals radii of the elements in Angstroms
#Taken from Mathematica's ElementData function from Wolfram Research, Inc.
#https://periodictable.com/Properties/A/VanDerWaalsRadius.v.html
#accessed Dec-11-2023

#note: dict in ElementSerial:vdWRadius format
from .AtomSymbols import atomSymbols

vdWRadiiBySerial = {
    1:1.20,
	2:1.40,
	3:1.82,
	6:1.70,
	7:1.55,
	8:1.52,
	9:1.47,
	10:1.54,
	11:2.27,
	12:1.73,
	14:2.10,
	15:1.80,
	16:1.80,
	17:1.75,
	18:1.88,
	19:2.75,
	28:1.63,
	29:1.40,
	30:1.39,
	31:1.87,
	33:1.85,
	34:1.90,
	35:1.85,
	36:2.02,
	46:1.63,
	47:1.72,
	48:1.58,
	49:1.93,
	50:2.17,
	52:2.06,
	53:1.98,
	54:2.16,
	78:1.75,
	79:1.66,
	80:1.55,
	81:1.96,
	82:2.02,
	92:1.86
}

#generate the symbol alternative
vdWRadiiBySymbol = {}
for key in vdWRadiiBySerial.keys():
    vdWRadiiBySymbol[atomSymbols[key-1]] = vdWRadiiBySerial[key]
    
#merge the serial and symbol dict
vdWRadii = vdWRadiiBySerial | vdWRadiiBySymbol
    

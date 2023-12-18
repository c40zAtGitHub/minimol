from minimol.ElementData import vdWRadiiBySymbol
from minimol.Styles.ElementColor import elementColor
from .BaseStyle import BaseStyle

class VDWStyle(BaseStyle):
    def __init__(self,scale) -> None:
        super().__init__()
        self.scale = scale

    def color(self,element):
        return elementColor[element]
    
    def radius(self,element):
        return self.scale * vdWRadiiBySymbol[element]
    

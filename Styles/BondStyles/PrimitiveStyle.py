import numpy as np
from .BaseStyle import BaseStyle

class PrimitiveStyle(BaseStyle):
    def __init__(self,radius=1.0) -> None:
        super().__init__()
        self.radius = radius
        self.color = np.array([0.5,0.5,0.5])


    
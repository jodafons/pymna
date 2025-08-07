
__all__ = [
          
            "transconductance",
            "conductance",
        ]

import numpy as np


def transconductance( A              : np.array,
                     nodeIn         : int,
                     nodeOut        : int,
                     controlNodeIn  : int,
                     controlNodeOut : int,
                     Gm             : float
                    ):
    A[nodeIn , controlNodeIn  ] +=  Gm
    A[nodeIn , controlNodeOut ] += -Gm
    A[nodeOut, controlNodeIn  ] += -Gm
    A[nodeOut, controlNodeOut ] +=  Gm

def conductance( A : np.array,
                nodeIn : int,
                nodeOut : int,
                G : float):
    transconductance(A, nodeIn, nodeOut, nodeIn, nodeOut, G)    

from . import element
__all__.extend( element.__all__ )
from .element import *

from . import sources
__all__.extend( sources.__all__ )
from .sources import *

from . import basics
__all__.extend( basics.__all__ )
from .basics import *

from . import amplifiers
__all__.extend( amplifiers.__all__ )
from .amplifiers import *

from . import semiconductors
__all__.extend( semiconductors.__all__ )
from .semiconductors import *

from . import gates
__all__.extend( gates.__all__ )
from .gates import *


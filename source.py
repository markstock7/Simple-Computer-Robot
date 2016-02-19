import sys
import os
path = os.getcwd()+"/source"
if not path in sys.path:
    sys.path.append(path)
from dytt8 import *
from youku import *


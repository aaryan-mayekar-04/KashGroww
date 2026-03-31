import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import recommend as r
print('recommend file:', r.__file__)
print('models_loaded', getattr(r, 'models_loaded', 'missing'))

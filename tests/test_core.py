import sys
import os

sys.path.append(os.path.split(sys.path[0])[0])

from src.core.swan import comment_swan_main, Swan

comment_swan_main()

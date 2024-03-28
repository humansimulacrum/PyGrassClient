import sys

from loguru import logger

from PyGrassClient import run_by_file

logger.remove() 

logger.add(sys.stdout, level="INFO") 

run_by_file('accounts.txt')

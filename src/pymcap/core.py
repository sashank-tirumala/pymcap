import pymcap.binaries
from pathlib import Path
import subprocess

class PyMCAP():
    def __init__(self):
        
        self.executable = (Path(__file__).parent / "binaries/linux_amd64/mcap").resolve()
        self.__version = subprocess.run([str(self.executable), "version"], stdout=subprocess.PIPE).stdout.decode("utf-8")
    
    @property
    def version(self):
        return self.__version

if __name__ == "__main__":
    p = PyMCAP()
    print(p.version)

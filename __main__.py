"""
Deze Applicatie verzorgd een koppeling tussen:
* Radio Audtomatisering
* MySQL Database
* FTP Server
Daarnaast word een XML gegenereerd voor koppeling Website -> Fileserver
Deel van commentaar volgt in het Engels, statussen worden in het Nederlands gegeven.
"""

__version__ = '1.1'
__author__ = 'Sander Post'

import threading
from Model import Model
from Interface import Interface


class Application:
    def __init__(self):
        self.model = Model()
        main = threading.Thread(target=self.model.job_scheduler)
        ui = Interface(self.model)
        main.start()
        ui.mainloop()

if __name__ == "__main__":
    Application()


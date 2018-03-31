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

import datetime
import tzlocal
import tkinter as tk


class Interface(tk.Tk):

    def __init__(self, model):
        self.model = model
        tk.Tk.__init__(self)
        self.winfo_toplevel().title('Uitzending Gemist')
        self.clock = tk.Label(self, text="")
        self.clock.configure(width=15, font=('Courier', 40))
        self.clock.pack(fill=tk.X, expand=True)
        self.status = tk.Label(self, text="")
        self.status.configure(font=('Courier', 10))
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

        self.update_clock()
        self.update_status(model)

    def update_clock(self):
        now = datetime.datetime.strftime(datetime.datetime.fromtimestamp(datetime.datetime.now().timestamp(),
                                                                         tzlocal.get_localzone()), '%H:%M:%S')
        self.clock.configure(text=now)
        self.after(1000, self.update_clock)

    def update_status(self, model):
        self.status.configure(text=model.status)
        print(model.status)
        self.after(5000, self.update_status, model)

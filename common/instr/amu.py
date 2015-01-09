#######################################################################################################################
#
# amu instrument driver class
#
#######################################################################################################################

import cmu

from cmu import rohde_and_schwarz_CMW500 as rohde_and_schwarz_CMW500

class Amu(cmu.CmuControl):
    def __init__(self, name,ip_addr='10.21.141.74'):
        self.name = name
        self.dev = rohde_and_schwarz_CMW500(ip_addr, timeout=20)
        self.dev.write("*cls")

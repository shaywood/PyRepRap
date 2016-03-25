# Library to abstract over communicating with a Duet (or any other platform)
# running the ZPL fork of the RepRapFirmware - ie: with Telnet and FTP support
# This is done so that manual control through the web interface remains open (although
# caution should be exercised to not issue conflicting instructions).

# To use: create a new RepRap object
# This exposes a number of methods which enable you to control the printer
# All control is done through the Telnet connection (simplest)
# All file upload is done using a background thread and FTP (best performance)

import Telnet from telnetlib

class RepRap:
    def __init__(host, telnet_port = 23, ftp_port = 21):
        """
        Constructs a new RepRap object, connecting via Telnet and FTP to the given host, on the 
        default ports for the respective services, unless overridden.
        """
        self.telnet = Telnet.open(host, telnet_port)

    def sendRawGCode(self, gcode):
        telnet.write(gcode)

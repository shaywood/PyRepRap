# Library to abstract over communicating with a Duet (or any other platform)
# running the ZPL fork of the RepRapFirmware - ie: with Telnet and FTP support
# This is done so that manual control through the web interface remains open (although
# caution should be exercised to not issue conflicting instructions).

# To use: create a new RepRap object
# This exposes a number of methods which enable you to control the printer
# All control is done through the Telnet connection (simplest)
# All file upload is done using a background thread and FTP (best performance)

from __future__ import print_function

import telnetlib
import json

class RepRap:
    """
    Class that wraps a Telnet connection linking to a ZPL/CH fork of the RepRapFirmware.
    """
    def __init__(self, host, telnet_port = 23, ftp_port = 21):
        """
        Constructs a new RepRap object, connecting via Telnet and FTP to the given host, on the 
        default ports for the respective services, unless overridden.
        """
        self.telnet = telnetlib.Telnet(host, telnet_port)

    def __del__(self):
        self.telnet.close()

    def _sendRawGCode(self, gcode):
        """
        Writes the string provided to the telnet connection.
        Whilst this method can be accessed from outside this class, it is not recommended.
        A single line of response can be read using _readResponse()

        :param gcode The gcode to send, do not forget a trailing newline!
        """
        #print("Sending " + gcode)
        self.telnet.write(gcode)

    def _readResponse(self, timeout = 10):
        """
        Reads one line from the telnet connection. Times out after 10 seconds, can be altered
        with the timeout parameter. Can raise EOFError.
        Whilst this method can be accessed from outside this class, it is not recommended.
        A single line of input GCode can be sent using _sendRawGCode()

        :timeout Timeout in seconds
        """
        s = self.telnet.read_until('\n', timeout)

        #print("Received: " + s)

        return s.strip("\r\n")

    def hashFile(self, filepath):
        """
        Invokes M38 (Compute SHA1 hash) on filepath
        Returns the result as a string.
        If the result is empty, then the file does not exist, or could not be hashed.
        This method has a two minute timeout, as hashing large files can take time
        """
        self._sendRawGCode("M38 " + filepath + "\n")
        s = self._readResponse(timeout = 120)

        if s.startswith("Error:"):
            # Can get system generated messages, which we do not want to return
            s = self._readResponse()

        if s.startswith("Cannot find file"):
            return ''

        return s

    def printFile(self, filepath):
        """
        Invokes M32 (select file and start SD print) on filepath
        Moves the printer into a printing status, which can be tested for with isPrinting(),
        although that simply uses the getStatusResponse() method.
        """
        self._sendRawGCode("M32 " + filepath + "\n")

    def getStatusResponse(self, level = 2):
        """
        Invokes M408 (report JSON-style response)
        The level defaults to 2 (because lower levels don't parse properly!), 
        but can be increased by providing an int argument

        Returns a the result of json.loads(), unless there was a problem, in which case None
        is returned
        
        :param level (optional) an int between 0 and 5
        """
        level = min(level, 2)

        self._sendRawGCode("M408 S" + str(level) + "\n")

        jsonStr = self._readResponse()

        if (jsonStr == ''):
            return None

        return json.loads(jsonStr)
    
    def isPrinting(self):
        status = self.getStatusResponse()

        if status is None:
            return False
        else:
            return status['status'] == 'P'

class Version:

    @staticmethod
    def BFVer():
        return "0.0.1"

    @staticmethod
    def OFVer():
        return "3.2"


class Header:
    """Input files header
        Usage:
            print Header.get_header()
    """

    @staticmethod
    def get_header():

        header ="*---------------------------------*- C++ -*-----------------------------------*\n" + \
                "|   '\ /'   |                                                                 |\n" + \
                "|  |\ | /|  | Butterfly : An Open Source Python API + Interface for OpenFOAM  |\n" + \
                "|  |-*|*-|  |                                                                 |\n" + \
                "|  |/ | \|  | Version: -                                                      |\n" + \
                "|     *     | Web:          https://github.com/mostaphaRoudsari/Butterfly/    |\n" + \
                "*-----------------------------------------------------------------------------*\n"
        return header

# coding=utf-8
"""Butterfly core library."""
import os
from shutil import rmtree
from distutils.dir_util import copy_tree
from collections import namedtuple
from copy import deepcopy

from .version import Version
from .utilities import mkdir, wfile, runbatchfile, readLastLine, loadSkippedProbes, \
    checkFiles

# constant folder objects
from .turbulenceProperties import TurbulenceProperties
from .RASProperties import RASProperties
from .transportProperties import TransportProperties
from .g import G

# 0 folder objects
from .U import U
from .k import K
from .p import P
from .nut import Nut
from .epsilon import Epsilon
from .T import T
from .alphat import Alphat
from .p_rgh import P_rgh
from .conditions import ABLConditions, InitialConditions

# system folder objects
from .blockMeshDict import BlockMeshDict
from .controlDict import ControlDict
from .snappyHexMeshDict import SnappyHexMeshDict
from .fvSchemes import FvSchemes
from .fvSolution import FvSolution
from .functions import Probes

from runmanager import RunManager


class OpemFOAMCase(object):
    """Butterfly case."""
    # goes in utilities/utility folder
    @staticmethod
    def loadProbesFromProjectPath(projectPath, field, probesFolder='probes'):
        """Return OpenFOAM probes results for a field.

        Args:
            projectPath: Path to project root folder.
            field: Probes field (e.g. U, p, T).
        """
        # find probes folder
        _basepath = os.path.join(projectPath, 'postProcessing', probesFolder)

        if not os.path.isdir(_basepath):
            print "Failed to find postProcessing folder at {}".format(_basepath)
            return

        folders = [os.path.join(_basepath, f) for f in os.listdir(_basepath)
                   if (os.path.isdir(os.path.join(_basepath, f)) and
                       f.isdigit())]

        # sort based on last modified
        folders = sorted(folders, key=lambda folder:
                         max(tuple(os.stat(os.path.join(folder, f)).st_mtime
                                   for f in os.listdir(folder))))

        # load the last line in the file
        _f = os.path.join(_basepath, str(folders[-1]), field)

        assert os.path.isfile(_f), 'Cannot find {}!'.format(_f)
        _res = readLastLine(_f).split()[1:]

        # convert values to tuple or number
        _rawres = tuple(d.strip() for d in readLastLine(_f).split()
                        if d.strip())[1:]

        try:
            # it's a number
            _res = tuple(float(r) for r in _rawres)
        except ValueError:
            try:
                # it's a vector
                _res = tuple(eval(','.join(_rawres[3 * i: 3 * (i + 1)]))
                             for i in range(int(len(_rawres) / 3)))
            except Exception as e:
                raise Exception('\nFailed to load probes:\n{}'.format(e))

        return _res

    # goes under Solution/ not meaningful before running the case
    def loadProbes(self, field):
        """Return OpenFOAM probes results for a field."""
        if self.probes.probesCount == 0:
            return []

        if field not in self.probes.fields:
            raise ValueError("Can't find {} in {}.".format(field,
                                                           self.probes.fields))

        self.loadProbesFromProjectPath(
            self.projectDir, field, self.probes.filename)

    # goes under Solution/ need to know the command to look for
    def loadSkippedProbes(self):
        """Get list of probes that are skipped in calculation."""
        return loadSkippedProbes(os.path.join(self.projectDir, 'etc', 'simpleFoam.log'))


    # *************************       START       ************************* #
    # ************************* OpenFOAM Commands ************************* #
    # goes under Solution
    def simpleFoam(self, args=None, decomposeParDict=None, run=True, wait=True):
        """Run simpleFoam command for this case.

        Returns:
            A tuple as (success, err). success is a boolen. err is None in case
            of success otherwise the error message as a string.
        """
        return self.__writeAndRunCommands('simpleFoam', 'simpleFoam', args,
                                          decomposeParDict, run, wait)

    # goes under Solution
    def buoyantBoussinesqSimpleFoam(self, args=None, decomposeParDict=None,
                                    run=True, wait=True):
        """Run buoyantBoussinesqSimpleFoam command for this case.

        Returns:
            A tuple as (success, err). success is a boolen. err is None in case
            of success otherwise the error message as a string.
        """
        return self.__writeAndRunCommands('buoyantBoussinesqSimpleFoam',
                                          'buoyantBoussinesqSimpleFoam', args,
                                          decomposeParDict, run, wait)

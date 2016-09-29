"""Butterfly core library."""
import os
from shutil import rmtree
from distutils.dir_util import copy_tree
from collections import namedtuple

from version import Version
from helper import mkdir, wfile, runbatchfile, readLastLine, loadSkippedProbes, \
    checkFiles
# constant folder objects
from turbulenceProperties import TurbulenceProperties
from RASProperties import RASProperties
from transportProperties import TransportProperties

# 0 folder objects
from U import U
from k import K
from p import P
from nut import Nut
from epsilon import Epsilon
from conditions import ABLConditions, InitialConditions

# system folder objects
from blockMeshDict import BlockMeshDict
from controlDict import ControlDict
from snappyHexMeshDict import SnappyHexMeshDict
from fvSchemes import FvSchemes
from fvSolution import FvSolution

from runmanager import RunManager


class CaseFoldersNotCreatedError(Exception):
    """Exception."""

    _msg = 'You need to creat folders before generating the contents.\n' + \
           'Use `createCaseFolders` method to creat the project and try again.'

    def __init__(self):
        """Init Exception."""
        Exception.__init__(self, self._msg)


class OpemFOAMCase(object):
    """Butterfly case."""

    def __init__(self, projectName, BFGeometries, blockMeshDict,
                 globalRefinementLevel=None, locationInMesh=None,
                 isSnappyHexMesh=False):
        """Init project."""
        self.username = os.getenv("USERNAME")
        self.version = float(Version.OFVer)
        self.projectName = projectName
        self.runmanager = RunManager(self.projectName)
        self.BFGeometries = BFGeometries

        # meshing - constant
        self.blockMeshDict = blockMeshDict

        # meshing - system
        self.isSnappyHexMesh = isSnappyHexMesh
        self.snappyHexMeshDict = SnappyHexMeshDict.fromBFGeometries(
            projectName, BFGeometries, globalRefinementLevel, locationInMesh)

        # place holder for refinment regions
        self.__refinementRegions = []

        # constant folder
        if self.version < 3:
            self.RASProperties = RASProperties()
        else:
            self.turbulenceProperties = TurbulenceProperties()
        self.transportProperties = TransportProperties()

        # 0 floder
        self.u = U.fromBFGeometries(BFGeometries + blockMeshDict.BFBlockGeometries)
        self.p = P.fromBFGeometries(BFGeometries + blockMeshDict.BFBlockGeometries)
        self.k = K.fromBFGeometries(BFGeometries + blockMeshDict.BFBlockGeometries)
        self.epsilon = Epsilon.fromBFGeometries(BFGeometries +
                                                blockMeshDict.BFBlockGeometries)
        self.nut = Nut.fromBFGeometries(BFGeometries + blockMeshDict.BFBlockGeometries)

        # system folder
        self.fvSchemes = FvSchemes()
        self.fvSolution = FvSolution()

        self.controlDict = ControlDict()
        self.probes = None

        # if any of these files are included they should be written to 0 floder
        self.ABLConditions = None
        self.initialConditions = None

        self._isInit = False
        self._isSnappyHexMeshFoldersRenamed = False

    @classmethod
    def fromWindTunnel(cls, windTunnel):
        """Create case from wind tunnel."""
        _blockMeshDict = windTunnel.blockMeshDict
        _locationInMesh = _blockMeshDict.center

        _case = cls(windTunnel.name, windTunnel.testGeomtries, _blockMeshDict,
                    globalRefinementLevel=windTunnel.globalRefLevel,
                    locationInMesh=_locationInMesh, isSnappyHexMesh=True,
                    )

        _case.initialConditions = InitialConditions(
            Uref=windTunnel.flowSpeed, Zref=windTunnel.Zref, z0=windTunnel.z0)

        _case.ABLConditions = ABLConditions.fromWindTunnel(windTunnel)

        # edit files in 0 folder
        _case.u.updateValues({'#include': '"initialConditions"',
                             'internalField': 'uniform $flowVelocity'})
        _case.p.updateValues({'#include': '"initialConditions"',
                             'internalField': 'uniform $pressure'})
        _case.k.updateValues({'#include': '"initialConditions"',
                             'internalField': 'uniform $turbulentKE'})
        _case.epsilon.updateValues({'#include': '"initialConditions"',
                                    'internalField': 'uniform $turbulentEpsilon'})

        if windTunnel.refinementRegions:
            for region in windTunnel.refinementRegions:
                _case.addRefinementRegion(region)

        return _case

    @classmethod
    def fromBlocks(cls, BFGeometries, blocks, scale):
        """Create case from BFGeometries and blocks.

        This case will only be meshed using blockMesh
        """
        raise NotImplementedError("Let us know if you in real need for this method!")

        _blockMeshDict = BlockMeshDict(scale, BFGeometries, blocks)
        return cls(BFGeometries, _blockMeshDict, isSnappyHexMesh=False)

    @property
    def isInitialConditionsIncluded(self):
        """Check if initialConditions file is included in this case."""
        return self.__isInitialConditionsIncluded

    @property
    def initialConditions(self):
        """Get initialConditions."""
        return self.__initialConditions

    @initialConditions.setter
    def initialConditions(self, value):
        if not value:
            self.__initialConditions = None
            self.__isInitialConditionsIncluded = False
        else:
            self.__initialConditions = value
            self.__isInitialConditionsIncluded = True

    @property
    def isABLConditionsIncluded(self):
        """Check if ABLConditions file is included in this case."""
        return self.__isABLConditionsIncluded

    @property
    def ABLConditions(self):
        """Get ABLConditions."""
        return self.__ABLConditions

    @ABLConditions.setter
    def ABLConditions(self, value):
        if not value:
            self.__ABLConditions = None
            self.__isABLConditionsIncluded = False
        else:
            self.__ABLConditions = value
            self.__isABLConditionsIncluded = True

    @property
    def refinementRegions(self):
        """Get refinement regions."""
        return self.__refinementRegions

    @property
    def probes(self):
        """Get and set Probes."""
        return self.__probes

    @probes.setter
    def probes(self, inp):
        if not inp:
            self.__probes = inp
        else:
            assert hasattr(inp, 'probeLocations'), \
                "Expected Probes not {}".format(type(inp))

            self.__probes = inp
            # include probes in controlDict
            self.controlDict.include(self.probes.filename)

    @staticmethod
    def loadProbesFromProjectPath(projectPath, field, probesFolder='probes'):
        """Return OpenFOAM probes results for a field.

        Args:
            projectPath: Path to project root folder.
            field: Probes field (e.g. U, p, T).
        """
        # find probes folder
        _basepath = os.path.join(projectPath, 'postProcessing', probesFolder)

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

    def loadProbes(self, field):
        """Return OpenFOAM probes results for a field."""
        if not self.probes:
            return []

        if field not in self.probes.fields:
            raise ValueError("Can't find {} in {}.".format(field,
                                                           self.probes.fields))

        self.loadProbesFromProjectPath(
            self.projectDir, field, self.probes.filename)

    def loadSkippedProbes(self):
        """Get list of probes that are skipped in calculation."""
        return loadSkippedProbes(os.path.join(self.projectDir, 'etc', 'simpleFoam.log'))

    def loadMesh(self):
        """Return OpenFOAM mesh as a Rhino mesh."""
        # This is a abstract property which should be implemented in subclasses
        raise NotImplementedError()

    def loadPoints(self):
        """Return OpenFOAM mesh as a Rhino mesh."""
        # This is a abstract property which should be implemented in subclasses
        raise NotImplementedError()

    def loadVelocity(self, timestep=None):
        """Return OpenFOAM mesh as a Rhino mesh."""
        # This is a abstract property which should be implemented in subclasses
        raise NotImplementedError()

    def addRefinementRegion(self, refinementRegion):
        """Add refinement regions to this case."""
        assert hasattr(refinementRegion, 'isRefinementRegion'), \
            "{} is not a refinement region.".format(refinementRegion)

        self.__refinementRegions.append(refinementRegion)
        self.snappyHexMeshDict.addRefinementRegion(refinementRegion)

    def createCaseFolders(self, workingDir=None):
        """Create project folders and subfolders.

        Args:
            projectName: A valid name for project. Avoid whitespace and special
                charecters.
            workingDir: By default workingDir for Butterfly files will be under
            "users/<username>/butterfy/". Do not change the folder unless you
            need to save the files in a different folder. OpenFOAM for windows
            uses "users/<username>" folder to share data.
        """
        # This method will be only useful on new systems
        self.__createCaseFolder(self.projectName, workingDir)

        # Create sub folders (0, constant, system)
        self.__createSubFolders()

        # create an empty project file
        _foamFile = os.path.join(self.projectDir, "%s.foam" % self.projectName)
        with open(_foamFile, "wb") as outf:
            outf.close()

        self._isInit = True
        print "OpenFOAM Case is successfully exported to: %s" % os.path.normpath(self.projectDir)

    def __createCaseFolder(self, projectName, workingDir=None):
        """Create root folder for butterfly projects."""
        self.workingDir = "c:/users/%s/butterfly/" % self.username \
            if not workingDir \
            else workingDir
        self.projectDir = os.path.join(self.workingDir, self.projectName)
        mkdir(self.workingDir)
        mkdir(self.projectDir)

    def __createSubFolders(self):
        """Create subfolders (0, constant, system) under case folder."""
        # create constant directory
        constantDir = os.path.join(self.projectDir, "constant")
        self.constantDir = mkdir(constantDir)

        # create polyMesh folder under contstant
        mkdir(os.path.join(self.constantDir, "polyMesh"))
        if self.isSnappyHexMesh:
            mkdir(os.path.join(self.constantDir, "triSurface"))

        # create system directory
        systemDir = os.path.join(self.projectDir, "system")
        self.systemDir = mkdir(systemDir)

        # create time directory
        zeroDir = os.path.join(self.projectDir, "0")
        self.zeroDir = mkdir(zeroDir)

        # create etc directory for .sh fils
        etcDir = os.path.join(self.projectDir, "etc")
        self.etcDir = mkdir(etcDir)

    def populateContents(self):
        """Populate all the files for this case under case folder."""
        self.populateZeroContents()
        self.populateConstantContents()
        self.populateSystemContents()

    def populateConstantContents(self):
        """Write constant folder files."""
        if not self._isInit:
            raise CaseFoldersNotCreatedError()

        # write stl files to triSurface
        # for geometry in self
        if self.isSnappyHexMesh:
            # collect stl strings
            _stl = (BFGeometry.toStlString() for BFGeometry in self.BFGeometries)
            # write stl to stl file
            with open(os.path.join(self.constantDir,
                                   "triSurface\\%s.stl" % self.projectName),
                      'wb') as outf:
                outf.write("\n\n".join(_stl))

        if self.refinementRegions:
            for region in self.refinementRegions:
                with open(
                    os.path.join(self.constantDir,
                                 "triSurface\\%s.stl" % region.name), 'wb') as outf:

                    outf.write(region.toStlString())

        if self.version < 3:
            # write blockMeshDict to polyMesh
            self.blockMeshDict.save(self.projectDir, 'constant\\polyMesh')
            self.RASProperties.save(self.projectDir)
        else:
            self.turbulenceProperties.save(self.projectDir)

        self.transportProperties.save(self.projectDir)

    def populateZeroContents(self):
        """Write 0 folder files."""
        if not self._isInit:
            raise CaseFoldersNotCreatedError()

        if self.isInitialConditionsIncluded:
            self.initialConditions.save(self.projectDir)
        if self.isABLConditionsIncluded:
            self.ABLConditions.save(self.projectDir)
        self.u.save(self.projectDir)
        self.p.save(self.projectDir)
        self.k.save(self.projectDir)
        self.epsilon.save(self.projectDir)
        self.nut.save(self.projectDir)

    def populateSystemContents(self):
        """Write system folder files."""
        if not self._isInit:
            raise CaseFoldersNotCreatedError()

        if not self.version < 3:
            # for version +3 blockMeshDict is moved under system
            self.blockMeshDict.save(self.projectDir)

        self.snappyHexMeshDict.save(self.projectDir)
        self.controlDict.save(self.projectDir)
        self.fvSchemes.save(self.projectDir)
        self.fvSolution.save(self.projectDir)

    # *************************       START       ************************* #
    # ************************* OpenFOAM Commands ************************* #
    def blockMesh(self, args=None, removeContent=True, run=True, wait=True):
        """Run meshBlock command for this case.

        Args:
            removeContent: Remove current content of the folder

        Returns:
            A tuple as (success, err). success is a boolen. err is None in case
            of success otherwise the error message as a string.
        """
        if removeContent:
            self.removePolyMeshContent()

        return self.__writeAndRunCommands('blockMesh', 'blockMesh', args, None,
                                          run, wait)

    def snappyHexMesh(self, args=None, decomposeParDict=None, run=True, wait=True):
        """Run snappyHexMesh command for this case."""
        return self.__writeAndRunCommands('snappyHexMesh', 'snappyHexMesh',
                                          args, decomposeParDict, run, wait)

    def checkMesh(self, args=None, decomposeParDict=None, run=True, wait=True):
        """Run simpleFoam command for this case.

        Returns:
            A tuple as (success, err). success is a boolen. err is None in case
            of success otherwise the error message as a string.
        """
        return self.__writeAndRunCommands('checkMesh', 'checkMesh', args,
                                          decomposeParDict, run, wait)

    def simpleFoam(self, args=None, decomposeParDict=None, run=True, wait=True):
        """Run simpleFoam command for this case.

        Returns:
            A tuple as (success, err). success is a boolen. err is None in case
            of success otherwise the error message as a string.
        """
        return self.__writeAndRunCommands('simpleFoam', 'simpleFoam', args,
                                          decomposeParDict, run, wait)

    # ************************* OpenFOAM Commands ************************* #
    # *************************        END        ************************* #

    def isPolyMeshSnappyHexMesh(self):
        """Check if the mesh in polyMesh folder is snappyHexMesh."""
        return len(os.listdir(os.path.join(self.constantDir, "polyMesh"))) > 5

    def __writeAndRunCommands(self, name, command, args=None,
                              decomposeParDict=None, run=True, wait=True):
        """Write batch files for commands and run them.

        returns:
            If run it reaturns a namedtuple.
                (success, error, process, logfiles, errorfiles).
                success: as a boolen.
                error: None in case of success otherwise the error message as
                    a string.
                process: Popen process.
                logfiles: List of fullpath to log files.
                errorfiles: List of fullpath to error files.
        """
        log = namedtuple('log', 'success error process logfiles errorfiles')

        if decomposeParDict:
            decomposeParDict.save(self.projectDir)

        _batchString, logfiles, errfiles = self.runmanager.command(
            command, args, decomposeParDict=decomposeParDict, includeHeader=True
        )

        _fpath = os.path.join(self.etcDir, '%s.bat' % name)

        # write batch file to drive
        wfile(_fpath, _batchString)

        # generate fullpath for files
        logfiles = tuple(os.path.normpath(os.path.join(self.etcDir, f))
                         for f in logfiles)

        errfiles = tuple(os.path.normpath(os.path.join(self.etcDir, f))
                         for f in errfiles)

        if run:

            p = runbatchfile(_fpath, wait=wait)

            if p.poll:
                # if the analysis is over check log files and error files
                checkFiles(logfiles)
                success, err = checkFiles(errfiles)
                return log(success, err, p, logfiles, errfiles)
            else:
                # analysis is still running return Popen process
                return log(True, None, p, logfiles, errfiles)
        else:
            return log(True, None, None, logfiles, errfiles)

    def getSnappyHexMeshFolders(self):
        """Return sorted list of numerical folders."""
        _f = [int(name) for name in os.listdir(self.projectDir)
              if (name.isdigit() and
                  os.path.isdir(os.path.join(self.projectDir,
                                             name, 'polyMesh'))
                  )]

        _f.sort()

        return tuple(str(f) for f in _f)

    def getResultFolders(self):
        """Return sorted list of numerical folders."""
        _f = [int(name) for name in os.listdir(self.projectDir)
              if (name != '0' and name.isdigit() and
                  os.path.isdir(os.path.join(self.projectDir, name)) and
                  not os.path.isdir(os.path.join(self.projectDir, name, 'polyMesh'))
                  )]

        _f.sort()

        return tuple(str(f) for f in _f)

    def copySnappyHexMesh(self, folderNumber=None):
        """Copy the results of snappyHexMesh to constant/polyMesh."""
        # pick the last numerical folder
        if folderNumber:
            _s = os.path.join(self.projectDir, str(folderNumber), 'polyMesh')
            assert os.path.isdir(_s), "Can't find {}.".format(_s)
        else:
            _folders = self.getSnappyHexMeshFolders()
            if not _folders:
                return
            _s = os.path.join(self.projectDir, _folders[-1], 'polyMesh')

        _t = os.path.join(self.constantDir, "polyMesh")

        # copy files to constant/polyMesh
        try:
            copy_tree(_s, _t)
        except Exception as e:
            print "Failed to copy snappyHexMesh folder: {}".format(e)

    def renameSnappyHexMeshFolders(self):
        """Rename snappyHexMesh numerical folders to name.org  and vice versa."""
        # find list of folders in project and collect the numbers
        if self._isSnappyHexMeshFoldersRenamed:
            _folders = (name for name in os.listdir(self.projectDir)
                        if (name.endswith('.org') and
                        os.path.isdir(os.path.join(self.projectDir, name, 'polyMesh'))))

            for f in _folders:
                os.rename(os.path.join(self.projectDir, f),
                          os.path.join(self.projectDir, f.replace('.org', '')))

            self._isSnappyHexMeshFoldersRenamed = False
        else:
            _folders = self.getSnappyHexMeshFolders()

            # rename them starting from 1
            for f in _folders:
                try:
                    os.rename(os.path.join(self.projectDir, f),
                              os.path.join(self.projectDir, '%s.org' % f))
                except Exception as e:
                    raise Exception('Failed to rename snappyHexMesh folders: {}'.format(e))

            self._isSnappyHexMeshFoldersRenamed = True

    def removeSnappyHexMeshFolders(self):
        """Remove snappyHexMesh numerical folders.

        Use this to clean the folder.
        """
        if self._isSnappyHexMeshFoldersRenamed:
            _folders = (name for name in os.listdir(self.workingDir)
                        if (name.endswith('.org') and
                            os.path.isdir(os.path.join(self.workingDir, name))))
        else:
            _folders = self.getSnappyHexMeshFolders()

        for f in _folders:
            rmtree(os.path.join(self.projectDir, f))

        self._isSnappyHexMeshFoldersRenamed = False

    def removeResultFolders(self):
        """Remove results folder."""
        _folders = self.getResultFolders()
        for _f in _folders:
            try:
                rmtree(os.path.join(self.projectDir, _f))
            except Exception as e:
                print 'Failed to remove {}:\n{}'.format(_f, e)

    def removePostProcessingFolder(self):
        """Remove post postProcessing folder."""
        _f = os.path.join(self.projectDir, 'postProcessing')

        if not os.path.isdir(_f):
            return

        try:
            rmtree(_f)
        except Exception as e:
            print 'Failed to remove postProcessing folder:\n{}'.format(e)

    def removePolyMeshContent(self):
        """Remove results folder."""
        folder = os.path.join(self.constantDir, 'polyMesh')
        for _f in os.listdir(folder):
            if _f != 'blockMeshDict':
                _fp = os.path.join(folder, _f)
                if os.path.isfile(_fp):
                    os.remove(_fp)
                elif os.path.isdir(_fp):
                    rmtree(_fp)

    def purge(self, removePolyMeshContent=True,
              removeSnappyHexMeshFolders=True,
              removeResultFolders=False,
              removePostProcessingFolder=False):
        """Purge case folder."""
        if removePolyMeshContent:
            self.removePolyMeshContent()
        if removeSnappyHexMeshFolders:
            self.removeSnappyHexMeshFolders()
        if removeResultFolders:
            self.removeResultFolders()
        if removePostProcessingFolder:
            self.removePostProcessingFolder()

    # *************************** Post Process **************************** #
    def calculateMeshOrthogonality(self, useCurrntCheckMeshLog=False):
        """Max and average mesh orthogonality.

        If average values is more than 80, try to generate a better mesh.
        You can use this values to set discretization schemes.
        try case.setFvSchemes(averageOrthogonality)
        """
        if not useCurrntCheckMeshLog:
            log = self.checkMesh(args=('latestTime',))
            assert log.success, log.error

        f = os.path.join(self.projectDir, 'etc/checkMesh.log')
        assert os.path.isfile(f), 'Failed to find {}.'.format(f)

        with open(f, 'rb') as inf:
            results = ''.join(inf.readlines())

            maximum, average = results \
                .split('Mesh non-orthogonality Max:')[-1] \
                .split('average:')[:2]

            average = average.split('\n')[0]

        return float(maximum), float(average)

    def setFvSchemesfromMeshOrthogonality(self, meshOrthogonality):
        """Set fvSchemes based on mesh orthogonality.

        Check pp. 45-50 of this document:
        http://www.dicat.unige.it/guerrero/oftraining/9tipsandtricks.pdf
        """
        self.fvSchemes = FvSchemes.fromMeshOrthogonality(meshOrthogonality)

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """OpenFOAM CASE."""
        return "OpenFOAM CASE: %s" % self.projectName

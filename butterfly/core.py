"""Butterfly core library."""
import os
from distutils.dir_util import copy_tree
from version import Version
from helper import mkdir, wfile, runbatchfile
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
# system folder objects
from blockMeshDict import BlockMeshDict
from controlDict import ControlDict
from snappyHexMeshDict import SnappyHexMeshDict
from fvSchemes import FvSchemes
from fvSolution import FvSolution
from runmanager import RunManager


class CaseFoldersNotCreatedError(Exception):
    _msg = 'You need to creat folders before generating the contents.\n' + \
           'Use `createCaseFolders` method to creat the project and try again.'
    def __init__(self):
        Exception.__init__(self, self._msg)


class Case(object):
    """Butterfly case."""
    def __init__(self, projectName, BFSurfaces, blockMeshDict,
                 globalRefinementLevel=None, locationInMesh=None,
                 isSnappyHexMesh=False):
        """Init project."""
        self.username = os.getenv("USERNAME")
        self.version = float(Version.OFVer)
        self.projectName = projectName
        self.runmanager = RunManager(self.projectName)
        self.BFSurfaces = BFSurfaces

        # meshing - constant
        self.blockMeshDict = blockMeshDict

        # meshing - system
        self.isSnappyHexMesh = isSnappyHexMesh
        self.snappyHexMeshDict = SnappyHexMeshDict.fromBFSurfaces(
            projectName, BFSurfaces, globalRefinementLevel, locationInMesh)

        # constant folder
        if self.version < 3:
            self.RASProperties = RASProperties()
        else:
            self.turbulenceProperties = TurbulenceProperties()
        self.transportProperties = TransportProperties()

        # 0 floder
        self.u = U.fromBFSurfaces(BFSurfaces + blockMeshDict.BFSurfaces)
        self.p = P.fromBFSurfaces(BFSurfaces + blockMeshDict.BFSurfaces)
        self.k = K.fromBFSurfaces(BFSurfaces + blockMeshDict.BFSurfaces)
        self.epsilon = Epsilon.fromBFSurfaces(BFSurfaces + blockMeshDict.BFSurfaces)
        self.nut = Nut.fromBFSurfaces(BFSurfaces + blockMeshDict.BFSurfaces)

        # system folder
        self.fvSchemes = FvSchemes()
        self.fvSolution = FvSolution()

        self.controlDict = ControlDict()

        self._isInit = False
        self._isSnappyHexMeshFoldersRenamed = False


    @classmethod
    def fromBlocks(cls, BFSurfaces, blocks, scale):
        """Create case from BFSurfaces and blocks.

        This case will only be meshed using blockMesh
        """
        raise NotImplementedError("Not implemented yet!")
        _blockMeshDict = BlockMeshDict(scale, BFSurfaces, blocks)
        return cls(BFSurfaces, _blockMeshDict, isSnappyHexMesh=False)

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
        print "Folders are created at: %s" % os.path.normpath(self.projectDir)

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
        # for surface in self
        if self.isSnappyHexMesh:
            # collect stl strings
            _stl = (BFSurface.toStlString() for BFSurface in self.BFSurfaces)
            # write stl to stl file
            with open(os.path.join(self.constantDir,
                                   "triSurface\\%s.stl" % self.projectName),
                      'wb') as outf:
                outf.write("\n\n".join(_stl))

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

    # ************************* OpenFOAM Commands ************************* #
    def meshBlock(self, run=True):
        """Run meshBlock command for this case."""
        self.__writeAndRunCommands('blockMesh', ('blockMesh',), run)

    def snappyHexMesh(self, run=True):
        """Run snappyHexMesh command for this case."""
        self.__writeAndRunCommands('snappyHexMesh', ('snappyHexMesh',), run)

    def meshCombo(self, run=True):
        """Run meshBlock and snappyHexMesh."""
        self.__writeAndRunCommands('meshCombo',
                                   ('meshBlock', 'snappyHexMesh'),
                                   run)

    def simpleFoam(self, run=True):
        """Run simpleFoam command for this case."""
        self.__writeAndRunCommands('simpleFoam', ('simpleFoam',), run)

    def __writeAndRunCommands(self, name, commands, run=True):
        """Write batch files for commands and run them."""
        _batchString = self.runmanager.command(self.projectDir,
                                               commands,
                                               includeHeader=True)
        _fpath = os.path.join(self.etcDir, '%s.bat' % name)
        wfile(_fpath, _batchString)
        if run:
            runbatchfile(_fpath)

    def __getNumericalSubfolders(self):
        """Return sorted list of numerical folders."""
        _f = [int(name) for name in os.listdir(self.workingDir)
              if (name.isdigit() and
                  os.path.isdir(os.path.join(self.workingDir, name)))]

        _f.sort()

        return tuple(str(f) for f in _f)

    def copySnappyHexMesh(self, folderNumber=None):
        """Copy the results of snappyHexMesh to constant/polyMesh."""
        # pick the last numerical folder
        _folders = self.__getNumericalSubfolders()
        if len(_folders) < 2:
            # it is only o folder
            return

        _s = os.path.join(self.workingDir, _folders[-1], 'polyMesh')
        _t = os.path.join(self.constantDir, "polyMesh")

        # copy files to constant/polyMesh
        copy_tree(_s, _t)

    def renameSnappyHexMeshFolders(self):
        """Rename snappyHexMesh numerical folders to name.org  and vice versa."""
        # find list of folders in project and collect the numbers
        if self._isSnappyHexMeshFoldersRenamed:
            _folders = (name for name in os.listdir(self.workingDir)
                  if (name.endswith('.org') and
                      os.path.isdir(os.path.join(self.workingDir, name))))

            for f in _folders:
                os.rename(os.path.join(self.workingDir, f),
                          os.path.join(self.workingDir, f.replace('.org', '')))

            self._isSnappyHexMeshFoldersRenamed = False
        else:
            _folders = self.__getNumericalSubfolders()
            if len(_folders) < 2:
                # it is only o folder
                return

            # rename them starting from 1
            for f in _folders:
                if f == '0':
                    continue
                os.rename(os.path.join(self.workingDir, f),
                          os.path.join(self.workingDir, '%s.org' % f))

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
            _folders = self.__getNumericalSubfolders()[1:]

        for f in _folders:
            try:
                os.remove(f)
            except:
                print "Failed to remove %s." % f

        self._isSnappyHexMeshFoldersRenamed = False

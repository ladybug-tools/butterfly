"""Butterfly core library."""
import os
from helper import mkdir
# constant folder objects
from RASProperties import RASProperties
from transportProperties import TransportProperties
from blockMeshDict import BlockMeshDict
# 0 folder objects
from U import U
from k import K
from p import P
from nut import Nut
from epsilon import Epsilon
# system folder objects
from controlDict import ControlDict
from snappyHexMeshDict import SnappyHexMeshDict
from fvSchemes import FvSchemes
from fvSolution import FvSolution


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
        self.projectName = projectName
        self.BFSurfaces = BFSurfaces
        # meshing - constant
        self.blockMeshDict = blockMeshDict

        # meshing - system
        self.isSnappyHexMesh = isSnappyHexMesh
        self.snappyHexMeshDict = SnappyHexMeshDict.fromBFSurfaces(
            projectName, BFSurfaces, globalRefinementLevel, locationInMesh)

        # constant folder
        self.RASProperties = RASProperties()
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

    def populateContents(self):
        """Populate all the files for this case under case folder."""
        self.populateZeroContents()
        self.populateConstantContents()
        self.populateSystemContents()

    def populateConstantContents(self):
        """Write constant folder files."""
        if not self._isInit:
            raise CaseFoldersNotCreatedError()

        # write blockMeshDict to polyMesh
        self.blockMeshDict.save(self.projectDir)

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

        self.RASProperties.save(self.projectDir)
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

        self.snappyHexMeshDict.save(self.projectDir)
        self.controlDict.save(self.projectDir)
        self.fvSchemes.save(self.projectDir)
        self.fvSolution.save(self.projectDir)

"""Butterfly core library."""
import os
import solvers
from fields import BoundaryField as bouf
from blockMeshDict import BlockMeshDict

class Case(object):
    """Butterfly case."""
    def __init__(self, BFSurfaces, blockMeshDict, snappyHexMesh=False):
        """Init project."""
        self.username = os.getenv("USERNAME")
        self.BFSurfaces = BFSurfaces
        self.blockMeshDict = blockMeshDict
        self.snappyHexMesh = snappyHexMesh

    @classmethod
    def fromBlocks(cls, BFSurfaces, blocks, scale):
        """Create case from BFSurfaces and blocks.

        This case will only be meshed using blockMesh
        """
        _blockMeshDict = BlockMeshDict(scale, BFSurfaces, blocks)
        return cls(BFSurfaces, _blockMeshDict, snappyHexMesh=False)

    def write(self, projectName, workingDir=None):
        """Create project folders and write input files.

        Args:
            projectName: A valid name for project. Avoid whitespace and special
                charecters.
            workingDir: By default workingDir for Butterfly files will be under
            "users/<username>/butterfy/". Do not change the folder unless you
            need to save the files in a different folder. OpenFOAM for windows
            uses "users/<username>" folder to share data.
        """
        self.projectName = projectName
        self.workingDir = "c:/users/%s/butterfly/" % self.username if not workingDir \
                     else workingDir
        self.projectDir = os.path.join(self.workingDir, self.projectName)

        # This method will be only useful on new systems
        self.__createCaseFolder()
        # Create sub folders (0, constant, system)
        self.__createSubFolders()

        print "Files are exported to:\n%s" % os.path.normpath(self.projectDir)

    def __createCaseFolder(self):
        self.__createDir(self.workingDir)

    def __createSubFolders(self):
        # create constant directory
        constantDir = os.path.join(self.projectDir, "constant")
        self.constantDir = self.__createDir(constantDir)
        # create polyMesh folder under contstant
        self.__createDir(os.path.join(self.constantDir, "polyMesh"))

        if self.snappyHexMesh:
            self.__createDir(os.path.join(self.constantDir, "triSurface"))

        self.__writeConstantFiles()

        # create system directory
        systemDir = os.path.join(self.projectDir, "system")
        self.systemDir = self.__createDir(systemDir)

        # create time directory
        timestepDir = os.path.join(self.projectDir, "0")
        self.timestepDir = self.__createDir(timestepDir)
        # TODO: write velocity and pressure boundary condition
        # self.__writeFilesInZeroDir()

    def __writeConstantFiles(self):
        """write files in constant folder."""
        # write blockMeshDict to polyMesh
        self.blockMeshDict.save(os.path.join(self.constantDir, "polyMesh"))
        # write stl files to triSurface
        # for surface in self
        if self.snappyHexMesh:
            for BFSurface in self.BFSurfaces:
                BFSurface.writeToStl(os.path.join(self.constantDir, "triSurface"))

    @staticmethod
    def __createDir(directory, overwrite=True):
        if not os.path.isdir(directory):
            try:
                os.mkdir(directory)
            except Exception as e:
                raise ValueError("Failed to create %s:\n%s" % (directory, e))
        # TODO add one more step to ask for user permission
        # print "%s already existed! Files will be overwritten." % directory
        return directory

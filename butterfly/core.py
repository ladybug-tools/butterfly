import os
import solvers
from fields import BoundaryField as bouf

class BFProject:

    def __init__(self, projectName):
        self.projectName = projectName
        self.username = os.getenv("USERNAME")
        self.__solvers = []

    def createProject(self):
        """Create project folders and write input files

            workingDir for Butterfly files will be under
                    "users/username/butterfy/"

            OpenFOAM for windows uses users/username folder to share data

            projectDir will be set to:
                    "users/username/butterfy/projectName/"
        """

        # This method will be only useful on new systems
        self.__createWorkingDir()

        # Create porject folders (0, constant, system)
        self.__createProjectDir()

    def __createWorkingDir(self):
        baseDir = "c:/users/%s/butterfly/"%self.username
        self.workingDir = self.__createDir(baseDir)

    def __createProjectDir(self):
        projectDir = self.workingDir + self.projectName + "/"
        self.projectDir = self.__createDir(projectDir)
        self.__createSubFolders()

    def __createSubFolders(self):
        # create zero directory
        zeroDir = self.projectDir + "0/"
        self.zeroDir = self.__createDir(zeroDir)
        self.__writeFilesInZeroDir()

        # create constant directory
        constantDir = self.projectDir + "constant/"
        self.constantDir = self.__createDir(constantDir)

        # create system directory
        systemDir = self.projectDir + "system/"
        self.systemDir = self.__createDir(systemDir)

    def __writeFilesInZeroDir(self):
        for solver in self.__solvers:
            solver.writeToFile(self.zeroDir)

    # TODO: write files inside the folder
    def createConstantDir(self):
        pass

    # TODO: write files inside the folder
    def createSystemDir(self):
        pass

    @staticmethod
    def __createDir(directory, overwrite = True):
        if not os.path.isdir(directory):
            try:
                os.mkdir(directory)
            except:
                raise Exception("Failed to create %s"%directory)
        else:
            # TODO add one more step to ask for user permission
            print "%s already existed! Files will be overwritten"%directory

        return directory

    # TODO: Check the solver to be valid
    def add_solver(self, newSolver):
        """Add solver to the list of solvers"""
        solverNames = [solver.FoamFile.object for solver in self.__solvers]

        if newSolver.FoamFile.object not in solverNames:
            self.__solvers.append(newSolver)
        else:
            raise ValueError("%s already exist in project."%newSolver.FoamFile.object + \
            "\nUse Project.get_solverByName and update the solver")

    def get_solverByName(self, name):
        """Return solver by name"""
        try:
            return [solver for solver in self.__solvers if solver.FoamFile.object == name][0]
        except:
            raise Exception("%s is not a solver in this project.\n"%name + \
                "You can create additional solvers and add them to project using Project.addSolver")

    @property
    def solvers(self):
        names = [solver.FoamFile.object for solver in self.__solvers]
        return ", ".join(names)

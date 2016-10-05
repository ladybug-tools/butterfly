# coding=utf-8
"""Runmanager for butterfly.

Run manager is only useful for running OpenFOAM for Windows which runs in a
docker container. For linux systems simply use .bash files or libraries such as
pyFOAM.
"""
import os
from subprocess import PIPE, Popen
from collections import namedtuple
from copy import deepcopy

from .version import Version


class RunManager(object):
    """
    Butterfly RunManager class.

    Use this class to create files that are needed to run a case.
    """

    shellinit = None
    containerId = None

    def __init__(self, projectName):
        """Init run manager for project.

        Project path will be set to: C:/Users/%USERNAME%/butterfly/projectName
        """
        assert os.name == 'nt', "Currently RunManager is only supported on Windows."
        self.__projectName = projectName

        self.isUsingDockerMachine = True \
            if hasattr(Version, 'isUsingDockerMachine') and Version.isUsingDockerMachine \
            else False

        self.dockerPath = r'C:\Program Files\Docker Toolbox' \
            if self.isUsingDockerMachine \
            else r'C:\Program Files\Boot2Docker for Windows'

    def getShellinit(self):
        """Get shellinit for setting up initial environment for docker."""
        os.environ['PATH'] += ';%s' % r'C:\Program Files (x86)\Git\bin'
        os.environ['PATH'] += ';%s' % self.dockerPath

        if self.isUsingDockerMachine:
            # version 1606 and higher
            process = Popen('docker-machine env', shell=True, stdout=PIPE,
                            stderr=PIPE)
        else:
            # older versions are using boot2docker
            process = Popen('boot2docker shellinit', shell=True, stdout=PIPE,
                            stderr=PIPE)

        if tuple(process.stderr):
            print 'ERROR!'
            for line in process.stderr:
                print line
            # return

        return tuple(line.replace('$Env:', 'set ')
                     .replace(' = ', '=')
                     .replace('"', '').strip()
                     for line in process.stdout
                     if not line.startswith('REM'))

    def getContainerId(self):
        """Get OpenFOAM's container id."""
        _id = None
        if not self.shellinit:
            self.shellinit = self.getShellinit()

        # write a batch file
        _BFFolder = r"C:\Users\%s\butterfly" % os.environ['USERNAME']
        _batchFile = os.path.join(_BFFolder, 'getid.bat')
        with open(_batchFile, 'wb') as outf:
            outf.write("\n".join(self.shellinit))
            outf.write("\ndocker ps")

        p = Popen(_batchFile, shell=True, stdout=PIPE, stderr=PIPE)

        if tuple(p.stderr):
            for line in p.stderr:
                print line
            return

        for count, line in enumerate(p.stdout):
            if line.find('docker ps') > 0:
                # find container
                _id = next(line.split()[0] for line in p.stdout
                           if line.split()[-1].startswith('of_plus'))

        try:
            os.remove(_batchFile)
        except:
            pass
        finally:
            return _id

    def startOpenFOAM(self):
        """Start OpenFOAM for Windows image from batch file."""
        if Version.OFFullVer == 'v3.0+':
            fp = r"C:\Program Files (x86)\ESI\OpenFOAM\v3.0+\Windows\Scripts\start_OF.bat"
        else:
            fp = r"C:\Program Files (x86)\ESI\OpenFOAM\{}\\" + \
                "Windows\Scripts\start_OF.bat".format(Version.OFFullVer[1:-1])

        Popen(fp, shell=True)

    def header(self):
        """Get header for batch files."""
        if not self.shellinit:
            self.shellinit = self.getShellinit()

        _base = '@echo off\n' \
                'cd {}\n' \
                'echo Setting up the environment to connect to docker...\n' \
                'echo .\n' \
                '{}\n' \
                'echo Done!\n' \
                'echo Running OpenFOAM commands...\n' \
                'echo .'

        return _base.format(self.dockerPath, '\n'.join(self.shellinit))

    def command(self, cmd, args=None, decomposeParDict=None, includeHeader=True,
                startOpenFOAM=False):
        """
        Get command line for OpenFOAM commands.

        Args:
            cmd: An OpenFOAM command.
            args: List of optional arguments for command. e.g. ('c', 'latestTime')
            decomposeParDict: decomposeParDict for parallel runs (default: None).
            includeHeader: Include header lines to set up the environment
                (default: True).
            startOpenFOAM: Execute OpenFOAM in case it's not already running
                (default: False).

        Returns:
            (cmd, logfiles, errorfiles)
        """
        res = namedtuple('log', 'cmd logfiles errorfiles')

        if Version.OFFullVer == 'v3.0+':
            _fp = r"C:\Program Files (x86)\ESI\OpenFOAM\v3.0+\Windows\Scripts\start_OF.bat"
        else:
            _fp = r"C:\Program Files (x86)\ESI\OpenFOAM\{}\\" \
                "Windows\Scripts\start_OF.bat".format(Version.OFFullVer[1:-1])

        _msg = "Failed to find container id. Do you have the OpenFOAM container running?\n" + \
            "You can initiate OpenFOAM container by running start_OF.bat:\n" + \
            _fp

        # try to get containerId
        if not self.containerId:
            self.containerId = self.getContainerId()

        try:
            assert self.containerId, _msg
        except AssertionError:
            # this can be tricky since it takes some time for the batch file to
            # turn on the
            if startOpenFOAM:
                self.startOpenFOAM()
                self.containerId = self.getContainerId()
        finally:
            assert self.containerId, _msg

        # containerId is found. put the commands together
        _base = 'docker exec -i {} su - ofuser -c "cd /home/ofuser/workingDir/butterfly/{}; {}"'
        _baseCmd = '{0} {1} > >(tee etc/{2}.log) 2> >(tee etc/{2}.err >&2)'

        # join arguments for the command
        arguments = '' if not args else '-{}'.format(' -'.join(args))

        if decomposeParDict:
            # run in parallel
            n = decomposeParDict.numberOfSubdomains
            arguments = arguments + ' -parallel'

            if cmd == 'snappyHexMesh':
                cmdList = ('decomposePar', 'mpirun -np %s %s' % (n, cmd),
                           'reconstructParMesh', 'rm')
                argList = ('', arguments + ' -overwrite', '-constant', '-r proc*')
                cmdNameList = ('decomposePar', cmd, 'reconstructParMesh', 'rm')
            else:
                cmdList = ('decomposePar', 'mpirun -np %s %s' % (n, cmd),
                           'reconstructPar', 'rm')
                argList = ('', arguments, '', '-r proc*')
                cmdNameList = ('decomposePar', cmd, 'reconstructPar', 'rm')

            # join commands together
            cmds = (_baseCmd.format(c, arg, name) for c, arg, name in
                    zip(cmdList, argList, cmdNameList))

            cmds = _base.format(self.containerId, self.__projectName,
                                '; '.join(cmds))

            errfiles = tuple('{}.err'.format(name) for name in cmdNameList)
            logfiles = tuple('{}.log'.format(name) for name in cmdNameList)
        else:
            # run is serial
            cmds = _base.format(self.containerId, self.__projectName,
                                _baseCmd.format(cmd, arguments, cmd))
            errfiles = ('{}.err'.format(cmd),)
            logfiles = ('{}.log'.format(cmd),)

        if includeHeader:
            return res(self.header() + "\n" + cmds, logfiles, errfiles)
        else:
            return res(cmds, logfiles, errfiles)

    def duplicate(self):
        """Return a copy of this object."""
        return deepcopy(self)

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """Run manager representation."""
        return """RunManager::{}""".format(self.__projectName)

# coding=utf-8
"""Runmanager for butterfly.

Run manager is only useful for running OpenFOAM for Windows which runs in a
docker container. For linux systems simply use .bash files or libraries such as
pyFOAM.
"""
import os
import ctypes
import time
import sys
from subprocess import PIPE, Popen
from collections import namedtuple
from copy import deepcopy

from .version import Version


class UserNotAdminError(Exception):
    """Exception for non-admin users."""
    pass


class RunManager(object):
    """RunManager to write and run OpenFOAM commands through batch files.

    Run manager is currently only useful for running OpenFOAM for Windows which
    runs in a docker container. For linux systems simply use .bash files or
    libraries such as pyFOAM.

    """

    shellinit = None
    __containerId = None

    def __init__(self, projectName):
        u"""Init run manager for project.

        Project path will be set to: C:/Users/%USERNAME%/butterfly/projectName

        Args:
            projectName: A string for project name.
        """
        assert os.name == 'nt', "Currently RunManager is only supported on Windows."
        # make sure user has admin rights
        if not ctypes.windll.shell32.IsUserAnAdmin():
            raise UserNotAdminError(
                'In order to run OpenFOAM using butterfly you must use an admin '
                'account or run the program as administrator.')

        self.__projectName = projectName
        self.__separator = '&'
        self.isUsingDockerMachine = True \
            if hasattr(Version, 'isUsingDockerMachine') and Version.isUsingDockerMachine \
            else False

        self.dockerPath = r'"C:\Program Files\Docker Toolbox"' \
            if self.isUsingDockerMachine \
            else r'"C:\Program Files\Boot2Docker for Windows"'

        self.logFolder = './log'
        self.errFolder = './log'
        self._pid = None

    @property
    def containerId(self):
        """Container ID."""
        if not self.__containerId:
            self.getContainerId()

        return self.__containerId

    @property
    def pid(self):
        """Return PID for the latest command."""
        return self._pid

    def getShellinit(self):
        """Get shellinit for setting up initial environment for docker."""
        os.environ['PATH'] += ';%s' % r'"C:\Program Files (x86)\Git\bin"'
        os.environ['PATH'] += ';%s' % self.dockerPath

        if self.isUsingDockerMachine:
            # version 1606 and higher
            process = Popen('docker-machine env', shell=True, stdout=PIPE,
                            stderr=PIPE)
        else:
            # older versions are using boot2docker
            process = Popen('boot2docker shellinit', shell=True, stdout=PIPE,
                            stderr=PIPE)

        err = '\n'.join(process.stderr)
        if err:
            if err.find('Error checking TLS connection: Host is not running') != -1:
                msg = ' Docker machine is not running! Run Oracle VM VirtualBox Manager ' \
                    'as administrator and make sure "default" machine is "running".'
            else:
                msg = ''

            raise IOError('{}\n\t{}'.format(err, msg))

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

        cmds = '&'.join(self.shellinit + ('docker ps',))

        p = Popen(cmds, shell=True, stdout=PIPE, stderr=PIPE)

        if tuple(p.stderr):
            for line in p.stderr:
                print(line)
            return

        for count, line in enumerate(p.stdout):
            if line.find('of_plus') > -1:
                # find container
                _id = line.split()[0]
                print('container id: {}'.format(_id))

        self.__containerId = _id

    def getPid(self, command, timeout=5):
        """Get pid of a command."""
        if not self.containerId:
            self.getContainerId()

        self._pid = None
        cmd = 'docker exec -i {} pgrep {}'.format(self.containerId, command)
        cmds = '&'.join(self.shellinit + (cmd,))
        sys.stdout.flush()
        timeout_start = time.time()
        while time.time() < timeout_start + timeout:
            pids = Popen(cmds, shell=True, stdout=PIPE)
            pp = [int(p) for p in tuple(pids.stdout)]
            pp.sort()
            if pp:
                self._pid = int(pp[-1])
                sys.stdout.flush()
                return self._pid
            else:
                time.sleep(0.5)
        sys.stdout.flush()

    def terminate(self, pid=None, force=False):
        """Kill the command using the pid."""
        if not self.containerId:
            self.getContainerId()
        pid = pid or self.pid
        if not pid:
            return
        if force:
            killer = 'docker exec -i {} kill -9 {}'.format(self.containerId, pid)
        else:
            killer = 'docker exec -i {} kill {}'.format(self.containerId, pid)

        cmds = '&'.join(self.shellinit + (killer,))
        sys.stdout.flush()
        k = Popen(cmds, shell=True, stdout=PIPE)
        print(''.join(tuple(k.stdout)))

    @property
    def __ofBatchFile(self):
        if Version.OFFullVer == 'v3.0+':
            return r'C:\Program Files (x86)\ESI\OpenFOAM\v3.0+\Windows\Scripts' \
                '\start_OF.bat'
        else:
            return r'C:\Program Files (x86)\ESI\OpenFOAM\{}\\' \
                'Windows\Scripts\start_OF.bat'.format(Version.OFFullVer[1:-1])

    def startOpenFOAM(self):
        """Start OpenFOAM for Windows image from batch file."""
        Popen(self.__ofBatchFile, shell=True)

    def header(self):
        """Get header for batch files."""
        if not self.shellinit:
            self.shellinit = self.getShellinit()

        _base = '@echo off{0}' \
                'cd {1}{0}' \
                'echo Setting up the environment to connect to docker...{0}' \
                'echo .{0}' \
                '{2}{0}' \
                'echo Done!{0}' \
                'echo Running OpenFOAM commands...{0}' \
                'echo .'

        return _base.format(self.__separator, self.dockerPath,
                            self.__separator.join(self.shellinit))

    # TODO(): Update controlDict.application for multiple commands
    def command(self, cmd, args=None, decomposeParDict=None, includeHeader=True):
        """Get command line for an OpenFOAM command in parallel or serial.

        Args:
            cmd: An OpenFOAM command.
            args: List of optional arguments for command. e.g. ('c', 'latestTime')
            decomposeParDict: decomposeParDict for parallel runs (default: None).
            includeHeader: Include header lines to set up the environment
                (default: True).
            tee: Include tee in command line.
        Returns:
            (cmd, logfiles, errorfiles)
        """
        if isinstance(cmd, str):
            return self.__command(cmd, args, decomposeParDict, includeHeader)
        elif isinstance(cmd, (list, tuple)):
            # a list of commands
            res = namedtuple('log', 'cmd logfiles errorfiles')
            logs = range(len(cmd))  # create a place holder for commands
            for count, c in enumerate(cmd):
                if count > 0:
                    includeHeader = False
                if c == 'blockMesh':
                    decomposeParDict = None
                try:
                    arg = args[count]
                except TypeError:
                    arg = args

                logs[count] = self.__command(c, (arg,), decomposeParDict,
                                             includeHeader)

            command = '&'.join(log.cmd for log in logs)
            logfiles = tuple(ff for log in logs for ff in log.logfiles)
            errorfiles = tuple(ff for log in logs for ff in log.errorfiles)

            return res(command, logfiles, errorfiles)

    def __command(self, cmd, args=None, decomposeParDict=None, includeHeader=True):
        """Get command line for an OpenFOAM command in parallel or serial.

        Args:
            cmd: An OpenFOAM command.
            args: List of optional arguments for command. e.g. ('-c', '-latestTime')
            decomposeParDict: decomposeParDict for parallel runs (default: None).
            includeHeader: Include header lines to set up the environment
                (default: True).
            tee: Include tee in command line.
        Returns:
            (cmd, logfiles, errorfiles)
        """
        tee = 'tee'
        res = namedtuple('log', 'cmd logfiles errorfiles')
        _msg = 'Failed to find container id.' \
            'Do you have the OpenFOAM container running?\n' \
            'You can initiate OpenFOAM container by running start_OF.bat:\n{}' \
            .format(self.__ofBatchFile)

        # try to get containerId
        if not self.containerId:
            self.getContainerId()

        assert self.containerId, _msg

        # containerId is found. put the commands together
        _base = 'start /wait docker exec -i {} su - ofuser -c ' \
            '"cd /home/ofuser/workingDir/butterfly/{}; {}"'
        _baseCmd = '{0} {1} > >(%s %s/{2}.log) 2> >(%s %s/{2}.err >&2)' \
            % (tee, self.logFolder, tee, self.errFolder)

        # join arguments for the command
        arguments = '' if not args else '{}'.format(' '.join(args))

        if decomposeParDict:
            # run in parallel
            n = decomposeParDict.numberOfSubdomains
            arguments = arguments + ' -parallel'

            if cmd == 'snappyHexMesh':
                cmdList = ('decomposePar', 'mpirun -np %s %s' % (n, cmd),
                           'reconstructParMesh', 'rm')
                argList = ('', arguments, '-constant', '-r proc*')
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

            errfiles = tuple('{}/{}.err'.format(self.errFolder, name)
                             for name in cmdNameList)
            logfiles = tuple('{}/{}.log'.format(self.logFolder, name)
                             for name in cmdNameList)
        else:
            # run is serial
            cmds = _base.format(self.containerId, self.__projectName,
                                _baseCmd.format(cmd, arguments, cmd))
            errfiles = ('{}/{}.err'.format(self.errFolder, cmd),)
            logfiles = ('{}/{}.log'.format(self.logFolder, cmd),)

        if includeHeader:
            return res(self.header() + self.__separator + cmds, logfiles, errfiles)
        else:
            return res(cmds, logfiles, errfiles)

    def run(self, command, args=None, decomposeParDict=None, wait=True):
        """Run OpenFOAM command."""
        # get the command as a single line
        cmd, logfiles, errfiles = self.command(command, args, decomposeParDict)

        # run the command.
        # shell should be True to run multiple commands at the same time.
        log = namedtuple('log', 'process logfiles errorfiles')
        p = Popen(cmd, shell=True)
        c = command.split()[0].strip()
        if c in ('blockMesh', 'surfaceFeatureExtract', 'postProcess'):
            timeout = 1
        else:
            timeout = 5
        time.sleep(0.5)  # wait 0.5 second to make sure the command has started
        ppid = self.getPid(command.split()[0], timeout)
        print('Butterfly is running {}. PID: {}'.format(command, ppid))
        if wait:
            p.communicate()
            # once over try to kill the process if exist.
            # This will ensure that the command will be terminated even if the
            # user has canceled the run by closing the batch window.
            self.terminate(ppid)

        return log(p, logfiles, errfiles)

    def checkFileContents(self, files, mute=False):
        """Check files for content and print them out if any.

        args:
            files: A list of ASCII files.

        returns:
            (hasContent, content)
            hasContent: A boolean that shows if there is any contents.
            content: Files content if any
        """
        def readFile(f):
            try:
                with open(f, 'rb') as log:
                    return log.read().strip()
            except Exception as e:
                err = 'Failed to read {}:\n\t{}'.format(f, e)
                print(err)
                return ''

        _lines = '\n'.join(tuple(readFile(f) for f in files)).strip()

        if len(_lines) > 0:
            if not mute:
                print(_lines)
            return True, _lines
        else:
            return False, _lines

    def duplicate(self):
        """Return a copy of this object."""
        return deepcopy(self)

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """Run manager representation."""
        return """RunManager::{}""".format(self.__projectName)

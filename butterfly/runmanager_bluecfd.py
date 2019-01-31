# coding=utf-8
"""Runmanager for butterfly.

Run Butterfly on Windows using blueCFD: http://bluecfd.github.io/Core/About/

This class has been tested against blueCFD-Core 2017-2:
http://bluecfd.github.io/Core/Downloads/
"""
import os
import ctypes
import time
import sys
import platform
from subprocess import PIPE, Popen
from collections import namedtuple
from copy import deepcopy
from .runmanagerenv import bluecfd as bcfdenv
from .version import Version
import butterfly


class UserNotAdminError(Exception):
    """Exception for non-admin users."""
    pass


class RunManagerBlueCFD(object):
    """RunManager BlueCFD to write and run OpenFOAM commands through batch files."""

    shellinit = None
    __containerId = None

    def __init__(self, project_name):
        u"""Init run manager for project.

        Project path will be set to: C:/Users/%USERNAME%/butterfly/project_name

        Args:
            project_name: A string for project name.
        """
        assert os.name == 'nt', "Currently RunManager is only supported on Windows."
        self._blue_folder = butterfly.config['of_folder']
        self._env = bcfdenv(self._blue_folder)
        self._project_name = project_name
        self._project_folder = r'c:\Users\{}\butterfly\{}'.format(
            os.getenv('USERNAME'), self._project_name)
        self.log_folder = './log'
        self.errFolder = './log'
        self._process = None

    @property
    def process(self):
        """Return PID for the latest command."""
        return self._process

    @property
    def is_user_admin(self):
        """Return True if user is admin."""
        if ctypes.windll.shell32.IsUserAnAdmin():
            return True
        else:
            return False

    def ensure_user_is_admin(self):
        """Ensure user is logged in as admin.

        If user is not admin raise UserNotAdminError.
        """
        if self.is_user_admin:
            raise UserNotAdminError(
                'In order to run OpenFOAM using butterfly you must use an admin '
                'account or run the program as administrator.')
        else:
            return True

    def terminate(self, pid=None, force=False):
        """Kill the command using the pid."""
        process = pid or self.process
        if not pid:
            return
        process.terminate()

    @property
    def is_ironpython(self):
        """Check if the platform is IronPython."""
        iron_python = True
        try:
            iron_python = True if platform.python_implementation() == 'IronPython' \
                else False
        except ValueError as e:
            # older versions of IronPython fail to parse version correctly
            # failed to parse IronPython sys.version: '2.7.5 (IronPython 2.7.5 (2.7.5.0)
            # on .NET 4.0.30319.42000 (64-bit))'
            if 'IronPython' in str(e):
                iron_python = True
        return iron_python

    # TODO(): Update controlDict.application for multiple commands
    def command(self, cmd, args=None, decomposeParDict=None, include_header=True):
        """Get command line for an OpenFOAM command in parallel or serial.

        Args:
            cmd: An OpenFOAM command.
            args: List of optional arguments for command. e.g. ('c', 'latestTime')
            decomposeParDict: decomposeParDict for parallel runs (default: None).
            include_header: Include header lines to set up the environment
                (default: True).
        Returns:
            (cmd, logfiles, errorfiles)
        """
        if isinstance(cmd, str):
            return self.__command(cmd, args, decomposeParDict, include_header)
        elif isinstance(cmd, (list, tuple)):
            # a list of commands
            res = namedtuple('log', 'cmd logfiles errorfiles')
            logs = list(range(len(cmd)))  # create a place holder for commands
            for count, c in enumerate(cmd):
                if count > 0:
                    include_header = False
                if c == 'blockMesh':
                    decomposeParDict = None
                try:
                    arg = args[count]
                except TypeError:
                    arg = args

                logs[count] = self.__command(c, (arg,), decomposeParDict,
                                             include_header)

            command = tuple(log.cmd for log in logs)
            logfiles = tuple(ff for log in logs for ff in log.logfiles)
            errorfiles = tuple(ff for log in logs for ff in log.errorfiles)

            return res(command, logfiles, errorfiles)

    def __command(self, cmd, args=None, decomposeParDict=None, include_header=True):
        """Get command line for an OpenFOAM command in parallel or serial.

        Args:
            cmd: An OpenFOAM command.
            args: List of optional arguments for command. e.g. ('-c', '-latestTime')
            decomposeParDict: decomposeParDict for parallel runs (default: None).
            include_header: Include header lines to set up the environment
                (default: True).
            tee: Include tee in command line.
        Returns:
            (cmd, logfiles, errorfiles)
        """
        res = namedtuple('log', 'cmd logfiles errorfiles')

        # join arguments for the command
        arguments = '' if not args else '{}'.format(' '.join(args))

        if decomposeParDict:
            # run in parallel
            n = decomposeParDict.numberOfSubdomains
            arguments = arguments + ' -parallel'

            if cmd == 'snappyHexMesh':
                cmd_list = ('decomposePar', 'mpirun -np %s %s' % (n, cmd),
                            'reconstructParMesh', 'rm')
                arg_list = ('', arguments, '-constant', '-r proc*')
                cmd_name_list = ('decomposePar', cmd,
                                 'reconstructParMesh', 'rm')
            else:
                cmd_list = ('decomposePar', 'mpirun -np %s %s' % (n, cmd),
                            'reconstructPar', 'rm')
                arg_list = ('', arguments, '', '-r proc*')
                cmd_name_list = ('decomposePar', cmd, 'reconstructPar', 'rm')

            cmds = tuple(' '.join((c, arg))
                         for c, arg in zip(cmd_list, arg_list))
            # join commands together
            errfiles = tuple('{}/{}.err'.format(self.errFolder, name)
                             for name in cmd_name_list)
            logfiles = tuple('{}/{}.log'.format(self.log_folder, name)
                             for name in cmd_name_list)
        else:
            # run is serial
            cmds = (cmd,)
            errfiles = ('{}/{}.err'.format(self.errFolder, cmd),)
            logfiles = ('{}/{}.log'.format(self.log_folder, cmd),)

        return res(cmds, logfiles, errfiles)

    def _run_ironpython(self, cmds, logfiles, errfiles, wait):
        """Run commands in IronPython.

        The command is running from inside Grasshopper or Dynamo
        make a batch file and run the command from inside batch file
        so it pops up in the screen.
        """
        log = namedtuple('log', 'process logfiles errorfiles')
        envfile = os.path.join(self._blue_folder, 'setvars.bat')
        header = \
            'call "{}"\nset PATH=%HOME%\\msys64\\usr\\bin;%PATH%\n' \
            'cd {}\n'.format(envfile, self._project_folder)
        commands = [cmd + ' | tee log\\%s.log' % cmd.split()[0]
                    for cmd in cmds]

        # write all the commnds in one go!
        cmd = '\n'.join(commands)

        with open('ir.bat', 'w') as batchfile:
            batchfile.write(header)
            batchfile.write(cmd)

        process = Popen('ir.bat', stderr=PIPE, shell=False)

        if not wait:
            return log(process, logfiles, errfiles)

        self._handle_process(process, logfiles[0], errfiles[0], True)

        return log(process, logfiles, errfiles)

    def run(self, command, args=None, decomposeParDict=None, wait=True):
        """Run OpenFOAM command."""
        # get the command as a single line
        cmds, logfiles, errfiles = self.command(
            command, args, decomposeParDict)
        is_ironpython = self.is_ironpython
        # run the command.
        log = namedtuple('log', 'process logfiles errorfiles')

        # update env variables
        env = os.environ.copy()
        full_path = self._env["PATH"] + env["PATH"]
        env.update(self._env)
        env["PATH"] = full_path

        os.chdir(self._project_folder)
        if is_ironpython:
            return self._run_ironpython(cmds, logfiles, errfiles, wait)

        elif not wait and len(cmds) > 1:
            # put all commands in a single line otherwise it won't wait for all of them
            # it is Winsows so I use &&
            cmds = ['&&'.join(cmds)]

        for counter, cmd in enumerate(cmds):
            try:
                process = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True, env=env,
                                encoding='utf8')
            except TypeError:
                # python 2
                process = Popen(cmd, stdout=PIPE, stderr=PIPE,
                                shell=True, env=env)

            if not wait:
                return log(process, logfiles, errfiles)

            self._handle_process(
                process, logfiles[counter], errfiles[counter], False)

        return log(process, logfiles, errfiles)

    def _handle_process(self, process, logfile, errfile, is_ironpython):
        # wait for process to finish while printing and logging
        with open(logfile, 'w') as outf:
            while True:
                if is_ironpython:
                    output = ''
                else:
                    output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    err = process.stderr.read()
                    break
                if output:
                    outf.write(output.strip())
                    print(output.strip())

        if process.returncode != 0:
            if str(err).strip():
                # pass cases that the user closes the window
                with open(errfile, 'w') as outf:
                    outf.write(err)
                raise Exception(err)
            else:
                self.terminate()
                print('The process is interrupted by user!')
        else:
            with open(errfile, 'w') as outf:
                # create an empty file
                pass

    def check_file_contents(self, files, mute=False):
        """Check files for content and print them out if any.

        args:
            files: A list of ASCII files.

        returns:
            (hasContent, content)
            hasContent: A boolean that shows if there is any contents.
            content: Files content if any
        """
        def read_file(f):
            try:
                with open(f, 'rb') as log:
                    return log.read().strip()
            except Exception as e:
                err = 'Failed to read {}:\n\t{}'.format(f, e)
                print(err)
                return ''

        _lines = '\n'.join(tuple(read_file(f) for f in files)).strip()

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
        return """RunManager::{}""".format(self._project_name)

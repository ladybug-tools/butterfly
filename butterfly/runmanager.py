from version import Version

import os
from subprocess import PIPE, Popen


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
        self.projectName = projectName

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

    def command(self, cmds, includeHeader=False, log=True, startOpenFOAM=False):
        """
        Get command line for OpenFOAM commands.

        Args:
            cmds: A sequence of commnads.
            includeHeader: Include header lines to set up the environment.
            log: Write the results to log files.
            startOpenFOAM: Execute OpenFOAM in case it's not already running.
        """
        if Version.OFFullVer == 'v3.0+':
            _fp = r"C:\Program Files (x86)\ESI\OpenFOAM\v3.0+\Windows\Scripts\start_OF.bat"
        else:
            _fp = r"C:\Program Files (x86)\ESI\OpenFOAM\{}\\" + \
                "Windows\Scripts\start_OF.bat".format(Version.OFFullVer[1:-1])

        _msg = "Failed to find container id. Do you have the OpenFOAM container running?\n" + \
            "You can initiate OpenFOAM container by running start_OF.bat:\n" + \
            _fp

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

        _base = 'docker exec -i {} su - ofuser -c "cd /home/ofuser/workingDir/butterfly/{}; {}"'

        if log:
            _baseCmd = '{0} > >(tee etc/{0}.log) 2> >(tee etc/{0}.err >&2)'

            _cmds = (_baseCmd.format(cmd, self.projectName) for cmd in cmds)
        else:
            _cmds = cmds

        _cmd = _base.format(self.containerId, self.projectName, '; '.join(_cmds))

        if includeHeader:
            return self.header() + "\n" + _cmd
        else:
            return _cmd

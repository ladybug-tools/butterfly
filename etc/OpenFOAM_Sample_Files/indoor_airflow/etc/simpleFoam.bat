@echo off
cd C:\Program Files\Docker Toolbox
echo Setting up the environment to connect to docker...
echo .
SET DOCKER_TLS_VERIFY=1
SET DOCKER_HOST=tcp://192.168.99.100:2376
SET DOCKER_CERT_PATH=C:\Users\Administrator\.docker\machine\machines\default
SET DOCKER_MACHINE_NAME=default
echo Done!
echo Running OpenFOAM commands...
echo .
docker exec -i e7a36e8e9eeb su - ofuser -c "cd /home/ofuser/workingDir/butterfly/indoor_airflow; decomposePar  > >(tee etc/decomposePar.log) 2> >(tee etc/decomposePar.err >&2); mpirun -np 2 simpleFoam  -parallel > >(tee etc/simpleFoam.log) 2> >(tee etc/simpleFoam.err >&2); reconstructPar  > >(tee etc/reconstructPar.log) 2> >(tee etc/reconstructPar.err >&2); rm -r proc* > >(tee etc/rm.log) 2> >(tee etc/rm.err >&2)"
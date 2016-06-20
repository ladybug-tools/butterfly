![Screenshot](https://raw.githubusercontent.com/mostaphaRoudsari/Butterfly/master/other_files/graphics/icon/butterfly_100px_2.png)

Butterfly
========================================
A python API for OpenFoam which will be used to create a plugin to connect Grasshopper3D to [OpenFoam](http://www.openfoam.org/) for CFD simulation!

Usage
========================================
```Python
from butterfly import core
import butterfly.solvers as solvers

## initiate project
p = core.BFProject("test")

# boundary conditions in the model
bConditions = ["floor", "ceiling", "fixedWalls"]

# create the solver with default values
# you can create your own solver by using solvers.Solver > check solver.py for examples
p_rgh = solvers.P_RGH()
# add boundary field
for bc in bConditions: p_rgh.add_boundaryField(bc, other = {"rho":"rhok"})
p.add_solver(p_rgh) #add p_rgh to project

# add one more solver as an example
k = solvers.K()
for bc in bConditions: k.add_boundaryField(bc)
p.add_solver(k) # add to project

# TODO: create constant folder

# TODO: add constant object to project

# TODO: create system objects

# TODO: add system projects to object

# write project
p.createProject()

# TODO: run the analysis
#p.run()

```

WARNING
========================================
## Work in progress! We're developing it live and open. It's not supposed to work until we remove this line!


Current Development Goal
========================================
Export a box room with two windows (inlet and outlet) to OpenFOAM and run the analysis.


Tentative Component List
========================================
### Create Butterfly surfaces
	Type > inlet, outlet, walls, outflow, ...
	Boundary Condition > This will change based on the type - velocity - pressure -...
	We may need to create several ones for each boundary condition type.

### Set meshing parameters
	Meshing density
	Meshing type

### Visualize test Grid
	Import back the generated grid by OpenFOAM into Grasshopper3D for quality check

### Set solver parameters

### Run CFD analysis

### Results visualization component


You need to have [Ladybug](https://github.com/mostaphaRoudsari/Ladybug) and [Honeybee](https://github.com/mostaphaRoudsari/Ladybug) installed in order to run Butterfly.


@license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

![Screenshot](https://raw.githubusercontent.com/mostaphaRoudsari/Butterfly/master/graphics/icon/butterfly_100px.png)

Butterfly
========================================
A plugin to connect Grasshopper3D to [OpenFoam](http://www.openfoam.org/) for CFD simulation

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

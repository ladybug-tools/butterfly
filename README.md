![Screenshot]()

Butterfly
========================================
A plugin to connect Grasshopper3D to OpenFoam for CFD simulation

WARNING
========================================
# Work in progress! We're developing it live and open. It's not supposed to work until we remove this line!

Current development goal
========================================
Export a box room with two windows (inlet and outlet) to OpenFOAM and run the analysis.

Tentative Component List
========================================
![checkmark]#Create Butterfly surfaces to assign
	Type > inlet, outlet, walls, outflow, ...
	Boundary Condition > This will change based on the type - velocity - pressure -...
	We may need to create several ones for each boundary condition type.

![checkmark] #Set meshing parameters
	Meshing density
	Meshing type

![checkmark] # Visualize test Grid
	Import back the generated grid by OpenFOAM into Grasshopper3D for quality check

![checkmark] #Set solver parameters

![checkmark] #Results visualization component

![Screenshot]()


You need to have [Ladybug](https://github.com/mostaphaRoudsari/Ladybug) and [Honeybee](https://github.com/mostaphaRoudsari/Ladybug) installed in order to run Butterfly.


@license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

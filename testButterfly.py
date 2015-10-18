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

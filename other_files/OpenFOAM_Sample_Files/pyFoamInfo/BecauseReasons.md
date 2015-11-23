Hello everyone!

I am adding a few examples of the use of pyFoam in OpenFoam. I believe pyFoam is a very important part of OpenFoam and can be extremely useful for our GUI for many reasons.

1. 

First of all, pyFoam & swak4foam allows you to create types of boundary conditions that are not currently available in OpenFoam (e.g. connected to a custom function or a table of attributes). I won't go into this now as I feel it is the least important for the stage we are at. But could be a powerful feature later on, especially if we provide ready made bcs to users.

2. 

Secondly, they allow for a pretty nice visualization of your solution on-the-fly, something that can easily be a part of every simulation of our tool. In order to use this feature of pyFoam, after installing it, run your simulations by writing:

pyFoamPlotRunner.py simpleFoam

or 

pyFoamPlotRunner.py mpirun -mp -numberofprocessorshere simpleFoam -parallel

The pyFoamPlotRunner.py utility is one of many pyFoam utilities, and it allows you to observe the fluctuation of several properties on the fly (as you can see in the screenshot I uploaded). This is a cool nice feature we can add with this simple command hidden behind the lines. Additionally, all pyFoam runner utilities create a bunch of files that can be used later on to retrieve information.

3. 

A third reason to use these tools is the powerful function objects they allow you to create. Function objects themselves are a very interesting part of our tool ESPECIALLY when we are operating through a Rhino interface. Most of the function objects operate on points or surfaces within and around your geometry and creating, manipulating and extracting information for all these is done wonderfully in GH. I will add a file with the native OpenFoam function objects I usually use in another space, but here I will just stick to the swak4foam object below.

One important information that one wants to get after a CFD in the urban environment is the wind velocity (usually but not always averaged to some property, e.g. floor area) in different rooms of a house, floor, building, etc. Unfortunately, something like that is impossible in post-processing phase (i.e. in paraView) in 99.999% of the cases. The only thing that would make it possible is to model and create a bc for each and every one of those surfaces (and it would still be problematic if you could). Thankfully, a beautiful and simple way of doing this is given to us by swak4foam:

(Everything below goes in ControlDict, under the last line which usually is "runTimeModifiable true;". It is also written in the OpenFoam C++ish code so you can simply copy paste it in your control dicts.)

//First we call the swak4foam libraries that will allow us to use the tools. Bare in mind that I'm currently operating in Linux so I have not tested this in Windows. I imagine that apart from the .so to .dll extension change there should not be other changes. If someone can test or already tested please let us know. Until I go home and actually do it.

libs (
"libOpenFOAM.dll"
"libsimpleSwakFunctionObjects.dll"
"libswakFunctionObjects.dll"
"libgroovyBC.dll"
);

//Second we introduce our functions area

functions
(

//we then create, in order to store it later, our expression field for our wind velocity (mag(U) for OpenFoam)
	
    makeMagU {
         type expressionField;
         functionObjectLibs
        (
            "libswakFunctionObjects.so"
        );      
	autowrite false;
        fieldName magU;
        expression "mag(U)";
    }

//I should note here that all the calculation we will be doing will be "on" surfaces we already  created in Rhino. I will upload a simple example once I get the time, but imagine a one room house for which you want to have an idea of the wind flow when the windows are open. You simply copy the floor surface and move it vertically upwards for let's say 1.2m. Then use that surface stl (let's call it CalculationPlane.stl) as a boundary where you calculate the average velocity. 

//To do that we first tell OpenFoam to use that .stl surface as the source from where it can extract the cells or faces on which it will calculate the average wind velocity. Remember here that every mesh consists of cells and every cell consists of faces.

	SimpleRoom 		//give a name to your function object
    {
        type            faceSource;
        functionObjectLibs ("libfieldFunctionObjects.dll");
        enabled         true;
        outputControl   outputTime;
        // Output to log&file (true) or to file only
        log             true;			//quite important for post processing, potential candidate for your .js visualization project!
        // Output field values as well
        valueOutput     true;
	surfaceFormat	stl;
        // Type of source: patch/faceZone/sampledSurface
        source          sampledSurface;			//when this is enabled we need a sampledSurfaceDict, see below.
	sourceName	T1A_Bedroom1;
        //// Note: will not sample surface fields.
        sampledSurfaceDict
        {
           // Sampling on triSurface
           type        sampledTriSurfaceMesh;
           surface     CalculationPlane.stl;		//our surface .stl that we created earlier in Rhino
           source      cells;  				// sample cells or boundaryFaces
           interpolate false;
        }

        // Operation: areaAverage/sum/weightedAverage ..., we choose areaAverage here.
        operation       areaAverage;

        fields
        (
            magU					//our wind velocity which we are telling OpenFoam to store in our previous function object.
        );
    }

//And voila! Enter this function object to any ControlDict file you have, with any names you choose for it and ur calculation surfaces, and you will get the average wind velocity on each surface at every write interval, during solving, in parallel! If you wish to calculate this in more surfaces you simply use the same code for each surface, with only the function object name and surface names changed. Here you can understand why I am excited with the connection between OpenFoam and Rhino/GH. I can select all my "Floor" layers, insert them in GH, move them 1.2m up, then link them to my "FunctionObjects" component, and run the solver. Even better, I can bring any number of Honeybee zones into my "FunctionObjects" component and then have it identify the name of each zone, use it to name each floor surface, and use it to generate the above code for each of the surfaces automatically! Rant over :)




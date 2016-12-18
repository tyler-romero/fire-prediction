This is the Github repo for the Artificial Intelligence (Stanford CS 221) and Machine Learning (Stanford CS 229) projects of:
Tyler Romero
Frank Cipollone
Zach Barnes


---------------------------------------------- reports ------------------------------------------------

This folder contains every report and poster that we turned in for each class. For an in-depth look into our projects, we recommend you start here.

---------------------------------------------- cs221_code ----------------------------------------------

This folder contains the final code for our cs221 project. Instructions for running are given below:

######### Infrastructure #########

Our project is coded in Python 2.7

In order to run testing.py as described below, matplotlib is required


######### File Descriptions #########

framework.py:
	Contains the infrastructure necessary to read in, process, and dispense data to our simulation at the appropriate timestep.

qlearning.py:
	Contains the qlearning algorithm as taught in class.

models.py:
	Contains an abstraction of a model, as well as implementations of our baseline, oracle, random walk, and qlearning model.

simulation.py:
	Contains the infrastructure necessary to fully describe the current state of our simulation, including truck locations, incident locations, the current model being exectued, and statistics regarding that model. In addition, simulation.py executes timesteps by recieving an action from the model, executing that action, and updating the state of the simulation.

utilities.py:
	Basic helper functions

model_demo.py:
	A demo we prepared to show how our model actually works in slow motion. It executes actions based on our qlearning model, prints the state of the simulation to the console, and pauses in between timesteps.

testing.py:
	A file we used in order to compile our results. It currently contains the code required to test and compare our baseline, oracle, and qlearning models over ten days of data.


######### Commands to Run #########

In order to view a demo of our simulation acting according to our qlearning model, run:
> python model_demo.py

In order to run our testing file in order to compare models, run:

>python testing.py


---------------------------------------------- cs229_code ------------------------------------------------

This folder contains the final code for our cs229 project.


---------------------------------------------- data -------------------------------------------------------

Contains the data files used in both projects. The data was given to us by the San Diego Fire Department.
We modified the original csvs by adding a column for latitude and longitude.


---------------------------------------------- visualizations ----------------------------------------------

This folder contains visualizations of our data that were used in our reports.




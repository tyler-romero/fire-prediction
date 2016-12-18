CS 221 Project Submission
Dynamic Allocation of Emergency Resources
Tyler Romero
Frank Cipollone
Zach Barnes


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


######### Setup #########

Unzip code.zip and data.zip into the same directory.

If you are reading this from GitHub, you won't have access to data.zip


######### Commands to Run #########

In order to view a demo of our simulation acting according to our qlearning model, run:
> python model_demo.py

In order to run our testing file in order to compare models, run:

>python testing.py
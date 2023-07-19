A Streamlit interactive webapp using Simpy to model the
elective hand surgery pathway at GSTT.

Contents
######################################################
/binder
Contains yml file for sim2 environment that includes 
Streamlit package

/content
Contains the model code

	./global_params.py
	Contains global parameter class g

	./HandPatient.py
	Contains class to simulate a patient Entity
	in Simpy

	./HandPathway.py
	Contains class for the simpy Environment 
	and functions to run the simulation

	./model.py
	Contains code to run the simulation

	./ResultsCalculator.py
	Contains code to run multiple simulations
	and Streamlit wrappers to run webapp

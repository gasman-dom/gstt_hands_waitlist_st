# Models the elective hand surgery pathway at GSTT
# A Streamlit webapp built using Simpy

import simpy
import random
import numpy as np
import pandas as pd
import csv
from statistics import mean
import matplotlib.pyplot as plt
import seaborn as sns
import os
import streamlit as st
import plotly.express as px

from HandPatient import Patient
from HandPathway import Hand_Surgery_Pathway
from ResultsCalculator import Trial_Results_Calculator
from global_params import g

# page config
st.set_page_config(layout='wide')

# title text
st.title('GSTT Hand Surgery Pathway Simulation')

# set up columns
col1, col2, col3, col4, col5 = st.columns(5)

# create input widgets
with col1:
    REFS_PER_WEEK = st.number_input('GP Referrals Per Week',
                                         step=1,
                                         value = g.referrals_per_week)

with col2:
    CLINICS_PER_WEEK = st.number_input('Clinics Per Week',
                                           step = 1,
                                           value = g.surg_clinic_per_week)
    
    CLINIC_APPTS = st.number_input('Appointments Per Clinic',
                                        step = 1,
                                        value = g.surg_clinic_appts)
    
    CLINIC_Q = st.number_input('Number in Clinic Queue',
                                    step = 1,
                                    value = g.fill_clinic_q)
    
with col3:
    IMAGING_WAIT = st.number_input('Wait Time for Imaging (days)',
                                   step = 1,
                                   value = g.imaging_wait)
    
    PROB_IMAGING = st.slider('Probability Patients Need Imaging',
                                            step = 0.01,
                                            value = g.prob_needs_imaging)
    
    IMAGING_Q = st.number_input('Number in Imaging Queue',
                                        step = 1,
                                        value = g.fill_imaging_q)
    
with col4:
    THERAPY_WAIT = st.number_input('Wait Time for Hand Therapy (days)',
                                   step = 1,
                                   value = g.therapy_wait)
    
    PROB_THERAPY = st.slider('Probability Patients Need Hand Therapy',
                                            step = 0.01,
                                            value = g.prob_needs_therapy)
    
    THERAPY_Q = st.number_input('Number in Therapy Queue at Start of Simulation',
                                        step = 1,
                                        value = g.fill_therapy_q)

with col5:
    LISTS_PER_WEEK = st.number_input('Theatre Lists Per Week',
                                            step = 1,
                                            value = g.theatre_list_per_week)
    
    LIST_CAPACITY = st.number_input('Cases Per Theatre List',
                                            step = 1,
                                            value = g.theatre_list_capacity)
    
    THEATRE_Q = st.number_input('Number in Theatre Queue at Start of Simulation',
                                        step = 1,
                                        value = g.fill_theatre_q)

NUM_OF_RUNS = st.number_input('Number of Times to Run Simulation',
                                        step = 1,   
                                        value = g.number_of_runs)

LENGTH_OF_SIM = st.number_input('Length of Simulation (days)',
                                        step = 1,
                                        value = g.sim_duration)

# button to run simulation
if st.button('Start Simulation'):

    # spinner while loading
    with st.spinner('Running simulation...'):

        # create a file to store the numbers in queues
        with open('queue_numbers.csv', 'w') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerow(['run','clinic_q', 'imaging_q', 'therapy_q', 'theatres_q'])

        # For the number of runs specified in the g class, create an instance of the
        # ED_Model class, and call its run method
        for run in range(g.number_of_runs):
            print (f"Run {run+1} of {g.number_of_runs}")
            demo_pathway_model = Hand_Surgery_Pathway(run,
                                                      referrals_per_week=REFS_PER_WEEK,
                                                      surg_clinic_per_week=CLINICS_PER_WEEK,
                                                      surg_clinic_appts=CLINIC_APPTS,
                                                      fill_clinic_q=CLINIC_Q,
                                                      imaging_wait=IMAGING_WAIT,
                                                      prob_needs_imaging=PROB_IMAGING,
                                                      fill_imaging_q=IMAGING_Q,
                                                      therapy_wait=THERAPY_WAIT,
                                                      prob_needs_therapy=PROB_THERAPY,
                                                      fill_therapy_q=THERAPY_Q,
                                                      theatre_list_per_week=LISTS_PER_WEEK,
                                                      theatre_list_capacity=LIST_CAPACITY,
                                                      fill_theatre_q=THEATRE_Q,
                                                      sim_duration=LENGTH_OF_SIM
                                                      )
            demo_pathway_model.run()

        # Once the trial is complete, we'll create an instance of the
        # Trial_Result_Calculator class and run the print_trial_results method
        demo_trial_results_calculator = Trial_Results_Calculator(number_of_runs=NUM_OF_RUNS,
                                                                 fill_clinic_q=CLINIC_Q,
                                                                 fill_imaging_q=IMAGING_Q,
                                                                 fill_therapy_q=THERAPY_Q,
                                                                 fill_theatre_q=THEATRE_Q)
        demo_trial_results_calculator.concatenate_wait_times()
        demo_trial_results_calculator.calculate_mean_queue_numbers()

        # plot the results
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(demo_trial_results_calculator.plot_wait_times())
        with col2:
            st.plotly_chart(demo_trial_results_calculator.plot_queue_numbers())

# A class to calculate and display trial results

import simpy
import random
import numpy as np
import pandas as pd
import csv
from statistics import mean
import matplotlib.pyplot as plt
import seaborn as sns
import os
import plotly.express as px

from global_params import g
from HandPathway import Hand_Surgery_Pathway
from HandPatient import Patient


class Trial_Results_Calculator:
    def __init__(self,
                 number_of_runs = g.number_of_runs,
                 sim_duration = g.sim_duration,
                 fill_clinic_q = g.fill_clinic_q,
                 fill_imaging_q = g.fill_imaging_q,
                 fill_therapy_q = g.fill_therapy_q,
                 fill_theatre_q = g.fill_theatre_q):
        #self.trial_results_df = pd.DataFrame()

        self.number_of_runs = number_of_runs
        self.sim_duration = sim_duration
        self.fill_clinic_q = fill_clinic_q
        self.fill_imaging_q = fill_imaging_q
        self.fill_therapy_q = fill_therapy_q
        self.fill_theatre_q = fill_theatre_q

    # A method to concatenate the multiple wait time CSVs
    def concatenate_wait_times(self):

        # create empty dataframe
        nodata = {'time_entered_pathway': [],
                    'overall_q_time': []}
        all_wait_times_df = pd.DataFrame(nodata)

        for i in range(self.number_of_runs):
            wait_times_this_run = pd.read_csv(f'wait_times_run_{i}.csv')
            all_wait_times_df = pd.concat([all_wait_times_df, wait_times_this_run])

        # save to csv
        #print(all_wait_times_df.head())
        all_wait_times_df.to_csv('all_wait_times.csv')

        # delete individual run files
        for i in range(self.number_of_runs):
            os.remove(f'wait_times_run_{i}.csv')

    # A method to read in the run results csv file and print them for the user
    def plot_wait_times(self):
        trial_results_df = pd.read_csv('all_wait_times.csv')
        
        fig = px.scatter(trial_results_df, x='time_entered_pathway',
                            y='overall_q_time', opacity=0.6, trendline='ols',
                            trendline_color_override='red',
                            title='Total wait time vs time of referral',
                            labels={'time_entered_pathway': 'Day of referral',
                                    'overall_q_time': 'Total wait time'})
        return fig

    # method to calculate average queue numbers over all runs
    def calculate_mean_queue_numbers(self):

        # read in queue numbers csv
        self.queue_numbers_df = pd.read_csv('queue_numbers.csv')

        # calculate mean queue numbers
        data = {
            'name': ['Clinic', 'Imaging', 'Hand Therapy', 'Theatres'],
            'Before': [self.fill_clinic_q, self.fill_imaging_q, self.fill_therapy_q, self.fill_theatre_q],
            'After': [self.queue_numbers_df['clinic_q'].mean(),
                        self.queue_numbers_df['imaging_q'].mean(),
                        self.queue_numbers_df['therapy_q'].mean(),
                        self.queue_numbers_df['theatres_q'].mean()]
        }

        # create dataframe
        self.overall_q_numbers_df = pd.DataFrame(data)
        self.overall_q_numbers_df.set_index('name', inplace=True)

        #print(f'Number in clinic queue before: {self.fill_clinic_q}')
        #print(f'Number in clinic queue after: {self.overall_q_numbers_df["After"][0]}')
        #print(self.overall_q_numbers_df)

    # plot the average queue numbers
    def plot_queue_numbers(self):
        fig = px.bar(self.overall_q_numbers_df, barmode='group',
                     title='Numbers in waiting lists at start and end of simulation',
                     labels={'value': 'Patients waiting',
                             'name': 'Stage of pathway',
                             'variable': 'Before or after simulation'})
        return fig
    
    # method to calculate queue numbers at end of simulation
    def readout_total_queue_numbers(self):

        return self.overall_q_numbers_df['After'].sum()
    
    # method to calculate average wait time at start of simulation
    def readout_wait_time_start(self):

        #read trial results csv
        trial_results_df = pd.read_csv('all_wait_times.csv')

        #return average wait time for patients who entered pathway on day 0
        return trial_results_df[trial_results_df['time_entered_pathway'] < 1]['overall_q_time'].mean()
    
    # method to calculate average wait time at end of simulation
    def readout_wait_time_end(self):

        # read trial results csv
        trial_results_df = pd.read_csv('all_wait_times.csv')

        # return average wait time for patients who entered pathway on final day of simulation
        last_day = self.sim_duration - 1
        return trial_results_df[trial_results_df['time_entered_pathway'] > last_day]['overall_q_time'].mean()

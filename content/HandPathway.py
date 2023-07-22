# A class containing functions to model the GSTT hand surgery pathway

import simpy
import random
import numpy as np
import pandas as pd
import csv

from HandPatient import Patient
from global_params import g

class Hand_Surgery_Pathway:

    def __init__(self, run_number,
                 referrals_per_week = g.referrals_per_week,
                 surg_clinic_per_week = g.surg_clinic_per_week,
                 surg_clinic_appts = g.surg_clinic_appts,
                 therapy_wait = g.therapy_wait,
                 imaging_wait = g.imaging_wait,
                 theatre_list_per_week = g.theatre_list_per_week,
                 theatre_list_capacity = g.theatre_list_capacity,
                 trauma_list_per_week = g.trauma_list_per_week,
                 trauma_extra_patients = g.trauma_extra_patients,
                 prob_needs_imaging = g.prob_needs_imaging,
                 prob_needs_therapy = g.prob_needs_therapy,
                 sim_duration = g.sim_duration,
                 fill_clinic_q = g.fill_clinic_q,
                 fill_imaging_q = g.fill_imaging_q,
                 fill_therapy_q = g.fill_therapy_q,
                 fill_theatre_q = g.fill_theatre_q
                 ):

        #setup environment
        self.env = simpy.Environment()
        self.active_entities = 0
        self.patient_counter = 0

        #setup values from defaults and calculate
        self.referrals_per_week = referrals_per_week
        self.referral_interval = 7 / referrals_per_week
        
        self.surg_clinic_per_week = surg_clinic_per_week
        self.surg_clinic_appts = surg_clinic_appts

        self.therapy_wait = therapy_wait
        self.imaging_wait = imaging_wait

        self.theatre_list_per_week = theatre_list_per_week
        self.theatre_list_capacity = theatre_list_capacity

        self.trauma_list_per_week = trauma_list_per_week
        self.trauma_extra_patients = trauma_extra_patients

        self.surg_clinic_duration = 1 / surg_clinic_appts
        self.surg_clinic_interval = 7 / surg_clinic_appts

        self.theatre_case_duration = 1 / theatre_list_capacity
        self.theatre_list_interval = 7 / theatre_list_per_week

        self.prob_needs_imaging = prob_needs_imaging
        self.prob_needs_therapy = prob_needs_therapy

        self.sim_duration = sim_duration

        self.fill_clinic_q = fill_clinic_q
        self.fill_imaging_q = fill_imaging_q
        self.fill_therapy_q = fill_therapy_q
        self.fill_theatre_q = fill_theatre_q

        self.total_fill_queues = fill_clinic_q + fill_imaging_q + fill_therapy_q + fill_theatre_q

        #create 'end of simulation' Event
        self.end_of_sim = self.env.event()

        #setup resources
        self.surg_clinic = simpy.Resource(self.env, capacity=1)
        self.theatres = simpy.Resource(self.env, capacity=1)

        self.run_number = run_number

        #variables to keep track of numbers in queues
        self.clinic_q = 0
        self.imaging_q = 0
        self.therapy_q = 0
        self.theatre_q = 0

        #create dataframe with queue times
        data = {'time_entered_pathway': [],
                'overall_q_time': []}
        self.q_times_df = pd.DataFrame(data)

    #method to determine if patient needs hand therapy
    def determine_therapy(self, patient):
        if random.uniform(0,1) < self.prob_needs_therapy:
            patient.needs_therapy = True

    #method to determine if patient needs imaging
    def determine_imaging(self, patient):
        if random.uniform(0,1) < self.prob_needs_imaging:
            patient.needs_imaging = True

    # method to determine before end sim
    def determine_end_sim(self, patient):
        if self.env.now >= self.sim_duration:
            patient.before_end_sim = False

    # method to pre fill queues with set numbers
    def prefill_queues(self):

        # fill clinic queue
        for i in range(self.fill_clinic_q):

            #increment patient counter by 1
            self.patient_counter += 1
            self.active_entities += 1

            #create new patient
            pt = Patient(self.patient_counter)

            #decide if needs hand therapy/imaging
            self.determine_imaging(pt)
            self.determine_therapy(pt)

            #get simpy env to run enter_pathway method with this patient
            self.env.process(self.enter_pathway(pt))

            # need to have yield statement so code works - timeout for zero time
            yield self.env.timeout(0)

        # fill imaging queue
        for i in range(self.fill_imaging_q):

            # increment patient counter by 1
            self.patient_counter += 1
            self.active_entities += 1

            # create new patient who needs imaging
            pt = Patient(self.patient_counter, already_seen_clinic = True,
                         needs_imaging = True)
            
            # determine if needs therapy
            self.determine_therapy(pt)

            # no need to determine if needs surg/therapy
            # as will skip straight to imaging queue
            # get simpy env to run enter_pathway method with this patient
            self.env.process(self.enter_pathway(pt))

            # need to have yield statement so code works - timeout for zero time
            yield self.env.timeout(0)

        # fill therapy queue
        for i in range(self.fill_therapy_q):

            # increment patient counter by 1
            self.patient_counter += 1
            self.active_entities += 1

            # create new patient who needs therapy
            pt = Patient(self.patient_counter, already_seen_clinic = True,
                         already_seen_imaging = True,
                         needs_therapy = True)

            # no need to determine if needs imaging
            # as will skip straight to therapy queue
            # get simpy env to run enter_pathway method with this patient
            self.env.process(self.enter_pathway(pt))

            # need to have yield statement so code works - timeout for zero time
            yield self.env.timeout(0)

        # fill theatre queue
        for i in range(self.fill_theatre_q):

            # increment patient counter by 1
            self.patient_counter += 1
            self.active_entities += 1

            # create new patient
            pt = Patient(self.patient_counter, already_seen_clinic = True,
                         already_seen_imaging = True,
                         already_seen_therapy = True)

            # no need to determine if needs surg/imaging/therapy
            # as will skip straight to theatre queue
            # get simpy env to run enter_pathway method with this patient
            self.env.process(self.enter_pathway(pt))

            # need to have yield statement so code works - timeout for zero time
            yield self.env.timeout(0)

    #method to generate patient referrals
    def generate_referrals(self):
        
        #keep generating indefinitely (until simulation ends)
        while True:
            
            #increment patient counter by 1
            self.patient_counter += 1
            
            #create new patient
            pt = Patient(self.patient_counter)
            
            #decide if needs hand therapy/imaging and end sim
            self.determine_imaging(pt)
            self.determine_therapy(pt) 
            self.determine_end_sim(pt)

            #if before end sim, increment counter
            if pt.before_end_sim == True:
                self.active_entities += 1
                
            #get simpy env to run enter_pathway method with this patient
            self.env.process(self.enter_pathway(pt))

            #randomly sample time to next referral
            sampled_interref_time = random.expovariate(1.0/self.referral_interval)
            
            #freeze until time has elapsed
            yield self.env.timeout(sampled_interref_time)

    #method to enter pathway
    def enter_pathway(self, patient):

        if not patient.already_seen_clinic:
            # record start of queue time and add to tracker
            start_q_clinic = self.env.now
            self.clinic_q += 1

            # request clinic resource
            with self.surg_clinic.request() as req:
                yield req

                # record end of queue time and add to tracker
                end_q_clinic = self.env.now
                self.clinic_q -= 1

                # record total queue time
                patient.clinic_q_time = end_q_clinic - start_q_clinic

                # freeze for clinic appointment duration
                yield self.env.timeout(self.surg_clinic_duration)


            # if needs imaging, timeout for imaging wait time
            if not patient.already_seen_imaging:
                if patient.needs_imaging == True:
                    self.imaging_q += 1
                    yield self.env.timeout(self.imaging_wait)
                    self.imaging_q -= 1

            # if needs therapy, timeout for therapy wait time
            if not patient.already_seen_therapy:
                if patient.needs_therapy == True:
                    self.therapy_q += 1
                    yield self.env.timeout(self.therapy_wait)
                    self.therapy_q -= 1

        # enter queue for theatres
        # record start of queue time and add to tracker
        start_q_theatres = self.env.now
        self.theatre_q += 1

        # request theatres resource
        with self.theatres.request() as req:
            yield req

            # record end of queue time and add to tracker
            end_q_theatres = self.env.now
            self.theatre_q -= 1

            # record theatre queue time and overall queue time
            patient.theatre_q_time = end_q_theatres - start_q_theatres
            patient.overall_q_time = end_q_theatres - start_q_clinic
            patient.time_entered_pathway = start_q_clinic

            # freeze for theatre case duration
            yield self.env.timeout(self.theatre_case_duration)
            
            # decrement counter if before end sim patient
            if patient.before_end_sim == True:
                self.active_entities -= 1

        # add patient to queue times dataframe
        if patient.id > self.total_fill_queues and patient.before_end_sim == True:
            self.store_queue_times(patient)

    # method to model interval between clinic appointments
    def clinic_unavail(self):

        #freeze clinic_unavail function for duration of clinic
        yield self.env.timeout(1)
        
        #request clinic with max priority and hold until next clinic
        with self.surg_clinic.request() as req:
            # Freeze the function until the request can be met (this
            # ensures that the last patient in clinic will be seen)
            yield req
            
            yield self.env.timeout(self.surg_clinic_interval)

    # method to model interval between theatre lists
    def theatres_unavail(self):
        
        #freeze theatres_unavail function for duration of list
        yield self.env.timeout(1)
        
        #request resource with max priority and hold until next list
        with self.theatres.request() as req:
            # Freeze the function until the request can be met (this
            # ensures that the last theatre case will be completed)
            yield req
            
            yield self.env.timeout(self.theatre_list_interval)

    # method to check if simulation should continue
    def monitor(self, env, active_entities, end_point, end_of_sim):
        while True:
            # check conditions every 1 time unit
            yield self.env.timeout(1)
            if self.env.now >= self.sim_duration and self.active_entities <= 0:
                # trigger end of simulation event
                self.end_of_sim.succeed()
                break
            #else:
                #print(self.active_entities)

    #method to store queue times
    def store_queue_times(self, patient):

        # create temporary dataframe with queue times
        df_to_add = pd.DataFrame({'time_entered_pathway': [patient.time_entered_pathway],
                                  'overall_q_time': [patient.overall_q_time]})

        # add to main dataframe
        self.q_times_df = pd.concat([self.q_times_df, df_to_add])

    # A method to save the wait times from this run to a csv file
    def write_queue_times(self):
        print(self.q_times_df.head())
        self.q_times_df.to_csv(f'wait_times_run_{self.run_number}.csv')

    # A method to write the queue numbers to a csv file
    def write_queue_numbers(self):
        with open('queue_numbers.csv', 'a', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerow([self.run_number, self.clinic_q, self.imaging_q,
                             self.therapy_q, self.theatre_q])
            
    # A method to run the simulation
    def run(self):
        # fill queues
        self.env.process(self.prefill_queues())

        # start entity generators
        self.env.process(self.generate_referrals())

        #simulate interval between clinics and lists
        self.env.process(self.clinic_unavail())
        self.env.process(self.theatres_unavail())

        #use monitor() to check if sim should end
        self.env.process(self.monitor(self.env, self.active_entities,
                                      self.sim_duration, self.end_of_sim))

        #run simulation
        self.env.run(until=self.end_of_sim)

        #write results to csv
        self.write_queue_times()
        self.write_queue_numbers()
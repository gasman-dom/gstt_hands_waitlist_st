# A class to store global default values for the simulation

class g:
    referrals_per_week = 10
    referral_interval = 7 / referrals_per_week
    
    #number of clinics per week and capacity
    surg_clinic_per_week = 2
    surg_clinic_appts = 6

    #average waiting times for imaging and hand therapy
    imaging_wait = 14
    therapy_wait = 30

    #appointments per week for imaging and hand therapy
    imaging_weekly_appts = 2
    therapy_weekly_appts = 2

    #theatre lists and cases per list
    theatre_list_per_week = 2
    theatre_list_capacity = 5

    trauma_list_per_week = 2
    trauma_extra_patients = 0
    
    #proportion of patients requiring interventions
    prob_needs_imaging = 0.25
    prob_needs_therapy = 0.25
    
    #length of simulation (days)
    sim_duration = 100
    
    #numbers to add to queues before simulation starts
    fill_clinic_q = 600
    fill_imaging_q = 300
    fill_therapy_q = 300
    fill_theatre_q = 600
    
    #number of times to run simulation
    number_of_runs = 5
# A class to store global default values for the simulation

class g:
    referrals_per_week = 50
    referral_interval = 7 / referrals_per_week
    
    #number of clinics per week and capacity
    surg_clinic_per_week = 1
    surg_clinic_appts = 8

    #average waiting times for imaging and hand therapy
    imaging_wait = 14
    therapy_wait = 30

    #theatre lists and cases per list
    theatre_list_per_week = 3
    theatre_list_capacity = 6
    
    surg_clinic_duration = 1 / surg_clinic_appts
    surg_clinic_interval = 7 / surg_clinic_per_week

    theatre_case_duration = 1 / theatre_list_capacity
    theatre_list_interval = 7 / theatre_list_per_week
    
    #proportion of patients requiring interventions
    prob_needs_imaging = 0.2
    prob_needs_therapy = 0.2
    
    #length of simulation (days)
    sim_duration = 100
    
    #numbers to add to queues before simulation starts
    fill_clinic_q = 100
    fill_imaging_q = 50
    fill_therapy_q = 40
    fill_theatre_q = 30

    total_fill_queues = fill_clinic_q + fill_imaging_q + fill_therapy_q + fill_theatre_q
    
    #number of times to run simulation
    number_of_runs = 5
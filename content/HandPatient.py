# A class representing patients referred to the GSTT hand surgery pathway

import random

class Patient:
    def __init__(self, p_id, already_seen_clinic=False,
                 already_seen_imaging=False, already_seen_therapy=False,
                 needs_imaging=False, needs_therapy=False,
                 before_end_sim=True):
        
        self.id = p_id
        self.needs_imaging = False
        self.needs_therapy = False

        self.time_entered_pathway = 0
        
        self.clinic_q_time = 0
        self.theatre_q_time = 0
        self.overall_q_time = 0

        #attributes to help with pre filling queues
        self.already_seen_clinic = False
        self.already_seen_imaging = False
        self.already_seen_therapy = False

        #attribute for before/after end of sim
        self.before_end_sim = True



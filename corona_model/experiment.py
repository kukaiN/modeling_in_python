only_medium = {"SC_WP":{
            # N = 150, L = 4, B = {G, L}, D = 0
            # f = 0.5, c = 0.90, h = 0.75, s' = 0.25
            "World": [
                ("TurnedOnInterventions", ["FaceMasks", "Quarantine", "ClosingBuildings", "LessSocial"]),
                ("ComplianceRatio", 0.5), # f = 0.5
            ],
            "Quarantine": [
                ("ResultLatency", 4*24), # L = 4
                ("BatchSize", 150), # N=150
                ("ShowingUpForScreening", 0.9), # c = 0.9#############
            ],
            "ClosingBuildings": [
            ("ClosedBuildingOpenHub", []),
            ("ClosedBuilding_ByType", ["gym", "library"]),
            ("GoingHomeP", 0.75), # h = 0.75 ##################
            ("Exception_SemiClosedBuilding", []),
            ("Exception_GoingHomeP", 0.75),
            ],
            "LessSocializing":[
                ("StayingHome",0.25), # s' = 0.25 ######################
            ],
        },}

medium_student_vary_policy = {
    "SC_WP":{
            # N = 150, L = 4, B = {G, L}, D = 0
            # f = 0.5, c = 0.90, h = 0.75, s' = 0.25
            "World": [
                ("TurnedOnInterventions", ["FaceMasks", "Quarantine", "ClosingBuildings", "LessSocial"]),
                ("ComplianceRatio", 0.5), # f = 0.5
            ],
            "Quarantine": [
                ("ResultLatency", 4*24), # L = 4
                ("BatchSize", 150), # N=150
                ("ShowingUpForScreening", 0.9), # c = 0.9#############
            ],
            "ClosingBuildings": [
            ("ClosedBuildingOpenHub", []),
            ("ClosedBuilding_ByType", ["gym", "library"]),
            ("GoingHomeP", 0.75), # h = 0.75 ##################
            ("Exception_SemiClosedBuilding", []),
            ("Exception_GoingHomeP", 0.75),
            ],
            "LessSocializing":[
                ("StayingHome",0.25), # s' = 0.25 ######################
            ],
        },
        "SC_MP":{
            #N = 250, L = 3, B = {G, L, DH, LG}, D=650
            # f = 0.5, c = 0.90, h = 0.75, s' = 0.25
            "World": [
                ("TurnedOnInterventions", ["FaceMasks", "Quarantine", "ClosingBuildings", "LessSocial", "HybridClasses"]),
                ("ComplianceRatio", 0.5), # f = 0.5
            ],
            "Quarantine": [
                ("ResultLatency", 3*24), # L = 3
                ("BatchSize", 250), # N=250
                ("ShowingUpForScreening", 0.9), # c = 0.9
            ],
            "ClosingBuildings": [
                ("ClosedBuildingOpenHub", ["dining"]), # ding stays open, but leaf Kv = 0
                ("ClosedBuilding_ByType", ["gym", "library"]),
                ("GoingHomeP", 0.75), # h = 0.75
                ("Exception_SemiClosedBuilding", ["dining", "faculty_dining_room"]), # replace these entrys 50/50
                ("Exception_GoingHomeP", 0.75),
            ],
            "LessSocializing":[
                ("StayingHome",0.25), # s' = 0.25
            ],
            "HybridClass":[
                ("RemoteStudentCount", 250),
                ("RemoteFacultyCount", 150),
                ("RemovedDoubleCount", 325), # 525 - 250 = 275
                ("OffCampusCount", 250),
                ("TurnOffLargeGathering", True),
                ("ChangedSeedNumber", 7),
            ],
        },
        "SC_SP":{
            #N = 500, L = 2, B = {G, L, DH, LG, O}, D=1300
            # f = 0.5, c = 0.90, h = 0.75, s' = 0.25
            "World": [
                ("TurnedOnInterventions", ["FaceMasks", "Quarantine", "ClosingBuildings", "LessSocial", "HybridClasses"]),
                ("ComplianceRatio", 0.5), # f = 0.5
            ],
            "Quarantine": [
                ("ResultLatency", 2*24), # L = 2
                ("BatchSize", 500), # N=500
                ("ShowingUpForScreening", 0.9), # c = 0.9
            ],
            "ClosingBuildings": [
                ("ClosedBuildingOpenHub", ["dining"]),
                ("ClosedBuilding_ByType", ["gym", "library", "office"]),
                ("GoingHomeP", 0.75), # h = 0.75
                ("Exception_SemiClosedBuilding", ["dining", "faculty_dining_room"]),
                ("Exception_GoingHomeP", 0.75), # h = 0.5
            ],
            "LessSocializing":[
                ("StayingHome",0.25), # s' = 0.25
            ],
            "HybridClass":[
                ("RemoteStudentCount", 500),
                ("RemoteFacultyCount", 300),
                ("RemovedDoubleCount", 525), #525 = total number of double
                ("OffCampusCount", 500),
                ("TurnOffLargeGathering", True),
                ("ChangedSeedNumber", 5),
            ]
        },
}

off_campus_multiplier = {
    "OCM_1x": {"Infection" : [("offCampusInfectionMultiplyer", 1)]},
    "OCM_2x": {"Infection" : [("offCampusInfectionMultiplyer", 2)]},
    "OCM_4x": {"Infection" : [("offCampusInfectionMultiplyer", 4)]},
    "OCM_8x": {"Infection" : [("offCampusInfectionMultiplyer", 8)]},
}
original_multiplier = {
    "OCM_0.1x": {"Infection" : [("offCampusInfectionMultiplyer", 0.1)]}
}
new_batch1 = {
    "BTC_150": {"Quarantine": [("BatchSize", 150)]},
    "BTC_160": {"Quarantine": [("BatchSize", 160)]},
    "BTC_170": {"Quarantine": [("BatchSize", 170)]},
    "BTC_180": {"Quarantine": [("BatchSize", 180)]},
    "BTC_190": {"Quarantine": [("BatchSize", 190)]},
    "BTC_200": {"Quarantine": [("BatchSize", 200)]},
    "BTC_210": {"Quarantine": [("BatchSize", 210)]},
    "BTC_220": {"Quarantine": [("BatchSize", 220)]},
    "BTC_230": {"Quarantine": [("BatchSize", 230)]},
    "BTC_240": {"Quarantine": [("BatchSize", 240)]},
    "BTC_250": {"Quarantine": [("BatchSize", 250)]},
}
new_batch2 = {
    "BTC_275": {"Quarantine": [("BatchSize", 275)]},
    "BTC_300": {"Quarantine": [("BatchSize", 300)]},
    "BTC_350": {"Quarantine": [("BatchSize", 350)]},
    "BTC_400": {"Quarantine": [("BatchSize", 400)]},
    "BTC_450": {"Quarantine": [("BatchSize", 450)]},
    "BTC_500": {"Quarantine": [("BatchSize", 500)]},
    "BTC_550": {"Quarantine": [("BatchSize", 550)]},
    "BTC_600": {"Quarantine": [("BatchSize", 600)]},
    "BTC_650": {"Quarantine": [("BatchSize", 650)]},
    "BTC_700": {"Quarantine": [("BatchSize", 700)]},

}

new_ControlledExperiment1 = {
    "base_case1":{},
    "v1_f0":{
        "Agents":[
            ("immunity", 0.05),
            ("vaccine", True),
            ("vaccineEffectiveness", 0.9),
            ("vaccinatedPopulation",0.3),
        ],
        "World": [
                ("TurnedOnInterventions", ["FaceMasks"]),
        ],
        "FaceMasks":[
            ("use_compliance", False),
            ("Facemask_mode", 0),
        ],
    },
    "v1_f1":{
        "Agents":[
            ("immunity", 0.05),
            ("vaccine", True),
            ("vaccineEffectiveness", 0.9),
            ("vaccinatedPopulation",0.3),
        ],
        "World": [
                ("TurnedOnInterventions", ["FaceMasks"]),
        ],
        "FaceMasks":[
            ("use_compliance", False),
            ("Facemask_mode", 1),
        ],
    },
    "v1_f2":{
        "Agents":[
            ("immunity", 0.05),
            ("vaccine", True),
            ("vaccineEffectiveness", 0.9),
            ("vaccinatedPopulation",0.3),
        ],
        "World": [
                ("TurnedOnInterventions", ["FaceMasks"]),
        ],
        "FaceMasks":[
            ("use_compliance", False),
            ("Facemask_mode", 2),
        ],
    },
    "v2_f0":{
        "Agents":[
            ("immunity", 0.05),
            ("vaccine", True),
            ("vaccineEffectiveness", 0.9),
            ("vaccinatedPopulation",0.6),
        ],
        "World": [
                ("TurnedOnInterventions", ["FaceMasks"]),
        ],
        "FaceMasks":[
            ("use_compliance", False),
            ("Facemask_mode", 0),
        ],
    },
    "v2_f1":{
        "Agents":[
                    ("immunity", 0.05),
            ("vaccine", True),
            ("vaccineEffectiveness", 0.9),
            ("vaccinatedPopulation",0.6),
        ],
        "World": [
                ("TurnedOnInterventions", ["FaceMasks"]),
        ],
        "FaceMasks":[
            ("use_compliance", False),
            ("Facemask_mode", 1),
        ],
    },
    "v2_f2":{
        "Agents":[
                    ("immunity", 0.05),
            ("vaccine", True),
            ("vaccineEffectiveness", 0.9),
            ("vaccinatedPopulation",0.6),
        ],
        "World": [
                ("TurnedOnInterventions", ["FaceMasks"]),
        ],
        "FaceMasks":[
            ("use_compliance", False),
            ("Facemask_mode", 2),
        ],
    },
    "v3_f0":{
        "Agents":[
                    ("immunity", 0.05),
            ("vaccine", True),
            ("vaccineEffectiveness", 0.9),
            ("vaccinatedPopulation",0.9),
        ],
        "World": [
                ("TurnedOnInterventions", ["FaceMasks"]),
        ],
        "FaceMasks":[
            ("use_compliance", False),
            ("Facemask_mode", 0),
        ],
    },
    "v3_f1":{
        "Agents":[
            ("immunity", 0.05),
            ("vaccine", True),
            ("vaccineEffectiveness", 0.9),
            ("vaccinatedPopulation",0.9),
        ],
        "World": [
                ("TurnedOnInterventions", ["FaceMasks"]),
        ],
        "FaceMasks":[
            ("use_compliance", False),
            ("Facemask_mode", 1),
        ],
    },
    "v3_f2":{
        "Agents":[
            ("immunity", 0.05),
            ("vaccine", True),
            ("vaccineEffectiveness", 0.9),
            ("vaccinatedPopulation",0.9),
        ],
        "World": [
                ("TurnedOnInterventions", ["FaceMasks"]),
        ],
        "FaceMasks":[
            ("use_compliance", False),
            ("Facemask_mode", 2),
        ],
    }
}

low_med = {
    "NC_WP":{
        # N = 150, L = 4, B = {G, L}, D = 0
        # f = 0, c = 0.80, h = 0.50, s' = 0
        "World": [
            ("TurnedOnInterventions", ["FaceMasks", "Quarantine", "LessSocial", "ClosingBuildings"]),
            ("ComplianceRatio", 0), # f = 0
        ],
        "Quarantine": [
            ("ResultLatency", 4*24), # L = 4
            ("BatchSize", 150), # N=150
            ("ShowingUpForScreening", 0.8), # c = 0.8
        ],
        "ClosingBuildings": [
        ("ClosedBuildingOpenHub", []),
        ("ClosedBuilding_ByType", ["gym", "library"]),
        ("GoingHomeP", 0.5), # h = 0.5
        ("Exception_SemiClosedBuilding", []),
        ("Exception_GoingHomeP", 0.5),
        ],
        "LessSocializing":[
            ("StayingHome",0), # s'
        ],
    },
    "NC_MP":{
        #N = 250, L = 3, B = {G, L, DH, LG}, D=650
        # f = 0, c = 0.80, h = 0.50, s' = 0
        "World": [
            ("TurnedOnInterventions", ["FaceMasks", "Quarantine", "ClosingBuildings", "LessSocial", "HybridClasses"]),
            ("ComplianceRatio", 0), # f = 0
            ("LargeGathering", False)
        ],
        "Quarantine": [
            ("ResultLatency", 3*24), # L = 3
            ("BatchSize", 250), # N=250
            ("ShowingUpForScreening", 0.8), # c = 0.8
        ],
        "ClosingBuildings": [
            ("ClosedBuildingOpenHub", ["dining"]), # ding stays open, but leaf Kv = 0####################################
            ("ClosedBuilding_ByType", ["gym", "library"]),
            ("GoingHomeP", 0.5), # h = 0.5
            ("Exception_SemiClosedBuilding",["dining", "faculty_dining_room"]), # replace these entrys 50/50###############
            ("Exception_GoingHomeP", 0.5),
        ],
        "LessSocializing":[
            ("StayingHome",0), # s'
        ],
        "HybridClass":[############################################################
            ("RemoteStudentCount", 250),
            ("RemoteFacultyCount", 150),
            ("RemovedDoubleCount", 325), # 525 doubles, extra agents = 200, means need 200 double beds available
            ("OffCampusCount", 250),
            ("TurnOffLargeGathering", True),
            ("ChangedSeedNumber", 7),
        ],
    },
    "NC_SP":{
        #N = 500, L = 2, B = {G, L, DH, LG, O}, D=1300
        # f = 0, c = 0.80, h = 0.50, s' = 0
        "World": [
            ("TurnedOnInterventions", ["FaceMasks", "Quarantine", "ClosingBuildings", "LessSocial", "HybridClasses"]),
            ("ComplianceRatio", 0), # f = 0
            ("LargeGathering", False)
        ],
        "Quarantine": [
            ("ResultLatency", 2*24), # L = 2
            ("BatchSize", 500), # N=500
            ("ShowingUpForScreening", 0.8), # c=0.8
        ],
        "ClosingBuildings": [
            ("ClosedBuildingOpenHub", ["dining"]),
            ("ClosedBuilding_ByType", ["gym", "library", "office"]),
            ("GoingHomeP", 0.5), # h = 0.5
            ("Exception_SemiClosedBuilding", ["dining", "faculty_dining_room"]),
            ("Exception_GoingHomeP", 0.5), # h = 0.5
        ],
        "LessSocializing":[
            ("StayingHome",0), # s'
        ],
        "HybridClass":[
            ("RemoteStudentCount", 500),
            ("RemoteFacultyCount", 300),
            ("RemovedDoubleCount", 525), #525 = total number of double
            ("OffCampusCount", 500),
            ("TurnOffLargeGathering", True),
            ("ChangedSeedNumber", 5),
        ],
    },

    "SC_WP":{
        # N = 150, L = 4, B = {G, L}, D = 0
        # f = 0.5, c = 0.90, h = 0.75, s' = 0.25
        "World": [
            ("TurnedOnInterventions", ["FaceMasks", "Quarantine", "ClosingBuildings", "LessSocial"]),
            ("ComplianceRatio", 0.5), # f = 0.5
        ],
        "Quarantine": [
            ("ResultLatency", 4*24), # L = 4
            ("BatchSize", 150), # N=150
            ("ShowingUpForScreening", 0.9), # c = 0.9#############
        ],
        "ClosingBuildings": [
        ("ClosedBuildingOpenHub", []),
        ("ClosedBuilding_ByType", ["gym", "library"]),
        ("GoingHomeP", 0.75), # h = 0.75 ##################
        ("Exception_SemiClosedBuilding", []),
        ("Exception_GoingHomeP", 0.75),
        ],
        "LessSocializing":[
            ("StayingHome",0.25), # s' = 0.25 ######################
        ],
    },
    "SC_MP":{
        #N = 250, L = 3, B = {G, L, DH, LG}, D=650
        # f = 0.5, c = 0.90, h = 0.75, s' = 0.25
        "World": [
            ("TurnedOnInterventions", ["FaceMasks", "Quarantine", "ClosingBuildings", "LessSocial", "HybridClasses"]),
            ("ComplianceRatio", 0.5), # f = 0.5
        ],
        "Quarantine": [
            ("ResultLatency", 3*24), # L = 3
            ("BatchSize", 250), # N=250
            ("ShowingUpForScreening", 0.9), # c = 0.9
        ],
        "ClosingBuildings": [
            ("ClosedBuildingOpenHub", ["dining"]), # ding stays open, but leaf Kv = 0
            ("ClosedBuilding_ByType", ["gym", "library"]),
            ("GoingHomeP", 0.75), # h = 0.75
            ("Exception_SemiClosedBuilding", ["dining", "faculty_dining_room"]), # replace these entrys 50/50
            ("Exception_GoingHomeP", 0.75),
        ],
        "LessSocializing":[
            ("StayingHome",0.25), # s' = 0.25
        ],
        "HybridClass":[
            ("RemoteStudentCount", 250),
            ("RemoteFacultyCount", 150),
            ("RemovedDoubleCount", 325), # 525 - 250 = 275
            ("OffCampusCount", 250),
            ("TurnOffLargeGathering", True),
            ("ChangedSeedNumber", 7),
        ],
    },
    "SC_SP":{
        #N = 500, L = 2, B = {G, L, DH, LG, O}, D=1300
        # f = 0.5, c = 0.90, h = 0.75, s' = 0.25
        "World": [
            ("TurnedOnInterventions", ["FaceMasks", "Quarantine", "ClosingBuildings", "LessSocial", "HybridClasses"]),
            ("ComplianceRatio", 0.5), # f = 0.5
        ],
        "Quarantine": [
            ("ResultLatency", 2*24), # L = 2
            ("BatchSize", 500), # N=500
            ("ShowingUpForScreening", 0.9), # c = 0.9
        ],
        "ClosingBuildings": [
            ("ClosedBuildingOpenHub", ["dining"]),
            ("ClosedBuilding_ByType", ["gym", "library", "office"]),
            ("GoingHomeP", 0.75), # h = 0.75
            ("Exception_SemiClosedBuilding", ["dining", "faculty_dining_room"]),
            ("Exception_GoingHomeP", 0.75), # h = 0.5
        ],
        "LessSocializing":[
            ("StayingHome",0.25), # s' = 0.25
        ],
        "HybridClass":[
            ("RemoteStudentCount", 500),
            ("RemoteFacultyCount", 300),
            ("RemovedDoubleCount", 525), #525 = total number of double
            ("OffCampusCount", 500),
            ("TurnOffLargeGathering", True),
            ("ChangedSeedNumber", 5),
        ]
    },
}
vaccine3 = {
    "v1" : {
        "Agents":[
            ("immunity", 0.05),
            ("vaccine", True),
            ("vaccineEffectiveness", 0.9),
            ("vaccinatedPopulation",0.3),
        ],
    },
    "v2" : {
        "Agents":[
            ("immunity", 0.05),
            ("vaccine", True),
            ("vaccineEffectiveness", 0.9),
            ("vaccinatedPopulation",0.6),
        ],
    },
    "v3" : {
        "Agents":[
            ("immunity", 0.05),
            ("vaccine", True),
            ("vaccineEffectiveness", 0.9),
            ("vaccinatedPopulation",0.9),
        ],
    },
}

# 30, 50, 70, 90
vaccine4 = {
    "v1" : {
        "World": [
                ("TurnedOnInterventions", ["FaceMasks",  "Quarantine"]),
        ],
        "Agents":[
            ("immunity", 0.05),
            ("vaccine", True),
            ("vaccineEffectiveness", 0.9),
            ("vaccinatedPopulation",0.3),
        ],
            "Quarantine" : [
            # this dictates if we randomly sample the population or cycle through Batches
            ("RandomSampling", False),
            ("ResultLatency",3*24),
            ("WalkIn",True),
            ("BatchSize" , 250),
            ("OnlySampleUnvaccinated",True),
            ],
    },
    "v2" : {
        "World": [
                ("TurnedOnInterventions", ["FaceMasks",  "Quarantine"]),
        ],
        "Agents":[
            ("immunity", 0.05),
            ("vaccine", True),
            ("vaccineEffectiveness", 0.9),
            ("vaccinatedPopulation",0.5),
        ],
            "Quarantine" : [
            # this dictates if we randomly sample the population or cycle through Batches
            ("RandomSampling", False),
            ("ResultLatency",3*24),
            ("WalkIn",True),
            ("BatchSize" , 250),
            ("OnlySampleUnvaccinated",True),
            ],
    },

    "v3" : {
        "World": [
                ("TurnedOnInterventions", ["FaceMasks",  "Quarantine"]),
        ],
        "Agents":[
            ("immunity", 0.05),
            ("vaccine", True),
            ("vaccineEffectiveness", 0.9),
            ("vaccinatedPopulation",0.7),
        ],
        "Quarantine" : [
            # this dictates if we randomly sample the population or cycle through Batches
            ("RandomSampling", False),
            ("ResultLatency",3*24),
            ("WalkIn",True),
            ("BatchSize" , 250),
            ("OnlySampleUnvaccinated",True),
            ],
    },

    "v4" : {
        "World": [
                ("TurnedOnInterventions", ["FaceMasks",  "Quarantine"]),
        ],
        "Agents":[
            ("immunity", 0.05),
            ("vaccine", True),
            ("vaccineEffectiveness", 0.9),
            ("vaccinatedPopulation",0.9),
        ],
        "Quarantine" : [
            # this dictates if we randomly sample the population or cycle through Batches
            ("RandomSampling", False),
            ("ResultLatency",3*24),
            ("WalkIn",True),
            ("BatchSize" , 250),
            ("OnlySampleUnvaccinated",True),
            ],
    }
}

# 0, 1, 2
facemask3 = {
    "f0": {
        "FaceMasks":[
            ("use_compliance", False),
            ("Facemask_mode", 0),
        ],
    },
    "f1": {
            "FaceMasks":[
            ("use_compliance", False),
            ("Facemask_mode", 1),
        ],
    },
    "f2": {
            "FaceMasks":[
            ("use_compliance", False),
            ("Facemask_mode", 2),
            ],
    }
}

different_base_p = {
    "p1.00": {"Infection" : [("baseP" , 1.00)],},
    "p1.05": {"Infection" : [("baseP" , 1.05)],},
    "p1.10": {"Infection" : [("baseP" , 1.10)],},
    "p1.15": {"Infection" : [("baseP" , 1.15)],},
    "p1.20": {"Infection" : [("baseP" , 1.20)],},
    "p1.25": {"Infection" : [("baseP" , 1.25)],},
    "p1.30": {"Infection" : [("baseP" , 1.30)],},
    "p1.35": {"Infection" : [("baseP" , 1.35)],},
    "p1.40": {"Infection" : [("baseP" , 1.40)],},
    "p1.45": {"Infection" : [("baseP" , 1.45)],},
    "p1.50": {"Infection" : [("baseP" , 1.50)],},
}
different_base_p_jump_025 = {
    "p0.50": {"Infection": [("baseP", 0.5)]},
    "p0.75": {"Infection": [("baseP", 0.75)]},
    "p1.00": {"Infection": [("baseP", 1)]},
    "p1.25": {"Infection": [("baseP", 1.25)]},
    "p1.50": {"Infection": [("baseP", 1.5)]},
}

base_p_initial_count_experiment = {
    "p125_10" : { "Infection" : [("baseP" , 1.25), ("SeedNumber", 10)]},
    "p125_20" : {"Infection" : [("baseP" , 1.25), ("SeedNumber", 20)]},
    "p125_30" : {"Infection" : [("baseP" , 1.25), ("SeedNumber", 30)]},
    "p125_40" : {"Infection" : [("baseP" , 1.25), ("SeedNumber", 40)]},
    "p125_50" : {"Infection" : [("baseP" , 1.25), ("SeedNumber", 50)]},
    "p125_60" : {"Infection" : [("baseP" , 1.25), ("SeedNumber", 60)]},
    "p125_70" : {"Infection" : [("baseP" , 1.25), ("SeedNumber", 70)]},
    "p125_80" : {"Infection" : [("baseP" , 1.25), ("SeedNumber", 80)]},
    "p125_90" : {"Infection" : [("baseP" , 1.25), ("SeedNumber", 90)]},
    "p125_100" : {"Infection" : [("baseP" , 1.25), ("SeedNumber", 100)]},

}

old_ControlledExperiment = {
    "baseModel":{
    }, # no changes
    "facemasks":{
        "World": [
            ("TurnedOnInterventions", ["FaceMasks"]),
            ("ComplianceRatio", 1),
            ],
    },
    "highDeden":{
        "World": [
            ("TurnedOnInterventions", ["HybridClasses"]),
            ],
        "HybridClass":[
            ("RemoteStudentCount", 500),
            ("RemoteFacultyCount", 300),
            ("RemovedDoubleCount", 525),
            ("OffCampusCount", 500),
            ("TurnOffLargeGathering", True),
            ("ChangedSeedNumber", 5),
        ],
    },
    "lessSocial":{
        "World": [
            ("TurnedOnInterventions", ["LessSocial"]),
            ],
    },
    "Quarantine":{
        "World": [
            ("TurnedOnInterventions", ["Quarantine"]),
        ],
        "Quarantine": [
            ("ResultLatency", 2*24),
            ("BatchSize", 500),
            ("ShowingUpForScreening", 1),
        ],
    },
    "Medium+L4":{
        "World": [
            ("TurnedOnInterventions", ["Quarantine","HybridClasses"]),
        ],
            "Quarantine": [
            ("ResultLatency", 4*24), # L = 4
            ("BatchSize", 250), # N=250
            ("ShowingUpForScreening", 1), # c = 1
        ],
        "HybridClass":[
            ("RemoteStudentCount", 250),
            ("RemoteFacultyCount", 150),
            ("RemovedDoubleCount", 325), # 525 - 250 = 275
            ("OffCampusCount", 250),
            ("TurnOffLargeGathering", False),
            ("ChangedSeedNumber", 7),
        ],
    },
    "Medium+L3":{
        "World": [
            ("TurnedOnInterventions", ["Quarantine","HybridClasses"]),
        ],
            "Quarantine": [
            ("ResultLatency", 3*24), # L = 3
            ("BatchSize", 250), # N=250
            ("ShowingUpForScreening", 1), # c = 1
        ],
        "HybridClass":[
            ("RemoteStudentCount", 250),
            ("RemoteFacultyCount", 150),
            ("RemovedDoubleCount", 325), # 525 - 250 = 275
            ("OffCampusCount", 250),
            ("TurnOffLargeGathering", False),
            ("ChangedSeedNumber", 7),
        ],
    },
    "Medium+L2":{
        "World": [
            ("TurnedOnInterventions", ["Quarantine","HybridClasses"]),
        ],
            "Quarantine": [
            ("ResultLatency", 2*24), # L = 2
            ("BatchSize", 250), # N=250
            ("ShowingUpForScreening", 1), # c = 1
        ],
        "HybridClass":[
            ("RemoteStudentCount", 250),
            ("RemoteFacultyCount", 150),
            ("RemovedDoubleCount", 325), # 525 - 250 = 275
            ("OffCampusCount", 250),
            ("TurnOffLargeGathering", False),
            ("ChangedSeedNumber", 7),
        ],
    },
    "Medium+L1":{
        "World": [
            ("TurnedOnInterventions", ["Quarantine","HybridClasses"]),
        ],
            "Quarantine": [
            ("ResultLatency", 1*24), # L = 1
            ("BatchSize", 250), # N=250
            ("ShowingUpForScreening", 1), # c = 1
        ],
        "HybridClass":[
            ("RemoteStudentCount", 250),
            ("RemoteFacultyCount", 150),
            ("RemovedDoubleCount", 325), # 525 - 250 = 275
            ("OffCampusCount", 250),
            ("TurnOffLargeGathering", False),
            ("ChangedSeedNumber", 7),
        ],
    },
}

original_3x3 = {
    "NC_WP":{
        # N = 150, L = 4, B = {G, L}, D = 0
        # f = 0, c = 0.80, h = 0.50, s' = 0
        "World": [
            ("TurnedOnInterventions", ["FaceMasks", "Quarantine", "LessSocial", "ClosingBuildings"]),
            ("ComplianceRatio", 0), # f = 0
        ],
        "Quarantine": [
            ("ResultLatency", 4*24), # L = 4
            ("BatchSize", 150), # N=150
            ("ShowingUpForScreening", 0.8), # c = 0.8
        ],
        "ClosingBuildings": [
        ("ClosedBuildingOpenHub", []),
        ("ClosedBuilding_ByType", ["gym", "library"]),
        ("GoingHomeP", 0.5), # h = 0.5
        ("Exception_SemiClosedBuilding", []),
        ("Exception_GoingHomeP", 0.5),
        ],
        "LessSocializing":[
            ("StayingHome",0), # s'
        ],
    },
    "NC_MP":{
        #N = 250, L = 3, B = {G, L, DH, LG}, D=650
        # f = 0, c = 0.80, h = 0.50, s' = 0
        "World": [
            ("TurnedOnInterventions", ["FaceMasks", "Quarantine", "ClosingBuildings", "LessSocial", "HybridClasses"]),
            ("ComplianceRatio", 0), # f = 0
            ("LargeGathering", False)
        ],
        "Quarantine": [
            ("ResultLatency", 3*24), # L = 3
            ("BatchSize", 250), # N=250
            ("ShowingUpForScreening", 0.8), # c = 0.8
        ],
        "ClosingBuildings": [
            ("ClosedBuildingOpenHub", ["dining"]), # ding stays open, but leaf Kv = 0####################################
            ("ClosedBuilding_ByType", ["gym", "library"]),
            ("GoingHomeP", 0.5), # h = 0.5
            ("Exception_SemiClosedBuilding",["dining", "faculty_dining_room"]), # replace these entrys 50/50###############
            ("Exception_GoingHomeP", 0.5),
        ],
        "LessSocializing":[
            ("StayingHome",0), # s'
        ],
        "HybridClass":[############################################################
            ("RemoteStudentCount", 250),
            ("RemoteFacultyCount", 150),
            ("RemovedDoubleCount", 325), # 525 doubles, extra agents = 200, means need 200 double beds available
            ("OffCampusCount", 250),
            ("TurnOffLargeGathering", True),
            ("ChangedSeedNumber", 7),
        ],
    },
    "NC_SP":{
        #N = 500, L = 2, B = {G, L, DH, LG, O}, D=1300
        # f = 0, c = 0.80, h = 0.50, s' = 0
        "World": [
            ("TurnedOnInterventions", ["FaceMasks", "Quarantine", "ClosingBuildings", "LessSocial", "HybridClasses"]),
            ("ComplianceRatio", 0), # f = 0
            ("LargeGathering", False)
        ],
        "Quarantine": [
            ("ResultLatency", 2*24), # L = 2
            ("BatchSize", 500), # N=500
            ("ShowingUpForScreening", 0.8), # c=0.8
        ],
        "ClosingBuildings": [
            ("ClosedBuildingOpenHub", ["dining"]),
            ("ClosedBuilding_ByType", ["gym", "library", "office"]),
            ("GoingHomeP", 0.5), # h = 0.5
            ("Exception_SemiClosedBuilding", ["dining", "faculty_dining_room"]),
            ("Exception_GoingHomeP", 0.5), # h = 0.5
        ],
        "LessSocializing":[
            ("StayingHome",0), # s'
        ],
        "HybridClass":[
            ("RemoteStudentCount", 500),
            ("RemoteFacultyCount", 300),
            ("RemovedDoubleCount", 525), #525 = total number of double
            ("OffCampusCount", 500),
            ("TurnOffLargeGathering", True),
            ("ChangedSeedNumber", 5),
        ],
    },

    "SC_WP":{
        # N = 150, L = 4, B = {G, L}, D = 0
        # f = 0.5, c = 0.90, h = 0.75, s' = 0.25
        "World": [
            ("TurnedOnInterventions", ["FaceMasks", "Quarantine", "ClosingBuildings", "LessSocial"]),
            ("ComplianceRatio", 0.5), # f = 0.5
        ],
        "Quarantine": [
            ("ResultLatency", 4*24), # L = 4
            ("BatchSize", 150), # N=150
            ("ShowingUpForScreening", 0.9), # c = 0.9#############
        ],
        "ClosingBuildings": [
        ("ClosedBuildingOpenHub", []),
        ("ClosedBuilding_ByType", ["gym", "library"]),
        ("GoingHomeP", 0.75), # h = 0.75 ##################
        ("Exception_SemiClosedBuilding", []),
        ("Exception_GoingHomeP", 0.75),
        ],
        "LessSocializing":[
            ("StayingHome",0.25), # s' = 0.25 ######################
        ],
    },
    "SC_MP":{
        #N = 250, L = 3, B = {G, L, DH, LG}, D=650
        # f = 0.5, c = 0.90, h = 0.75, s' = 0.25
        "World": [
            ("TurnedOnInterventions", ["FaceMasks", "Quarantine", "ClosingBuildings", "LessSocial", "HybridClasses"]),
            ("ComplianceRatio", 0.5), # f = 0.5
        ],
        "Quarantine": [
            ("ResultLatency", 3*24), # L = 3
            ("BatchSize", 250), # N=250
            ("ShowingUpForScreening", 0.9), # c = 0.9
        ],
        "ClosingBuildings": [
            ("ClosedBuildingOpenHub", ["dining"]), # ding stays open, but leaf Kv = 0
            ("ClosedBuilding_ByType", ["gym", "library"]),
            ("GoingHomeP", 0.75), # h = 0.75
            ("Exception_SemiClosedBuilding", ["dining", "faculty_dining_room"]), # replace these entrys 50/50
            ("Exception_GoingHomeP", 0.75),
        ],
        "LessSocializing":[
            ("StayingHome",0.25), # s' = 0.25
        ],
        "HybridClass":[
            ("RemoteStudentCount", 250),
            ("RemoteFacultyCount", 150),
            ("RemovedDoubleCount", 325), # 525 - 250 = 275
            ("OffCampusCount", 250),
            ("TurnOffLargeGathering", True),
            ("ChangedSeedNumber", 7),
        ],
    },
    "SC_SP":{
        #N = 500, L = 2, B = {G, L, DH, LG, O}, D=1300
        # f = 0.5, c = 0.90, h = 0.75, s' = 0.25
        "World": [
            ("TurnedOnInterventions", ["FaceMasks", "Quarantine", "ClosingBuildings", "LessSocial", "HybridClasses"]),
            ("ComplianceRatio", 0.5), # f = 0.5
        ],
        "Quarantine": [
            ("ResultLatency", 2*24), # L = 2
            ("BatchSize", 500), # N=500
            ("ShowingUpForScreening", 0.9), # c = 0.9
        ],
        "ClosingBuildings": [
            ("ClosedBuildingOpenHub", ["dining"]),
            ("ClosedBuilding_ByType", ["gym", "library", "office"]),
            ("GoingHomeP", 0.75), # h = 0.75
            ("Exception_SemiClosedBuilding", ["dining", "faculty_dining_room"]),
            ("Exception_GoingHomeP", 0.75), # h = 0.5
        ],
        "LessSocializing":[
            ("StayingHome",0.25), # s' = 0.25
        ],
        "HybridClass":[
            ("RemoteStudentCount", 500),
            ("RemoteFacultyCount", 300),
            ("RemovedDoubleCount", 525), #525 = total number of double
            ("OffCampusCount", 500),
            ("TurnOffLargeGathering", True),
            ("ChangedSeedNumber", 5),
        ]
    },
    "VC_WP":{
        # N = 150, L = 4, B = {G, L}, D = 0
        # f = 1, c = 1, h = 1, s' = 0.75, no large gatherings
        "World": [
            ("TurnedOnInterventions", ["FaceMasks", "Quarantine", "ClosingBuildings", "LessSocial"]),
            ("ComplianceRatio", 1), # f = 1
            ("LargeGathering", False),
        ],
        "Quarantine": [
            ("ResultLatency", 4*24),
                # L = 4
            ("BatchSize", 150), # N=150
            ("ShowingUpForScreening", 1), # c = 1
        ],
        "ClosingBuildings": [
        ("ClosedBuildingOpenHub", []),
        ("ClosedBuilding_ByType", ["gym", "library"]),
        ("GoingHomeP", 1), # h = 1
        ("Exception_SemiClosedBuilding", []),
        ("Exception_GoingHomeP", 1),
        ],
        "LessSocializing":[
            ("StayingHome",0.75), # s'
        ],
    },
    "VC_MP":{
        #N = 250, L = 3, B = {G, L, DH, LG}, D=650
        # f = 1, c = 1, h = 1, s' = 0.75, no large gatherings
        "World": [
            ("TurnedOnInterventions", ["FaceMasks", "Quarantine", "ClosingBuildings", "LessSocial", "HybridClasses"]),
            ("ComplianceRatio", 1), # f = 1
            ("LargeGathering", False)
        ],
        "Quarantine": [
            ("ResultLatency", 3*24), # L = 3
            ("BatchSize", 250), # N=250
            ("ShowingUpForScreening", 1), # c = 1
        ],
        "ClosingBuildings": [
            ("ClosedBuildingOpenHub", ["dining"]), # ding stays open, but leaf Kv = 0
            ("ClosedBuilding_ByType", ["gym", "library"]),
            ("GoingHomeP", 1), # h = 1
            ("Exception_SemiClosedBuilding", ["dining", "faculty_dining_room"]), # replace these entrys 50/50
            ("Exception_GoingHomeP", 1),
        ],
        "LessSocializing":[
            ("StayingHome",0.75), # s'
        ],
        "HybridClass":[
            ("RemoteStudentCount", 250),
            ("RemoteFacultyCount", 150),
            ("RemovedDoubleCount", 325), # 525 - 250 = 275
            ("OffCampusCount", 250),
            ("TurnOffLargeGathering", True),
            ("ChangedSeedNumber", 7),
        ],
    },
    "VC_SP":{
        #N = 500, L = 2, B = {G, L, DH, LG, O}, D=1300
        # f = 1, c = 1, h = 1, s' = 0.75, no large gatherings
        "World": [
            ("TurnedOnInterventions", ["FaceMasks", "Quarantine", "ClosingBuildings", "LessSocial", "HybridClasses"]),
            ("ComplianceRatio", 1), # f = 1
            ("LargeGathering", False)
        ],
        "Quarantine": [
            ("ResultLatency", 2*24), # L = 2
            ("BatchSize", 500), # N=500
            ("ShowingUpForScreening", 1), # c = 1
        ],
        "ClosingBuildings": [
            ("ClosedBuildingOpenHub", ["dining"]),
            ("ClosedBuilding_ByType", ["gym", "library", "office"]),
            ("GoingHomeP", 1), # h = 1
            ("Exception_SemiClosedBuilding", ["dining", "faculty_dining_room"]),
            ("Exception_GoingHomeP", 1), # h = 1
        ],
        "LessSocializing":[
            ("StayingHome",0.75), # s' = 0.75
        ],
        "HybridClass":[
            ("RemoteStudentCount", 500),
            ("RemoteFacultyCount", 300),
            ("RemovedDoubleCount", 525), #525 = total number of double
            ("OffCampusCount", 500),
            ("TurnOffLargeGathering", True),
            ("ChangedSeedNumber", 5),
        ]
    },
}


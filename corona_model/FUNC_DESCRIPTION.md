This file lists the functionality and how to modify the code with ease.





1.) starting the model:

x = Agent_based_model()
x.load_data()
x.initilaize()
x.initilize_agents()
x.initilize_storing_parameters()

for _ in range(10):
    model.update_time()
    model.store_information()
    model.print_relevant_info()


2.) 
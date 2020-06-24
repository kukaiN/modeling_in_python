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





## Schedule creation

O = odd days, E = even days, W = weekends
what an empty schedule looks like:
[
    O: [0, 0, 0, 0, 0 ,0, 0, 0, 0, 0, 0 ,0, 0, 0, 0, 0, 0 ,0, 0, 0, 0, 0, 0 ,0]
    E: [0, 0, 0, 0, 0 ,0, 0, 0, 0, 0, 0 ,0, 0, 0, 0, 0, 0 ,0, 0, 0, 0, 0, 0 ,0]
    W: [0, 0, 0, 0, 0 ,0, 0, 0, 0, 0, 0 ,0, 0, 0, 0, 0, 0 ,0, 0, 0, 0, 0, 0 ,0]
]


| Classroom | Capacity | available days |
|-----------|----------|----------------|
| A | 5 | O, E |
| B | 5| O, E |
| C | 5|O, E |
| D | 5 |O |

From the information above, we make a new list
the new list will contain repeating room names (repeat for capacity #)

Odd days: [A, A, A, A, A, B, B, B, B, B, C, C, C, C, C, D, D, D, D, D]
Even days: [A, A, A, A, A, B, B, B, B, B, C, C, C, C, C]

Then each agent will have a boolean mask that looks like the one below
* the number of T and F is configurable *
    [   [T, F, T, F],
        [F, F, T, T]]

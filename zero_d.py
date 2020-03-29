import numpy as np
import pandas as pd

from tqdm import tqdm

def infect(df, trans_rate, day_name): # need to speed up
    """
    Simulates a single day of infection. Each infected person
    
    NOTE: a 0 counts as infected, while a 1 is healthy.
    
    Inputs:
        df : (pandas DataFrame) object holding all values of infected people. Each
                        column of "infected day _" corresponds to a different day, 
                        with "_" being some integer or float. The "name" column
                        assigns a name to each object, independent of index. In
                        the infected columns, a 0 counts as infected, while a 1 is 
                        healthy.
        trans_rate : (float) rate of transmission between individuals. infection
                        is performed in a probabilistic manner, casting it as a 
                        draw from a binomial distribution with a rate of 
                        1 - trans_rate.
        day_name : (float or int) the day of this infection, used to create a new
                        column in the dataframe tracking the day's infections.
                        
    Outputs:
        df : (pandas DataFrame) object, same as the input, but with a new column
                        holding this day's infected results.
    """
    p = 1 - trans_rate # to confer correct healthy/sick convention.
    for i in range(len(df)):
        if df[f'infected day {day_name - 1}'][i] == 0.0: # if infected, infect others
            infect_col = np.random.binomial(size=len(df), p=p, n=1) # 1 toss, siz
            
            # next, create a new column to track this day's number of infected individuals
            if i == 0:
                df[f"infected day {day_name}"] = df[f"infected day {day_name - 1}"] * infect_col
            else:
                df[f"infected day {day_name}"] = df[f"infected day {day_name}"] * infect_col
    return df

def simulate(N, trans_rate, t_steps, N_initial):
    """
    Simulates an infection run.
    
    Inputs:
        N : (int) number of individuals in the system.
        trans_rate : (float) rate of transmission between individuals. infection
                        is performed in a probabilistic manner, casting it as a 
                        draw from a binomial distribution with a rate of 
                        1 - trans_rate.
        t_steps : (int) number of time steps ("days") to consider.
        N_initial : (int) number of initially infected individuals.
        
    Outputs:
         df : (pandas DataFrame) object holding all values of infected people. Each
                        column of "infected day _" corresponds to a different day, 
                        with "_" being some integer or float. The "name" column
                        assigns a name to each object, independent of index. In
                        the infected columns, a 0 counts as infected, while a 1 is 
                        healthy. 
    """
    # making separate name column because indices get messy. 
    # other cols later.
    d = {'name': np.arange(N), 'infected day 0': np.ones(N)} 

    df = pd.DataFrame(data=d)
    
    df.loc[:N_initial, 'infected day 0'] = 0 # Make first N_initial people sick 
    t = 1
    for t in tqdm(range(1, t_steps), position=0, leave=True):
        df = infect(df, trans_rate, t)
    return df
        
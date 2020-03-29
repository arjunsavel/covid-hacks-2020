import numpy as np
import pandas as pd
from numba import jit

from math import sqrt
from tqdm import tqdm


@jit(nopython=True)
def find_first(searched, vec):
    """return the index of the first occurence of item in vec"""
    for i, item in enumerate(vec):
        if searched == item:
            return i
    return -1

def do_multiplier(x, y, power, thresh, df_sorted, df2D_test, farthest_calc):
    x = np.float64(x)
    y = np.float64(y)
    power = np.float64(power)
    thresh = np.float64(thresh)
    place_in_sorted = find_first(x, df_sorted.x.values)
    calc_indices = df_sorted.index[place_in_sorted 
                                   - np.int(farthest_calc):place_in_sorted 
                                   + np.int(farthest_calc)]
    df_calc_x = df2D_test.x[calc_indices]
    df_calc_y = df2D_test.y[calc_indices]
    dists = np.sqrt((df_calc_x.sub(x))**2 + (df_calc_y.sub(y))**2)
    multiplier_col = np.where(dists > thresh, np.power(dists, -power), np.ones_like(dists))
    del dists
    return multiplier_col, calc_indices

def distance(frame, ind1, ind2):
    """Just finding the distance between two rows and their x-y pairs."""
    x1, y1 = frame['x'].values[ind1], frame['y'].values[ind1]
    x2, y2 = frame['x'].values[ind2], frame['y'].values[ind2]
    return sqrt((x1-x2)**2 + (y1-y2)**2)

def infect2D(df, trans_rate, day_name, thresh, power, df_sorted, farthest_calc):
    """
    Simulates a single day of infection in 1D. 
    
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
        dist_matrix : (numpy.ndarray) distance matrix holding the distances between all individuals.
                        
    Outputs:
        df : (pandas DataFrame) object, same as the input, but with a new column
                        holding this day's infected results.
    """
    df[f"infected day {day_name}"] = df[f"infected day {day_name - 1}"].copy()
    infected = df[df[f'infected day {day_name}'] == 0.]
    
    if len(infected) == len(df): # everyone is infected
        return df
    for index, row in infected.iterrows(): # this is number of rows, right?  
        # find distance multiplier between this ind and all others
        x, y = row['x'], row['y']
        multiplier_col, calc_indices = do_multiplier(x, y, power, thresh, df_sorted, df, farthest_calc)
        p = 1 - (multiplier_col * trans_rate)
        infect_col = np.random.binomial(size=len(calc_indices), p=p, n=1) # 1 toss
#         df.loc[calc_indices, f'infected day {day_name}'] *= infect_col
        df.loc[calc_indices[infect_col == 0], f'infected day {day_name}'] = 0
    return df
def simulate2D(N, trans_rate, t_steps, N_initial, thresh, power, 
               distrib_pop, distrib_infec, kwargs_for_pop={}, 
               kwargs_for_infec={}):
    """
    Simulates an infection run in 1D.
    
    Inputs:
        N : (int) number of individuals in the system.
        trans_rate : (float) rate of transmission between individuals. infection
                        is performed in a probabilistic manner, casting it as a 
                        draw from a binomial distribution with a rate of 
                        1 - trans_rate.
        t_steps : (int) number of time steps ("days") to consider.
        N_initial : (int) number of initially infected individuals.
        thresh : (float) distance less than which infection is transmitted at the trans_rate;
                            that is, less than which this function returns a value of 1. At
                            a distance greater than this, this function returns 1/distance^power.
        power : (float) Greater than 0. Power to which the multiplier falls off if the distance
                            is greater than some threshold.
        distrib_pop : (func) distribution function to determine how individuals are initialized.
        distrib_infec : (func) distribution function to determine how initial infections are initialized.
        kwargs_for_pop : (dict) keyword arguments passed to the distrib_pop distribution type. 
                        Size not included.
        kwargs_for_infec : (dict) keyword arguments passed to the distrib_infect distribution type. Size not 
                        included.
        
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
    name = np.arange(N)
    zero_infected = np.ones(N)
    pop = initialize_pop_2D(N, distrib_pop, **kwargs_for_pop)
    x, y = pop[:, 0], pop[:, 1]
    d = {'name': np.arange(N), 'infected day 0': zero_infected, 'x' : x, 'y' : y} 

    df = pd.DataFrame(data=d)
    
    
    pop = initialize_pop_2D(N_initial, distrib_infec, **kwargs_for_infec)
    x, y = pop[:, 0], pop[:, 1]
    all_infected = np.zeros(N_initial)
    d_infec = {'name': np.arange(N, N + N_initial), 'infected day 0': all_infected, 'x' : x, 'y' : y}
    df_infec = pd.DataFrame(data=d_infec)
    
    df = df.append(df_infec, ignore_index = True)
    
    test_vals = np.round(np.linspace(1, 1000, 100))
    df['Rank'] = df.x.rank() + df.y.rank()
    df_sorted = df.sort_values('Rank', ascending=False).drop('Rank',axis=1)
    dists = np.array([distance(df_sorted, 100, int(val)) for val in test_vals])
    farthest_calc = int(test_vals[np.argmin(np.abs(dists - thresh))])
    # the above determines the farthest index to calculate distance from a given point.
    
    for t in tqdm(range(1, t_steps), position=0, leave=True):
        df = infect2D(df, trans_rate, t, thresh, power, df_sorted, farthest_calc)
    return df
        
def initialize_pop_2D(N, distrib, **kwargs):
    '''
    This will change once we have the U.S. map.
    
    distrib: size is not a thing again.
    '''
    pop = distrib(size=(N, 2), **kwargs)
    
    return pop
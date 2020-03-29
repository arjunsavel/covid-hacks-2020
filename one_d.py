import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.path as path
import matplotlib.patches as patches
import matplotlib.animation as animation

from tqdm import tqdm

def infect1D(df, trans_rate, day_name, thresh, power): # need to speed up
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
                        
    Outputs:
        df : (pandas DataFrame) object, same as the input, but with a new column
                        holding this day's infected results.
    """
    df[f"infected day {day_name}"] = df[f"infected day {day_name - 1}"].copy()
    infected = df[df[f'infected day {day_name}'] == 0.]
    if len(infected) == len(df): # everyone is infected
        return df
    for i in range(len(infected)): # this is number of rows, right?            
        # find distance multiplier between this ind and all others
        uninfected = df[df[f'infected day {day_name}'] == 1.]
        r2 = infected['locs'].values[i] # time this versus

        subs = uninfected['locs'].apply(lambda x:abs(x - r2))
        multiplier_col = subs.apply(lambda x:1/pow(x, power) if x > thresh else 1)

        # now get different p values

        p = 1 - (multiplier_col * trans_rate)

        infect_col = np.random.binomial(size=len(uninfected), p=p, n=1) # 1 toss

        # next, create a new column to track this day's number of infected individuals
        
        df.loc[df[f'infected day {day_name}'] == 1., f'infected day {day_name}'] *= infect_col

#         uninfected[f"infected day {day_name}"] = uninfected[f"infected day {day_name}"] * infect_col
    return df

def simulate1D(N, trans_rate, t_steps, N_initial, thresh, power, 
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
    
    def initial_infect(df, distrib_infec, N_initial, kwargs):
        """
        Based on the specified distribution functions, this initializes the infected
        population.
        
        Inputs:
             df : (pandas DataFrame) object holding all values of infected people. Each
                        column of "infected day _" corresponds to a different day, 
                        with "_" being some integer or float. The "name" column
                        assigns a name to each object, independent of index. In
                        the infected columns, a 0 counts as infected, while a 1 is 
                        healthy. 
            distrib_infec : (func) distribution function to determine how initial infections are initialized.
            **kwargs : (dict) keyword arguments passed to the distrib_infect distribution type. Size not 
                        included.
                        
        Outputs:
            df : (pandas DataFrame) object holding all values of infected people. Each
                        column of "infected day _" corresponds to a different day, 
                        with "_" being some integer or float. The "name" column
                        assigns a name to each object, independent of index. In
                        the infected columns, a 0 counts as infected, while a 1 is 
                        healthy. This time, initialized with the initially infected individuals.
        """
        infected = distrib_infec(size=N_initial, **kwargs)
        for inf in infected:
            uninfected = df[df['infected day 0'] == 1] # want to find a person that isn't infected
            closest_in_frame = uninfected['locs'].sub(inf).abs().idxmin() 
            df.loc[closest_in_frame, 'infected day 0'] = 0 # make that closest individual infected
        return df
    
    
    name = np.arange(N)
    zero_infected = np.ones(N)
    locs = distrib_pop(size=N, **kwargs_for_pop)
    d = {'name': np.arange(N), 'infected day 0': zero_infected, 'locs' : locs} 

    df = pd.DataFrame(data=d)
    
    df = initial_infect(df, distrib_infec, N_initial, kwargs_for_infec) # now infected
    for t in tqdm(range(1, t_steps), position=0, leave=True):
        df = infect1D(df, trans_rate, t, thresh, power)
    return df

def animate_histogram(df, title):
    """
    animates a histogram.
    
    adapted from https://matplotlib.org/gallery/animation/animated_histogram.html
    """

    n, bins = np.histogram(df['locs'][df['infected day 29'] == 0], 30)
    infect_cols = [col for col in df.columns if 'infected day' in col]

    # get the corners of the rectangles for the histogram
    left = np.array(bins[:-1])
    right = np.array(bins[1:])
    bottom = np.zeros(len(left))
    top = bottom + n
    nrects = len(left)


    nverts = nrects * (1 + 3 + 1)
    verts = np.zeros((nverts, 2))
    codes = np.ones(nverts, int) * path.Path.LINETO
    codes[0::5] = path.Path.MOVETO
    codes[4::5] = path.Path.CLOSEPOLY
    verts[0::5, 0] = left
    verts[0::5, 1] = bottom
    verts[1::5, 0] = left
    verts[1::5, 1] = top
    verts[2::5, 0] = right
    verts[2::5, 1] = top
    verts[3::5, 0] = right
    verts[3::5, 1] = bottom

    patch = None


    def animate(i):
        # simulate new data coming in
        col = infect_cols[i]
        n, bins2 = np.histogram(df['locs'][df[col] == 0], bins=bins)
        top = n
        verts[1::5, 1] = top
        verts[2::5, 1] = top
        lab = f'{col[-2:]} days after patient 0'
        label.set_text(lab)

        return [patch, ]


    fig, ax = plt.subplots(figsize=(8,8))
    # ax.set_ylim(0, 2)
    ax.set_xlim(-20, 20)
#     ax.set_ylim(0, 10000)
    ax.set_title(title, fontsize=20)
    lab = f'{infect_cols[0][-2:]} days after patient 0'
    label = ax.text(-9, 0.9 * np.max(n), lab, fontsize=18)
    ax.set_ylabel('Number of infected individuals', fontsize=20)
    ax.set_xlabel(r'Location', fontsize=20)
    barpath = path.Path(verts, codes)
    patch = patches.PathPatch(
        barpath, facecolor='maroon', edgecolor='gray', alpha=0.5)
    ax.add_patch(patch)

    # ax.set_xlim(left[0], right[-1])
    ax.set_ylim(bottom.min(), top.max())

    return animation.FuncAnimation(fig, animate, len(infect_cols), repeat=False, blit=True)
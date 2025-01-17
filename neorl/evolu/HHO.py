# -*- coding: utf-8 -*-
"""
@author:
% _____________________________________________________
% Main paper:
% Harris hawks optimization: Algorithm and applications
% Ali Asghar Heidari, Seyedali Mirjalili, Hossam Faris, Ibrahim Aljarah, Majdi Mafarja, Huiling Chen
% Future Generation Computer Systems,
% DOI: https://doi.org/10.1016/j.future.2019.02.028
"""
import random
import numpy
import math
import time

#This class is for data collection, not important
class solution:
    def __init__(self):
        self.best = 0
        self.bestIndividual = []
        self.convergence = []
        self.optimizer = ""
        self.objfname = ""
        self.startTime = 0
        self.endTime = 0
        self.executionTime = 0
        self.lb = 0
        self.ub = 0
        self.dim = 0
        self.popnum = 0
        self.maxiers = 0

#Main alg function!!!
def HHO(objf, lb, ub, dim, SearchAgents_no, Max_iter):

    # dim=30
    # SearchAgents_no=50
    # lb=-100
    # ub=100
    # Max_iter=500

    # initialize the location and Energy of the rabbit
    Rabbit_Location = numpy.zeros(dim) # Rabbit always starts at (0, 0)?
    Rabbit_Energy = float("inf")  # change this to -inf for maximization problems

    if not isinstance(lb, list):
        lb = [lb for _ in range(dim)]
        ub = [ub for _ in range(dim)]
    lb = numpy.asarray(lb)
    ub = numpy.asarray(ub)

    # Initialize the locations of Harris' hawks
    X = numpy.asarray(
        [x * (ub - lb) + lb for x in numpy.random.uniform(0, 1, (SearchAgents_no, dim))]
    ) # x --> array of random numbers between 0 and 1 with shape 1 x dim

    # Initialize convergence
    convergence_curve = numpy.zeros(Max_iter)

    ############################
    s = solution()

    print('HHO is now tackling  "' + objf.__name__ + '"')

    timerStart = time.time()
    s.startTime = time.strftime("%Y-%m-%d-%H-%M-%S")
    ############################

    t = 0  # Loop counter

    # Main loop
    while t < Max_iter:
        # Go through each hawk and update rabbit location based on "best" (most minimized) hawk location
        for i in range(0, SearchAgents_no):

            # Check boundaries

            X[i, :] = numpy.clip(X[i, :], lb, ub) # X[i, :] --> this hawk's location in all dimensions
            # not sure why numpy.clip is needed here since all dimension locations should be in bound

            # fitness of locations
            fitness = objf(X[i, :])

            # Update the location of Rabbit
            if fitness < Rabbit_Energy:  # Change this to > for maximization problem
                Rabbit_Energy = fitness
                Rabbit_Location = X[i, :].copy()

        E1 = 2 * (1 - (t / Max_iter))  # factor to show the decreasing energy of rabbit

        # Update the location of Harris' hawks
        for i in range(0, SearchAgents_no):

            E0 = 2 * random.random() - 1  # -1<E0<1 why so complicated?
            Escaping_Energy = E1 * E0  # escaping energy of rabbit Eq. (3) in the paper

            # -------- Exploration phase Eq. (1) in paper -------------------

            if abs(Escaping_Energy) >= 1:
                # Harris' hawks perch randomly based on 2 strategy:
                q = random.random()
                rand_Hawk_index = math.floor(SearchAgents_no * random.random())
                X_rand = X[rand_Hawk_index, :] # location of random hawk
                if q < 0.5:
                    # perch based on other family members
                    X[i, :] = X_rand - random.random() * abs(
                        X_rand - 2 * random.random() * X[i, :]
                    )

                elif q >= 0.5:
                    # perch on a random tall tree (random site inside group's home range)
                    X[i, :] = (Rabbit_Location - X.mean(0)) - random.random() * (
                        (ub - lb) * random.random() + lb
                    )

            # -------- Exploitation phase -------------------
            elif abs(Escaping_Energy) < 1:
                # Attacking the rabbit using 4 strategies regarding the behavior of the rabbit

                # phase 1: ----- surprise pounce (seven kills) ----------
                # surprise pounce (seven kills): multiple, short rapid dives by different hawks

                r = random.random()  # probablity of each event

                if (
                    r >= 0.5 and abs(Escaping_Energy) < 0.5
                ):  # Hard besiege Eq. (6) in paper
                    X[i, :] = (Rabbit_Location) - Escaping_Energy * abs(
                        Rabbit_Location - X[i, :]
                    )

                if (
                    r >= 0.5 and abs(Escaping_Energy) >= 0.5
                ):  # Soft besiege Eq. (4) in paper
                    Jump_strength = 2 * (
                        1 - random.random() # 1 < J < 2
                    )  # random jump strength of the rabbit
                    X[i, :] = (Rabbit_Location - X[i, :]) - Escaping_Energy * abs(
                        Jump_strength * Rabbit_Location - X[i, :]
                    )

                # phase 2: --------performing team rapid dives (leapfrog movements)----------

                if (
                    r < 0.5 and abs(Escaping_Energy) >= 0.5
                ):  # Soft besiege Eq. (10) in paper
                    # rabbit try to escape by many zigzag deceptive motions
                    Jump_strength = 2 * (1 - random.random())
                    X1 = Rabbit_Location - Escaping_Energy * abs(
                        Jump_strength * Rabbit_Location - X[i, :]
                    )
                    X1 = numpy.clip(X1, lb, ub)

                    if objf(X1) < fitness:  # improved move?
                        X[i, :] = X1.copy()
                    else:  # hawks perform levy-based short rapid dives around the rabbit
                        X2 = (
                            Rabbit_Location
                            - Escaping_Energy
                            * abs(Jump_strength * Rabbit_Location - X[i, :])
                            + numpy.multiply(numpy.random.randn(dim), Levy(dim))
                        )
                        X2 = numpy.clip(X2, lb, ub)
                        if objf(X2) < fitness:
                            X[i, :] = X2.copy()
                if (
                    r < 0.5 and abs(Escaping_Energy) < 0.5
                ):  # Hard besiege Eq. (11) in paper
                    Jump_strength = 2 * (1 - random.random())
                    X1 = Rabbit_Location - Escaping_Energy * abs(
                        Jump_strength * Rabbit_Location - X.mean(0)
                    )
                    X1 = numpy.clip(X1, lb, ub)

                    if objf(X1) < fitness:  # improved move?
                        X[i, :] = X1.copy()
                    else:  # Perform levy-based short rapid dives around the rabbit
                        X2 = (
                            Rabbit_Location
                            - Escaping_Energy
                            * abs(Jump_strength * Rabbit_Location - X.mean(0))
                            + numpy.multiply(numpy.random.randn(dim), Levy(dim))
                        )
                        X2 = numpy.clip(X2, lb, ub)
                        if objf(X2) < fitness:
                            X[i, :] = X2.copy()

        convergence_curve[t] = Rabbit_Energy
        if t % 1 == 0: # change depending on how often message should be displayed
            print(
                [
                    "At iteration "
                    + str(t)
                    + " the best fitness is "
                    + str(Rabbit_Energy)
                ]
            )
        t = t + 1

    timerEnd = time.time()
    s.endTime = time.strftime("%Y-%m-%d-%H-%M-%S")
    s.executionTime = timerEnd - timerStart
    s.convergence = convergence_curve
    s.optimizer = "HHO"
    s.objfname = objf.__name__
    s.best = Rabbit_Energy
    s.bestIndividual = Rabbit_Location

    return s

#auxiliary function used by HHO to make dives
def Levy(dim):
    beta = 1.5
    sigma = (
        math.gamma(1 + beta)
        * math.sin(math.pi * beta / 2)
        / (math.gamma((1 + beta) / 2) * beta * 2 ** ((beta - 1) / 2))
    ) ** (1 / beta)
    u = 0.01 * numpy.random.randn(dim) * sigma
    v = numpy.random.randn(dim)
    zz = numpy.power(numpy.absolute(v), (1 / beta))
    step = numpy.divide(u, zz)
    return step

#-----------------------------------------------------------
#main HHO application
#-----------------------------------------------------------
if __name__ == '__main__':

    #Fitness function for testing
    def Sphere(individual):
        """Sphere test objective function.
                F(x) = sum_{i=1}^d xi^2
                d=1,2,3,...
                Range: [-100,100]
                Minima: 0
        """
        y=sum(x**2 for x in individual)
        return y

    nx=10
    lb=[-100]*nx
    ub=[100]*nx
    nhawks=20
    results=HHO(objf=Sphere, lb=lb, ub=ub, dim=nx, SearchAgents_no=nhawks, Max_iter=100)

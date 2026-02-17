import matplotlib.pyplot as plt
from random import shuffle, choice, random
from copy import copy
from itertools import permutations
from math import factorial



def generate_preferences(n):
    """ 
    Returns a random preference profile P for <n> agents
    """
    A = [i for i in range(n)]
    P = []
    for i in range(n):
        shuffle(A)
        new = copy(A)
        new.remove(i)
        P.append( tuple(new) )
    return tuple(P)


def prefprof1euc(n):
    """ 
    generate 1-euclidean preferences 
    """ 
    pos = [random() for _ in range(n)]
    p = []
    for i in range(n):
        d = [(abs(pos[i]- val),j) for j,val in enumerate(pos)]
        d.sort()
        p.append( tuple([j for dist,j in d if j!= i]) )
    return tuple(p)


def random_matching(n):
    """ 
    Returns a random matching for <n> agents
    """
    A = list(range(n))
    assert n%2==0
    matching = [-1 for i in A]
    tbm = copy(A)
    for i in range(n):
        if matching[i] != -1: continue
        tbm.remove(i)
        partner = choice(tbm)
        matching[i] = partner 
        matching[partner] = i
        tbm.remove(partner)
    return matching


def rank(P, i, j):
    """ 
    Rank of agent j for agent i in preference list P (starting at 1)
    """
    if i == j:
        raise ValueError("i must be different than j")
    
    
    if j not in P[i]:
        print("pi",P[i])
        print("i",i,"j",j)
    # return P[i].index(int(j)) + 1
    return P[i].index(j) + 1
            
    
def rk_ef(M,P,k=float("inf"),verbose = False):
    """ 
    Returns True if matching <M> is r<k>-EF wrt to preference profile <P> else returns False. 
    If k is infinite, it represents r-EF
    """
    o = M 
    for i in M:
        for j in M:
            if i == j: continue 
            if i==o[j]: continue
            rioi = rank(P,i,o[i])
            rioj = rank(P,i,o[j])
            rjoj = rank(P,j,o[j])
            
            if not ( rioi < rioj or rjoj <= min( rioj , k ) ): 
                if verbose:
                    print("i j",i,j,"##",i,":",o[i],'r',rioi,"##",j,":",o[j],"r",rioj)
                return False 
    return True
    

def check_matching(m):
    """ 
    With <m> a list representing a matching such that: agent i is matched to agent m[i],
    check that the matching satisfies:
        - no agent is matched to itself 
        - each agent i is matched to agent m[i]
    """
    return all( [ m[m[i]] == i and m[i] != i  for i in range(len(m)) ] )


def get_all_matchings(n):
    """ 
    Returns all possible matchings of <n> agents. 
    Checks that every matching is correct wrt the roommate matching problem
    """
    return set(filter(check_matching, permutations(range(n))))


def get_all_profiles(N):
    """ 
    Returns all possible preference profiles for <N> agents
    """
    agents = [i for i in range(N)]
    all_profiles = set()
    all_p_agent = []
    for i in range(len(agents)):
        agents_i = copy(agents)
        agents_i.remove(i)
        all_p_i = list( permutations(agents_i) )
        all_p_agent.append(all_p_i)
        
    first = []
    for i in range(N):
        first.append(all_p_agent[i][0])
    all_profiles.add(tuple(first))
    
    Np = len(all_p_agent[0]) - 1
    current = [0 for i in range(N)]
    end = [Np for i in range(N)]
    while True:
        if current == end: break
        if current[-1] < Np:
            current[-1] += 1 
        else:
            current[-1] = 0
            current[-2] += 1
            for j in range(N-2,0,-1):
                if current[j] < Np+1: break
                current[j] = 0
                current[j-1] += 1
        
        current_profile = []
        for i, pind in enumerate(current):
            current_profile.append( all_p_agent[i][pind] )
        all_profiles.add( tuple(current_profile) )
    return all_profiles


def nb_pref_profiles(n):
    """
    Returns the number of all possible preference profiles for <n> agents. 
       a = each agent can have (n-1) ! possible preferences
       There are a**n combinations of an agent having each preference profile 
    """
    a = factorial(n-1) 
    return a ** n


def nb_matchings(n):
    """ 
    nb of possible matchings of <n> agents
    """ 
    a = factorial(n)
    b = factorial(n//2) * 2 **(n//2)
    return a / b


def get_rkef_matchings(n):
    """ 
    Given a number <n> of agents, find all the most rk-EF matchings. Returns
        - matchings , allm, allp ; where
            - for all pref profiles P, matchings[P] = (k,m) where 
                - P is a preference profile
                - k is the smallest k value of rk-EF found for this preference profile (-1 if none)
                - m is the corresponding matching for k (-1 if none)
            - allm is the set of all possible matchings of <n> agents
    """ 
    if n % 2 != 0:
        raise ValueError("n must be even")
    if n > 4:
        raise ValueError("Trop lourd en calcul")

    allp = get_all_profiles(n)
    allm = get_all_matchings(n)
    matchings = {}
    for P in allp:
        best = (-1,-1)
        for m in allm:
            if best == (-1,-1) and rk_ef(m, P):
                best = (float("inf"),m)
                
        for m in allm:
            for k in range(n):
                if rk_ef(m, P,k=k) and (k < best[0] or best[0] == -1):
                    best = (k, m)
                    break

        matchings[str(P)] = best 
    return matchings,allm         
    


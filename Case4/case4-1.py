import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from scipy.stats import norm
from sklearn import linear_model
from sklearn.preprocessing import normalize
from Data_generation import Data_generation


def inverse_logit(Z):
    return np.exp(Z) / (np.exp(Z)+1)

def intfy(W):
    return np.array(list(map(int,W)))

def logistic_training(X,Y):
    clf = linear_model.LogisticRegression()
    clf.fit(X,Y)
    return clf

def linear_training(X,Y):
    clf = linear_model.LinearRegression()
    clf.fit(X, Y)
    return clf

# def normalize(X):


print("----------------------START------------------------------")

''' Data generation '''
np.random.seed(123)

fig_version = 2

dim = 50
# Ns = 10*dim
Ns = 50
N = 100*dim

case_num = 41
Obs, Intv, Intv_S =  Data_generation(case_num=case_num ,N=N,Ns=Ns,dim = dim,seed_num=1234)
Z = Obs[ list(range(dim)) ]

# z_care = list( np.random.multivariate_normal( np.mean(Z,axis=0), np.diag( np.std(Z,axis=0) ), 1 )[0] )
# z_care = list(np.mean(Z,axis=0) - 0.5* np.std(Z,axis=0))
z_care = list(Obs[list(range(dim))].loc[100])

if fig_version == 1:
    x_care = 0
    care = [x_care] + z_care

    # Compute mu and std of P(Y|x,z)
    ## Training for P(Y|x,z) for all x and z
    obs_lin = linear_training(Obs[ ['X']+list(range(dim)) ],Obs['Y'])
    ### Compute the residual distribution for std
    obs_result = obs_lin.predict(Obs[ ['X']+list(range(dim)) ])
    obs_resid = obs_result - Obs['Y']
    ## Compute mu and std of P(Y|x,z)
    mu_yxz = obs_lin.predict(care)[0]
    std_yxz = np.std(obs_resid)

    # Compute mu and std of Ds(Y|do(x),z)
    ## Training for D(Y|do(x),z) for all x and z
    Sdox_lin = linear_training(Intv_S[ ['X']+list(range(dim)) ], Intv_S['Y'])
    ### Compute the residual distribution for std
    Sdox_resid = Sdox_lin.predict(Intv_S[ ['X']+list(range(dim)) ]) - Intv_S['Y']
    ## Compute mu and std of Ds(Y|do(x),z)
    mu_sydox = Sdox_lin.predict(care)[0]
    std_sydox = np.std(Sdox_resid)

    # Compute mu and std of P(Y|do(x),z)
    ## Training for P(Y|do(x),z) for all x and z
    dox_lin = linear_training(Intv[ ['X']+list(range(dim)) ], Intv['Y'])
    ### Compute the residual distribution for std
    dox_resid = dox_lin.predict(Intv[ ['X']+list(range(dim)) ]) - Intv['Y']
    ## Compute mu and std of P(Y|do(x),z)
    mu_ydox = dox_lin.predict(care)[0]
    std_ydox = np.std(dox_resid)
    # std_sydox = std_ydox

    # Compute P(X=x_care | z)
    ## Training P(X|Z) for all z and x
    pxz_logit = logistic_training(Obs[ list(range(dim)) ], Obs['X'])
    ## Compute P(X|z)
    pxz_compute = pxz_logit.predict_proba(z_care)[0]
    ## Pick P(x_care | z)
    pxz = pxz_compute[x_care]

    # Compute constant term C = Hx + 1/2 - log(std_yxz / std_ydoxz) - (std_yxz)^2/(2 * (std_ydoxz)^2)
    Hxz = -np.log(pxz)
    C = Hxz + 0.5 - np.log(std_sydox / std_yxz) - (std_yxz ** 2) / (2 * std_sydox ** 2)

    # Compute LB and UB
    LB = mu_yxz - std_sydox * np.sqrt(2 * C)
    UB = mu_yxz + std_sydox * np.sqrt(2 * C)

    print("----------- Analysis --------")
    print("P(x): ", pxz)
    print("min(P(Y|x)): ", min(norm.pdf(obs_result, loc=mu_yxz, scale=std_yxz)))
    print("avg(P(Y|x)): ", np.mean(norm.pdf(obs_result, loc=mu_yxz, scale=std_yxz)))
    print("min(P(Y,x)): ", pxz * min(norm.pdf(obs_result, loc=mu_yxz, scale=std_yxz)))
    print("avg(P(Y,x)): ", pxz * np.mean(norm.pdf(obs_result, loc=mu_yxz, scale=std_yxz)))

    print("X=", x_care, ", Interval:", LB, mu_ydox, UB)

    # Graphical illustration
    domain = np.linspace(mu_yxz - 10 * std_yxz, mu_yxz + 10 * std_yxz, num=10000)
    output = ((mu_yxz - domain) ** 2) / (2 * (std_sydox ** 2))
    plt.figure(1)
    plt.plot(domain, output)
    plt.plot(domain, [C] * len(domain))
    plt.axvline(mu_ydox)


elif fig_version == 2:
    ''' When X = 0 '''
    x_care = 0
    care = [x_care] + z_care

    # Compute mu and std of P(Y|x,z)
    ## Training for P(Y|x,z) for all x and z
    obs_lin = linear_training(Obs[['X'] + list(range(dim))], Obs['Y'])
    ### Compute the residual distribution for std
    obs_result = obs_lin.predict(Obs[['X'] + list(range(dim))])
    obs_resid = obs_result - Obs['Y']
    ## Compute mu and std of P(Y|x,z)
    mu_yxz0 = obs_lin.predict(care)[0]
    std_yxz = np.std(obs_resid)

    # Compute mu and std of Ds(Y|do(x),z)
    ## Training for D(Y|do(x),z) for all x and z
    Sdox_lin = linear_training(Intv_S[['X'] + list(range(dim))], Intv_S['Y'])
    ### Compute the residual distribution for std
    Sdox_resid = Sdox_lin.predict(Intv_S[['X'] + list(range(dim))]) - Intv_S['Y']
    ## Compute mu and std of Ds(Y|do(x),z)
    mu_sydox0 = Sdox_lin.predict(care)[0]
    std_sydox = np.std(Sdox_resid)

    # Compute mu and std of P(Y|do(x),z)
    ## Training for P(Y|do(x),z) for all x and z
    dox_lin = linear_training(Intv[['X'] + list(range(dim))], Intv['Y'])
    ### Compute the residual distribution for std
    dox_resid = dox_lin.predict(Intv[['X'] + list(range(dim))]) - Intv['Y']
    ## Compute mu and std of P(Y|do(x),z)
    mu_ydox0 = dox_lin.predict(care)[0]
    std_ydox = np.std(dox_resid)
    # std_sydox = std_ydox

    # Compute P(X=x_care | z)
    ## Training P(X|Z) for all z and x
    pxz_logit = logistic_training(Obs[list(range(dim))], Obs['X'])
    ## Compute P(X|z)
    pxz_compute = pxz_logit.predict_proba(z_care)[0]
    ## Pick P(x_care | z)
    pxz0 = pxz_compute[x_care]

    # Compute constant term C = Hx + 1/2 - log(std_yxz / std_ydoxz) - (std_yxz)^2/(2 * (std_ydoxz)^2)
    Hxz0 = -np.log(pxz0)
    C0 = Hxz0 + 0.5 - np.log(std_ydox / std_yxz) - (std_yxz ** 2) / (2 * std_ydox ** 2)

    # Compute LB and UB
    LB0 = mu_yxz0 - std_ydox * np.sqrt(2 * C0)
    UB0 = mu_yxz0 + std_ydox * np.sqrt(2 * C0)

    print("----------- Analysis --------")
    print("P(x): ", pxz0)
    print("min(P(Y|x)): ", min(norm.pdf(obs_result, loc=mu_yxz0, scale=std_yxz)))
    print("avg(P(Y|x)): ", np.mean(norm.pdf(obs_result, loc=mu_yxz0, scale=std_yxz)))
    print("min(P(Y,x)): ", pxz0 * min(norm.pdf(obs_result, loc=mu_yxz0, scale=std_yxz)))
    print("avg(P(Y,x)): ", pxz0 * np.mean(norm.pdf(obs_result, loc=mu_yxz0, scale=std_yxz)))
    print("X=", x_care, ", Interval:", LB0, mu_ydox0, UB0)











    ''' When X = 1 '''
    x_care = 1
    care = [x_care] + z_care

    # Compute mu and std of P(Y|x,z)
    ## Training for P(Y|x,z) for all x and z
    obs_lin = linear_training(Obs[['X'] + list(range(dim))], Obs['Y'])
    ### Compute the residual distribution for std
    obs_result = obs_lin.predict(Obs[['X'] + list(range(dim))])
    obs_resid = obs_result - Obs['Y']
    ## Compute mu and std of P(Y|x,z)
    mu_yxz1 = obs_lin.predict(care)[0]
    std_yxz = np.std(obs_resid)

    # Compute mu and std of Ds(Y|do(x),z)
    ## Training for D(Y|do(x),z) for all x and z
    Sdox_lin = linear_training(Intv_S[['X'] + list(range(dim))], Intv_S['Y'])
    ### Compute the residual distribution for std
    Sdox_resid = Sdox_lin.predict(Intv_S[['X'] + list(range(dim))]) - Intv_S['Y']
    ## Compute mu and std of Ds(Y|do(x),z)
    mu_sydox1 = Sdox_lin.predict(care)[0]
    std_sydox = np.std(Sdox_resid)

    # Compute mu and std of P(Y|do(x),z)
    ## Training for P(Y|do(x),z) for all x and z
    dox_lin = linear_training(Intv[['X'] + list(range(dim))], Intv['Y'])
    ### Compute the residual distribution for std
    dox_resid = dox_lin.predict(Intv[['X'] + list(range(dim))]) - Intv['Y']
    ## Compute mu and std of P(Y|do(x),z)
    mu_ydox1 = dox_lin.predict(care)[0]
    std_ydox = np.std(dox_resid)
    # std_sydox = std_ydox

    # Compute P(X=x_care | z)
    ## Training P(X|Z) for all z and x
    pxz_logit = logistic_training(Obs[list(range(dim))], Obs['X'])
    ## Compute P(X|z)
    pxz_compute = pxz_logit.predict_proba(z_care)[0]
    ## Pick P(x_care | z)
    pxz1 = pxz_compute[x_care]

    # Compute constant term C = Hx + 1/2 - log(std_yxz / std_ydoxz) - (std_yxz)^2/(2 * (std_ydoxz)^2)
    Hxz1 = -np.log(pxz1)
    C1 = Hxz1 + 0.5 - np.log(std_ydox / std_yxz) - (std_yxz ** 2) / (2 * std_ydox ** 2)

    # Compute LB and UB
    LB1 = mu_yxz1 - std_ydox * np.sqrt(2 * C1)
    UB1 = mu_yxz1 + std_ydox * np.sqrt(2 * C1)

    print("----------- Analysis --------")
    print("P(x): ", pxz1)
    print("min(P(Y|x)): ", min(norm.pdf(obs_result, loc=mu_yxz1, scale=std_yxz)))
    print("avg(P(Y|x)): ", np.mean(norm.pdf(obs_result, loc=mu_yxz1, scale=std_yxz)))
    print("min(P(Y,x)): ", pxz1 * min(norm.pdf(obs_result, loc=mu_yxz1, scale=std_yxz)))
    print("avg(P(Y,x)): ", pxz1 * np.mean(norm.pdf(obs_result, loc=mu_yxz1, scale=std_yxz)))
    print("X=", x_care, ", Interval:", LB1, mu_ydox1, UB1)

    # Graphical illustration
    f, ax = plt.subplots(2, sharex='all')
    min_val = min(LB0, LB1, min(Obs['Y']))
    max_val = max(UB0, UB1, max(Obs['Y']))

    x_domain = np.linspace(min_val, max_val, 10000)
    y_graphic = 0.5
    y_domain = np.array([y_graphic] * len(x_domain))

    title_size = 40
    label_size = 30
    legend_size = 20
    marker_size = 15

    ax[0].set_title('Interval of P(y|do(X= 0), Z=z)',fontsize=title_size)
    ax[0].plot(x_domain, y_domain)
    ax[0].axvline(x=min_val, ymin=0.48, ymax=0.52)
    ax[0].axvline(x=max_val, ymin=0.48, ymax=0.52)
    ax[0].axvline(x=LB0, ymin=0.35, ymax=0.65,label="Lower bound")
    ax[0].axvline(x=UB0, ymin=0.35, ymax=0.65,label="Upper bound")
    ax[0].plot(mu_ydox0, y_graphic, marker='o', color='r',label="P(y|do(X=0),z)",markersize=marker_size )
    ax[0].set_xlabel('Mean of causal quantity', fontsize=label_size)  # X label
    ax[0].yaxis.set_visible(False)  # Hide only x axis
    ax[0].xaxis.set_visible(False)  # Hide only x axis
    ax[0].legend(fontsize=legend_size,loc='upper right')

    ax[1].plot(x_domain, y_domain)
    ax[1].set_title('Interval of P(y|do(X= 1), Z=z)',fontsize=title_size)
    ax[1].axvline(x=min_val, ymin=0.48, ymax=0.52)
    ax[1].axvline(x=max_val, ymin=0.48, ymax=0.52)
    ax[1].axvline(x=LB1, ymin=0.35, ymax=0.65,label="Lower bound")
    ax[1].axvline(x=UB1, ymin=0.35, ymax=0.65,label="Upper bound")
    ax[1].plot(mu_ydox1, y_graphic, marker='o', color='r',label="P(y|do(X=1),z)",markersize=marker_size )
    ax[1].set_xlabel('Mean of causal quantity', fontsize=label_size)  # X label
    ax[1].yaxis.set_visible(False)  # Hide only x axis
    ax[1].legend(fontsize=legend_size,loc='upper right')

import numpy as np
import matplotlib.pyplot as plt
import math
import os

msun=1.9892e33
cgrav=6.67428e-8
rsun=6.9598e10
secday=24.0*60.0*60.0

pfit=[-8.65828957e-08,  3.25183895e-05, -5.31786630e-03,  4.94552158e-01,\
 -2.86053873e+01,  1.05372343e+03, -2.41399605e+04,  3.14452667e+05,\
 -1.78318233e+06]

y_mbh=np.poly1d(pfit)

def get_mbh(data):


    mhe,mcore,mstar=data
    heenv=mhe-mcore
    mbh0=0.8*(0.8*heenv+mcore) # ComBinE assumption

    if mhe < 35.28:
        return mbh0
    if mhe > 61.1:
        return 0.0
    return y_mbh(x)*0.8 # PPISN



def func(x1,x2,idx):
    return (x2**idx-x1**idx)/idx

# y for logPorb
# IMF_m and IMF_n are unnormalized
def IMF_m(par1,par2):
    m1,m2,q1,q2,y1,y2=par1
    alpha,beta,gamma=par2

    t1=func(m1,m2,-alpha+2)
    t2a=func(q1,q2,-beta+1)
    t2b=func(q1,q2,-beta+2)
    t3=func(y1,y2,-gamma+1)

    return t1*(t2a+t2b)*t3

def IMF_n(par1,par2):
    m1,m2,q1,q2,y1,y2=par1
    alpha,beta,gamma=par2

    t1=func(m1,m2,-alpha+1)
    t2=func(q1,q2,-beta+1)
    t3=func(y1,y2,-gamma+1)

    return t1*t2*t3

def get_norm(par2):
    alpha,beta,gamma=par2
    # m1,m2,q1,q2,y1,y2=par1

    x1=0.0
    x2=0.0
    par1=[0.08,0.5,0.1,1,0.15,3.5]
    par2=[1.3,beta,gamma]
    x1=x1+IMF_m(par1,par2)
    x2=x2+IMF_n(par1,par2)

    par1=[0.5,1.0,0.1,1,0.15,3.5]
    par2=[alpha,beta,gamma]
    x1=x1+IMF_m(par1,par2)
    x2=x2+IMF_n(par1,par2)

    par1=[1.0,100,0.1,1,0.15,3.5]
    par2=[alpha,beta,gamma]
    x1=x1+IMF_m(par1,par2)
    x2=x2+IMF_n(par1,par2)

    par1=[0.01,0.08,0.1,1,0.15,3.5]
    par2=[0.3,beta,gamma]
    x1=x1+IMF_m(par1,par2)
    x2=x2+IMF_n(par1,par2)

    return 1.0/x1,1.0/x2


def get_M_avg(par1,par2):
    m1,m2,q1,q2,y1,y2=par1
    alpha,beta,gamma=par2

    x1=IMF_m(par1,par2)
    x2=IMF_n(par1,par2)

    return x1/x2

def get_weight(par1,par2,A1,A2):
    # SFR X lifetime X weight = number
    m1,m2,q1,q2,y1,y2=par1
    alpha,beta,gamma=par2

    m_bar=get_M_avg(par1,par2)
    kk=IMF_m(par1,par2)

    return A1*kk/m_bar


dlgm1i=0.05
dqi=0.05
dlgpi=0.025
lgm1=0.700
lgm2=2.000
q1=0.00
q2=1.000
lgp1=0.000
lgp2=3.500



def cal_number_weight(inpar,par2):
    lgm1,qi,lgp=inpar
    A1,A2=get_norm(par2)

    m1=10**lgm1
    m2=10**(lgm1+dlgm1i)
    par1=[m1,m2,qi,qi+dqi,lgp,lgp+dlgpi]

    N1=get_weight(par1,par2,A1,A2)

    return N1
    #nn=1.0
    #Ny=N1/nn
    #N=Ny*lifetime


    



def make_ppisn_orbit(data):

    mhe,m1,mcore,mstar,porb,m2,mbh = data

    porb=porb*secday
    m2=m2*msun
    m1=m1*msun
    mbh=mbh*msun
    m0=(m1+m2)
    
    a0=(cgrav*m0/4.0/np.pi/np.pi*porb**2)**(1.0/3)
    v02=cgrav*m0/a0
    
    if mbh < 0.01:
        print( 'Stop due to BH mass less than 0.01')
        exit()

    q_ratio=mbh/m2
    
    temp_a=2.0/a0-v02/(cgrav*(m2+mbh))

    if temp_a < 0.0:
        print( 'Stop due to negative semi-major axis for post-SN orbit')
        exit()

    a1=1.0/temp_a
    porb1=(4.0*np.pi*np.pi/(cgrav*(m2+mbh))*a1*a1*a1)**0.5
    temp=v02*a0*a0/(cgrav*(m2+mbh))*temp_a

    if np.fabs(1-temp) < 1e-4:
        e1=0
    else:
        e1 = (1.0-temp)**0.5

    e=e1
    a=a1/rsun
    porb=porb1/secday
    K2=2.0*np.pi*a1/porb1/np.sqrt(1-e1*e1)*mbh/(m2+mbh)/1e5 # km/s

    return mbh/msun,m2/msun,q_ratio,porb,K2,e,m1/msun,a
    


def make_vsini(v0,figname,n=10000,xlabel='',ylabel='Possibility'):
    # (data['HeOB_VHe'],'HeOB_fig1.pdf',n=10000)
    cosi=np.random.random(n)*2 - 1
    sini=np.sqrt(1.0 - cosi*cosi)

    vsini=v0*sini
    plt.figure()
    nbins=np.arange(0,v0+0.15*v0+10,10)
    plt.hist(vsini,normed=True, histtype='step',bins=nbins,lw=3,color='C0')
    ax=plt.gca()

    ax.set_xlabel(xlabel,fontsize='large')
    ax.set_ylabel(ylabel,fontsize='large')
    ax.tick_params(axis="both",direction="in",which='both')
    plt.savefig(figname,bbox_inches='tight')
    print('saving '+figname)
    plt.close()



def mhe_mc_relation(mhe):
    xx=np.log10(mhe)
    a,b,c,d=[ 0.48982066, -0.59135916,  1.32351403, -0.33861267]
    xlog = a + b*xx + c*xx**2 + d*xx**3
    return 10**xlog # final carbon core mass

def get_z_from_t_H(t_H):
    # input: t_H in Gyr
    # return z redshift
    # t_H = Hubble time return z = 0

    a,b,c = [71.01866611, -5.1898196,   3.22467184]

    return np.sqrt(a/t_H  - b) - c

def get_t_H_from_z(z):

    a,b,c = [71.01866611, -5.1898196,   3.22467184]

    return a/((z+c)**2+b)


def add_Wind_fed_XRB(result,data,phase,idx):
    data[phase+'_disk_'+idx]="%.4E" % result[0]
    data[phase+'_Lx_'+idx]="%.4E" % result[2]
    return data





import numpy as np
import matplotlib.pyplot as plt
import os
import support 

msun=1.9892e33
cgrav=6.67428e-8
rsun=6.9598e10
secday=24.0*60.0*60.0

Msun = 1.9892e33
Rsun = 6.9598e10
Lsun = 3.8418e33
clight= 2.99792458e10
secyer= 3.1558149984e7
cgrav = 6.67428e-8
cosmictime = 14e9

pfit=[-8.65828957e-08,  3.25183895e-05, -5.31786630e-03,  4.94552158e-01,\
 -2.86053873e+01,  1.05372343e+03, -2.41399605e+04,  3.14452667e+05,\
 -1.78318233e+06]

y_mbh=np.poly1d(pfit)

def get_mbh(data,ppisn=True):

#    mhe=data['he_core_mass']
#    mcore=data['c_core_mass']
#    mstar=data['star_mass']

    mhe,mcore,mstar,method=data
    if method == 'He-core':
        mbh0=mhe

        if not ppisn:
            return mbh0

        if mhe < 35.28:
            return mbh0
        if mhe > 61.1:
            return 0.0
        return y_mbh(mhe)*0.8 # PPISN

    heenv=mhe-mcore
    mbh0=0.8*(0.8*heenv+mcore) # ComBinE assumption

    if not ppisn:
        return mbh0

    if mhe < 35.28:
        return mbh0
    if mhe > 61.1:
        return 0.0
    return y_mbh(mhe)*0.8 # PPISN

def rlda(q):
    # M1/M2
    x=q**(1.0/3)
    t1=0.49*x*x
    t2=0.6*x*x+np.log(1+x)
    return t1/t2 # RL-1/a


def CE_a_div_a0(d0,mbh):
#    mhe=ds2['he_core_mass']
#    m2=ds2['star_mass']
#    lam_ce=ds2['lambda_g']#*0.0+1
    mhe,m2,lam_ce,eta_ce=d0
    t1=mhe/m2*mbh
    menv=m2-mhe
    kk=rlda(m2/mbh)
    t2=1.0/(mbh+2.0*menv/eta_ce/lam_ce/kk)


    return t1*t2

def RLO_a_div_a0(par1,par2):
    alpha,beta = par1
    q0,q = par2
    xi=1-alpha-beta
    t1=(q/q0)**(2.0*alpha-2.0)
    t2=((q+1)/(q0+1))**((-alpha-beta)/(1-xi))
    t3=((xi*q+1)/(xi*q0+1))**(3.0+2.0*((alpha*xi*xi+beta)/xi/(1-xi)))
    return t1*t2*t3

def merger_time(m1,m2,porb,e):
    m1=m1*Msun
    m2=m2*Msun
    porb=porb*24*60*60
    asep=(cgrav*(m1+m2)/4.0/np.pi/np.pi*porb*porb)**(1.0/3)
    Jdot_gr=32.0/5/(clight**5)*(2.0*np.pi*cgrav/porb)**(7.0/3)*m1*m1*m2*m2/(m1+m2)**(2.0/3)
    J=np.sqrt(cgrav*asep/(m1+m2))*m1*m2

    fe=(1+0.27 * e**10.0 + 0.33 * e**20.0 + 0.2 * e**1000.0) * (1.0 - e*e)**3.5
    # Mandel 2021
    # https://arxiv.org/pdf/2110.09254.pdf


    return J/Jdot_gr/secyer/1e9 * fe # Gyrs




# ------------------------------------------------------

def get_He_OB(d1,d2):
    d2=d2[:len(d1)]
    ch1=d1['center_h1']

    che4=d1['center_he4']
    if che4[-1] > 1e-3:
        return -1,-1
    kch1=d2['center_h1']
    if kch1[-1] < 1e-3:
        return -2,-2

    for i0,x in enumerate(ch1):
        if x < 1e-6:
            break


    for i,x in enumerate(che4):
        if i < i0:
            continue

        if x > 0.5 and che4[i+1] < 0.5:
            break
    He05_idx=i

    t0=d1['star_age']
    for j1,x in enumerate(che4):
        if j1 < i0:
            continue
        if x > 0.97 and che4[j1+1] < 0.97:
            break
    for j2,x in enumerate(che4):
        if j2 < i0:
            continue
        if x > 0.01 and che4[j2+1] < 0.01:
            break

    tau_HeOB=t0[j2] - t0[j1]

    return He05_idx, tau_HeOB

def get_BHNS_OB(d1,d2,data,kick_flag=False):

    if kick_flag:
        print('stop due to WRONG kick option')
        exit()

    # mhe,mcore,mstar=data
    mhe=d1['he_core_mass'][-1]
    mcore=d1['c_core_mass'][-1]
    mstar=d1['star_mass'][-1]

    if mhe > data['BH_NS_boundary']:
        BH_flag=True
    else:
        BH_flag=False
    if mhe < data['BH_NS_boundary'] and mcore < 1.375 and mcore > 1e-3: 
        # not BH
        # C dep and small mcore
#        print('final He_core_mass',mhe)
#        print('final C_core_mass',mcore)
#        print('Stop due to WD progenitor')
        print('\n#===================================')
        print('WARNING: WD progenitor (primary). Keeping going with M_NS=1.4.')
        print('#===================================\n')
        BH_flag=False
#        exit()

    if BH_flag:
        #mco=support.get_mbh([mhe,mcore,mstar,data['BH_mass_calculation']])
        mco=get_mbh([mhe,mcore,mstar,data['BH_mass_calculation']],ppisn=data['PPISN_flag'])
    else:
        mco=1.4 # NS mass
        print('\n#===================================')
        print('  WARNING: forming NS (primary) WITHOUT Kick')
        print('#===================================\n')

    inputs=[
                data['BHOB_s1_He00_MHe'],
                data['BHOB_s1_He00_MHe'],
                data['BHOB_s1_He00_MC'],
                data['BHOB_s1_He00_M'],
                data['BHOB_s1_He00_Porb'],
                data['BHOB_s2_He00_M'],
                mco
            ]

    mbh,m2,q_ratio,porb,K2,e,m1,a0=support.make_ppisn_orbit(inputs)
    # print 'ecc',e
    # q_ratio - mbh/m2
    # mbh-BH mass | m2-OB star mass | porb-porb after BH formation
    # K2-semi-amp of OB star | e-ecc | m1-pre-collapse mass of primary star
    # a-semimajor-axis with e in rsun

    # circularization 
    # Jorb keeps unchanged
    a_circ=a0*(1.0-e*e)

    rl2=rlda(m2/mbh)*a_circ
    rl20=rlda(m2/mbh)*a0*(1-e)

    #d2=d2[len(d1):]

    age=d2['star_age']
    ch1=d2['center_h1']
    r2=d2['photosphere_r']

    n0 = len(d1)

    for i in range(len(age)):
        if i < n0 - 1:
            continue
        if ch1[i] < 1e-5:
            break
        if r2[i] > rl2:
            break

    for RLO_idx in range(len(r2)):
        if RLO_idx < n0 - 1:
            continue
        if r2[RLO_idx] > rl2:
            break

    tau_OBBH=age[i] - age[0]

    result=[mbh,m2,q_ratio,porb,K2,e,m1,a0,a_circ,tau_OBBH,ch1[i],r2[i],rl20,RLO_idx]
    return result

def get_BHNS_He(d1,d2,data,kick_flag=False):

    eta_ce=data['BHWR_etaCE']
    qmin=data['BHWR_qmin']
    porbmax=data['BHWR_porbmax']
    beta=data['BHWR_beta']
    alpha=data['BHWR_alpha']

    if alpha > 1e-8:
        alpha = 0.0
        print('alpha is fixed to be zero')

    if beta > 1.0-1e-8:
        print('\n#===================================')
        print('beta',beta)
        print('setting beta to be 1-1e-8 to avoid numerical issue at zero accretion efficiency')
        print('1-1e-8 is close enough to the zero accretion efficiency case')
        print('#===================================\n')
        beta=1-1e-8

    par1 = [alpha,beta]


    m2=data['BHWR_s2_RLO_M']
    porb=data['BHOB_Porb']*24*60*60 # uncircularized orbital period
    mbh=data['BHOB_MBH']
    ecc=data['BHOB_e']

    porb=porb*(1-ecc*ecc)**1.5

    a0=(cgrav*(mbh+m2)*Msun/4.0/np.pi/np.pi*porb*porb)**(1.0/3)
    rl2=rlda(m2/mbh)*a0
    porb0=porb/24/60.0/60.0
    s2ch1=data['BHWR_s2_RLO_ch1']
    mhe=data['BHWR_s2_He05_MHe']


    if (s2ch1 > 0.2) and (flagCE == False):
        print('Case A mass transfer onto BH')
        print('with core H1',s2ch1)
        print('using fitting result for early Case A')
        print('only apply to zero accretion efficiency')
        # xxu ---- early Case A fitting 
        # ******
        print('terminated: to be updated')
        exit()

    q0=mbh/m2 # accretor / donor

    dm2=m2-mhe
    mbhrlo = mbh + dm2*(1.0 - par1[0] - par1[1])
    q1=mbhrlo/mhe

    flagCE=False
    if (q0 < qmin) or (porb0 > porbmax):
        flagCE=True

    if not flagCE:
        mbh=mbhrlo

    if flagCE:
    #    mhe,m2,lam_ce=d0
        if data['BHWR_fix_lambda_flag']:
            lam_ce = data['BHWR_fix_lambda']
        else:
            lam_ce = data['BHWR_s2_RLO_lam_ce']
        if lam_ce < 1e-8:
            print('terminated: wrong lambda_bind')
        af=CE_a_div_a0([mhe,m2,lam_ce,eta_ce],mbh) * a0
    else:
        par1 = [alpha,beta]
        par2 = [1.0/q0,1.0/q1]  # donor / accretor
        af=RLO_a_div_a0(par1,par2) * a0

    rl_He=rlda(mhe/mbh)*af / rsun

    merger=False

    kd2=d2[d2['center_h1'] < 1e-6]
    che4=kd2['center_he4']
    for idx_He_ign,x in enumerate(che4):
        if x >0.97 and che4[idx_He_ign+1] < 0.97:
            break

    t0=kd2['star_age']
    tauWRBH=t0[-1] - t0[idx_He_ign]

    if rl_He < data['BHWR_s2_He05_RHe']:
        merger=True

    if merger:
        porbf=-1
        af=-1*rsun
        tauWRBH=-1*1e6
    else:
        porbf=np.sqrt(np.array(af)**3*np.pi*np.pi*4.0/(cgrav*(mbh+mhe)*Msun))/24/60/60
        # in days

    e1=0.0
    K2=2.0*np.pi*af/(porbf*secday)/np.sqrt(1-e1*e1)*mbh/(mhe+mbh)/1e5

    result=[flagCE,q0,porb0,a0/rsun,q1,porbf,af/rsun,merger,mbh,mhe,rl_He,tauWRBH,K2]

    return result 

def get_BHBH(d1,d2,data,kick_flag=False):

    if data['BHWR_porbf'] < 1e-8:
        print('\n#===================================')
        print('merge before BBH')
        print('#===================================\n')
        result=[-1,-1,-1,-1,-1,-1,-1,-1,-1,-1]
        return result

    mbh1=data['BBH_MBH1']
    if data['BBH_s2_He05_MHe'] < data['BH_NS_boundary']:
        if data['BBH_s2_He00_MC'] < 1.375:
            print('\n#===================================')
            print('WARNING: WD progenitor (secondary). Keeping going with M_NS=1.4.')
            print('#===================================\n')

        mbh2 = 1.4 
        print('\n#===================================')
        print('  WARNING: forming NS (secondary) WITHOUT Kick')
        print('#===================================\n')

    else:
        mbh2=get_mbh([data['BBH_s2_He05_MHe'],data['BBH_s2_He00_MC'],-1,data['BH_mass_calculation']],ppisn=data['PPISN_flag'])

    inputs=[
            data['BBH_s2_He05_MHe'],
            data['BBH_s2_He05_MHe'],
            data['BBH_s2_He00_MC'],
            -1,
            data['BHWR_porbf'],
            data['BBH_MBH1'],
            mbh2
            ]


    mbh2,mbh1,x1,porb,x2,ecc,x3,x4=support.make_ppisn_orbit(inputs)


    tauM       = merger_time(mbh1,mbh2,porb,ecc)
    tauM0       = merger_time(mbh1,mbh2,porb,0)
    tau_delay = d2['star_age'][-1]/1e9 + tauM
    mchirp     = (mbh1*mbh2)**(3.0/5)/(mbh1+mbh2)**(1.0/5)
    q1         = mbh2/mbh1
    q2         = min(q1,1.0/q1) # 
    redshift   = support.get_z_from_t_H(support.get_t_H_from_z(0) - tau_delay) # birth redshift if merging at z=0
    Xeff       = 0
    if data['BHWR_porbf'] <  0.3:
        Xeff = mbh2/(mbh1+mbh2) 
        # Qin 2018
        # could be reduced by wind braking or less efficient tide

    if support.get_t_H_from_z(0) - tau_delay < 0.0:
        redshift = -1

    result=[mbh2,tauM,tau_delay,mchirp,q1,q2,redshift,Xeff,ecc,tauM0]

    return result 
        
cgrav=6.67428e-8
msun=1.9892e33
clight=2.99792458e10
Lsun=3.8418e33
rsun=6.9598e10
sigma_SB=5.670400e-5
secyr=3.1558149984e7
Teffsun=5777.0e0

def func_y(x,a,b,c,d):
#    a,b,c,d = par
    y = a + b*x + c*x**2 + d*x**3
    return y


def cal_disk_criterion(data,eta0=1.0/3.0,beta=1.0,coef_w=2.6,gamma=1):

    mbh,mob,rob,porb,mdot_w,Gedd,X=data
    mdot_w=10**mdot_w * msun/secyr

    if rob < 1e-8:
        rob=1e-8
        #print('R < 1e-8')
        return -1,-1,-1
    if porb < 1e-8:
        #print('Porb < 1e-8')
        return -1,-1,-1
    
    rob=rob * rsun
    porb=porb *24*60*60

#    if He_wind:
#	popt1=[-10.44730985,   4.56657325,  -1.02414871,   0.19863583]
#	mdot_w=10**(func_y(np.log10(mob),*popt1))*msun/secyr
#	Gedd=0.0
    
    vesc=np.sqrt(2.0*cgrav*mob*msun/rob*(1.0-Gedd))
    aorbit=(cgrav*(mbh+mob)*msun/4.0/np.pi/np.pi*porb*porb)**(1.0/3)
    vorb=np.sqrt(cgrav*(mob+mbh)*msun/aorbit)
    vw=(coef_w*vesc)*(1.0-rob/aorbit)**beta
    vrel=np.sqrt(vw*vw+vorb*vorb)
    RA=2*cgrav*mbh*msun/vrel/vrel
    RISCO=6*cgrav*mbh*msun/clight/clight * gamma
    j=0.5*vorb*RA*RA/aorbit*eta0
    RD=j*j/cgrav/mbh/msun
    disk_flag1=RD/RISCO

    Ledd=65335/(1+X)*mbh*Lsun # mbh in msub
    mdot_edd=Ledd/cgrav/mbh/msun*RISCO
    mdot_acc=mdot_w*RA*RA*vrel/aorbit/vw/aorbit/4e0

    Lx1=cgrav*mbh*msun*mdot_acc/RISCO*0.5
    
    return disk_flag1,Ledd/1e38,Lx1/1e38

#    for i,x in enumerate(disk_flag1):
#        if x < 1e-50:
#            if porbx[i] > 1:
#                print '\n'
#                print RD[i],RISCO[i]
#                print j[i]
#                print vorb[i],RA[i],aorbit[i],eta0
#                print vrel[i],porb0[i]
#                print rob[i]

        




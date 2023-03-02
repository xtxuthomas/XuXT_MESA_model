import numpy as np
import matplotlib.pyplot as plt
import os
import evo
import make_pdf_report 
import support
import sys
import shutil

data=dict(test_flag=False) 
# record properties for each phase and control parameters
# new value can be easily added by
# data[name]=value
data['open_pdf_report_after_calculation']=False
data['open_pdf_cmd']='gnome-open' 
# if 'open_pdf_report_after_calculation' == True
# open pdf file with the cmd defined by data['open_pdf_cmd']
# for ubuntu, data['open_pdf_cmd'] can be 'evince' or 'gnome-open'

data['home_path'] = os.getcwd()

overwrite_mode=True
# if running with the same inputs as previous run,
# 'overwrite_mode=False' will keep previous run and save new run by adding  '_new' as identifier

# -------------------------------------------------------------------
# overview of the inputs of this script

# lgm1i,qi,lgPi
#x1,x2,x3=1.7,0.8,3.0

#p0='/vol/hal/halraid/pablo/mesa-runs/LMC_models/lowsc/models/%.3f/%.3f_%.3f/' % (x1,x2,x3))
#p0='/vol/hal/halraid/cwang/MESA_binary_models/sc1/%.3f/%.3f_%.3f/' % (x1,x2,x3))
#p0='/vol/hal/halraid/dpauli/GRID/%.3f/%.3f_%.3f/' % (x1,x2,x3)

#data['file_name']='LMC_' 
#data['file_name']='SMC_' 

#data['model_path'] = p0
#data['output'] = 'Results'

#data['model_directory']=p0.strip('%.3f/%.3f_%.3f/' % (x1,x2,x3))
#work_dir=data['file_name']+'%.3f_%.3f_%.3f/' % (x1,x2,x3)

# ------------------------------------------------------------------
# outputs of this script

# A pdf file named by work_dir will be saved in data['output'] directory.
# Inside data['output'], there is another directory also named by work_dir, 
# which saves all tex files.

# -------------------------------------------------------------------
# this code block allows you to run this script by
# python XuXT_MESA_model.py 1.7 0.8 1.5 2

try:
    x1 = float(sys.argv[1])
    x2 = float(sys.argv[2])
    x3 = float(sys.argv[3])
    idx = int(sys.argv[4])
    if idx < 1 or idx > 3:
        print('wrong idx')
        exit()
except:

    print('input initial parameters')
    x1=float(input('log M1i:'))
    x2=float(input('qi:'))
    x3=float(input('logPi:'))
    
    print('\nModel:')
    print('1) LMC (Pablo)  : /vol/hal/halraid/pablo/mesa-runs/LMC_models/lowsc/models/%.3f/%.3f_%.3f/' % (x1,x2,x3))
    print('2) SMC (Chen)   : /vol/hal/halraid/cwang/MESA_binary_models/sc1/%.3f/%.3f_%.3f/' % (x1,x2,x3))
    print('3) LMC (Daniel) : /vol/hal/halraid/dpauli/GRID/%.3f/%.3f_%.3f/' % (x1,x2,x3))
    idx=int(input('which one? (1, 2, or 3):'))
    print('\n')
    
if idx == 1:
    p0='/vol/hal/halraid/pablo/mesa-runs/LMC_models/lowsc/models/%.3f/%.3f_%.3f/' % (x1,x2,x3)
elif idx ==2:
    p0='/vol/hal/halraid/cwang/MESA_binary_models/sc1/%.3f/%.3f_%.3f/' % (x1,x2,x3)
elif idx ==3:
    p0='/vol/hal/halraid/dpauli/GRID/%.3f/%.3f_%.3f/' % (x1,x2,x3)
else:
    print('exit: wrong model directory')
    exit()

print('Model: '+p0+'\n')

if idx == 1 or idx == 3:
    data['file_name']='LMC_' 
elif idx ==2:
    data['file_name']='SMC_' 

data['model_path'] = p0
data['output'] = 'Results'

data['model_directory']=p0.strip('%.3f/%.3f_%.3f/' % (x1,x2,x3))
work_dir=data['file_name']+'%.3f_%.3f_%.3f/' % (x1,x2,x3)

# -------------------------------------------------------------------
# initialization and setting control parameters

data['lgm1i']=x1
data['qi']=x2
data['logpi']=x3
data['m1i']=round(10**x1,4)
data['m2i']=data['m1i']*x2
data['porbi']=round(10**x3,4)

data['BH_mass_calculation']='ComBinE' 
#data['BH_mass_calculation']='He-core' 
data['PPISN_flag']=True
# 'ComBinE' or 'He-core'
# -- 'ComBinE': 20% of He-rich envelope is ejected and 
#    then 20% of mass is lost due to the release of gravitational
#    binding energy
# -- 'He-core': simply take He core mass as BH mass
# both of these two options only works for non-PPISN system
# if PPISN occurs, mass ejection is given by a fitting formula 
# based on Marchant+2019: https://iopscience.iop.org/article/10.3847/1538-4357/ab3426
# In addition, you can turn off PPISN by setting data['PPISN_flag']=False

if not os.path.exists(work_dir):
    os.system('mkdir '+work_dir)
else:
    print('clean...\n')
    shutil.rmtree(work_dir)
    #os.rmdir(work_dir)
    os.system('mkdir '+work_dir)
os.chdir(work_dir)

data['HeOB_vsini']=False 
# check the effect of sini 
# this will generate two plots
# better to keep it 'False' 

data['Wind_fed_BHHMXB']=True

data['BH_NS_boundary']=6.6 
# BH if final He core mass larger than this value.
# the boundary between WD and NS is determined by ECSN,
# which is not considered here. 
# For WD, I will keep going by treating it as NS (M=1.4)

# mass transfer onto first-born BH/NS
data['BHWR_etaCE']=1.0 # common envelope (CE) efficiency
data['BHWR_qmin']=0.3 # accretor/donor < qmin -> CE
data['BHWR_porbmax']=1000.0 # porb > porbmax -> CE
data['BHWR_beta']=1.0 # usually the Eddington limit is far below the mass transfer rate
data['BHWR_alpha']=0.0 # usually fixed (non-zero case is not well tested yet)
data['BHWR_fix_lambda_flag']=False # use fixed binding energy parameter?
data['BHWR_fix_lambda']=1.0 # use data['BHWR_fix_lambda'] if data['BHWR_fix_lambda_flag']=True 
if data['BHWR_fix_lambda_flag']:
    data['BHWR_lambda_type']='fixed value'
    # use data['BHWR_fix_lambda']
else:
    data['BHWR_lambda_type']='MESA output'
    # use lambda_g column 
    # if can not find lambda_g in history file, use data['BHWR_fix_lambda'] 

# -------------------------------------------------------------------
# check summary file in the model directory

data['summary_file']=''
if os.path.exists(p0+'summary.txt'):
    fp=open(p0+'summary.txt','r')
    for line in fp:
        print(line.strip('\n'))
        if 'with M' in line:
            line=line.split('with M')
            line=line[0]+'with M$>$13 Msun\n'
        data['summary_file']=data['summary_file']+line+'\\newline'
    fp.close()
    print('')
else:
    print('Warning: can not find summary file ')

# -------------------------------------------------------------------
# calculate birth rates with different initial distributions

inpar=[x1,x2,x3]
SFR=0.05
data['Rbirth_23_01_055']="%.4E" % (support.cal_number_weight(inpar,[2.3,0.1,0.55]) * SFR)
data['Rbirth_27_01_055']="%.4E" % (support.cal_number_weight(inpar,[2.7,0.1,0.55]) * SFR)
data['Rbirth_23_0_0']="%.4E" % (support.cal_number_weight(inpar,[2.3,0,0]) * SFR)
data['Rbirth_0_0_0']="%.4E" % (support.cal_number_weight(inpar,[0,0,0]) * SFR)

make_pdf_report.write_info(data)

# -------------------------------------------------------------------
# start analysis
# I will go through the following phases
# (1) stripped star + OB star, (2) BH/NS + OB star, (3) BH/NS + stripped star, and (4) BH/NS + BH/NS
# (1) and (2) can be directly extracted from the history files
# - properties of (1) are picked at the middle of core He burning of the primary star
# - properties of (2) are picked at the birth time of the compact object 
# (3) and (4) are anaylized with several assumptions since 
# our models switch to single star evolution after the termination of primary star
# there could be some bugs if (1) does not exist
# If data['Wind_fed_BHHMXB']=True, I will also check whether accretion disk can form
# around BH in BH+OB and BH+He phases. This estimation only apply for BH. The story
# for NS is much more complicated (see the output pdf for details)

# kick is not included since we need Monte Carlo simulation for this.
# with efficient semiconvection or low metallicity, donor star could be core He burning and clothed by 
# slowly expanding H-rich envelope. This case is not considered neither.

d1=np.genfromtxt(p0+'LOGS1/history.data',names=True,skip_header=5)
d2=np.genfromtxt(p0+'LOGS2/history.data',names=True,skip_header=5)
# binary info should be saved in LOGS1/history.data

# check ------------------------------------------------------

final_ch1=d1['center_h1'][-1]
if final_ch1 > 1e-5:
    print( 'Primary terminated before core H depletion')
    exit()

final_che4=d1['center_he4'][-1]
if final_che4 > 1e-5:
    print( 'Primary terminated before core He depletion')
    exit()


# He+OB ------------------------------------------------------
s1_He05_idx, tau_HeOB = evo.get_He_OB(d1,d2)

if s1_He05_idx < 0:
    print( 'No stripped star + OB star phase')
else:
    data['HeOB_Porb']=round(d1['period_days'][s1_He05_idx],4)
    data['HeOB_VHe']=round(d1['v_orb_1'][s1_He05_idx],4)
    data['HeOB_Rstripped_div_RL']=round(d1['photosphere_r'][s1_He05_idx]/d1['rl_1'][s1_He05_idx],4)
    data['HeOB_logMdot_mtr']=round(d1['lg_mtransfer_rate'][s1_He05_idx],4)
    data['HeOB_VOB']=round(d1['v_orb_2'][s1_He05_idx],4)
    data['HeOB_q']=round(d1['star_mass'][s1_He05_idx]/d2['star_mass'][s1_He05_idx],4)
    data['HeOB_s1_M']=round(d1['star_mass'][s1_He05_idx],4)
    data['HeOB_s1_logL']=round(d1['log_L'][s1_He05_idx],4)
    data['HeOB_s1_logTeff']=round(d1['log_Teff'][s1_He05_idx],4)
    data['HeOB_s1_Xsurf']=round(d1['surface_h1'][s1_He05_idx],4)
    data['HeOB_s1_logMdot']=round(d1['lg_wind_mdot_1'][s1_He05_idx],4)
    data['HeOB_s2_M']=round(d2['star_mass'][s1_He05_idx],4)
    data['HeOB_s2_logL']=round(d2['log_L'][s1_He05_idx],4)
    data['HeOB_s2_logTeff']=round(d2['log_Teff'][s1_He05_idx],4)
    data['HeOB_s2_Xsurf']=round(d2['surface_h1'][s1_He05_idx],4)
    data['HeOB_s2_Xcent']=round(d2['center_h1'][s1_He05_idx],4)
    data['HeOB_s2_logMdot']=round(d1['lg_wind_mdot_2'][s1_He05_idx],4)
    data['HeOB_s2_Vrot']=round(d2['surf_avg_v_rot'][s1_He05_idx],4)
    data['HeOB_s2_v_div_vc']=round(d2['surf_avg_omega_div_omega_crit'][s1_He05_idx],4)
    data['HeOB_lifetime']=tau_HeOB
    data['HeOB_age_He05']=round(d1['star_age'][s1_He05_idx],4)

    data['HeOB_s1_MHecore']=round(d1['he_core_mass'][s1_He05_idx],4)
    data['HeOB_s1_MHenv']=round(d1['star_mass'][s1_He05_idx]-d1['he_core_mass'][s1_He05_idx],4)
    data['HeOB_s1_RHe']=round(d1['photosphere_r'][s1_He05_idx],4)
    data['HeOB_s1_RHecore']=round(d1['he_core_radius'][s1_He05_idx],4)

    if data['HeOB_vsini']:
        support.make_vsini(data['HeOB_VHe'],'HeOB_fig1.pdf',n=10000,xlabel='V$_{\\rm He}$ sini [km/s]')
        support.make_vsini(data['HeOB_VOB'],'HeOB_fig2.pdf',n=10000,xlabel='V$_{\\rm OB}$ sini [km/s]')
    make_pdf_report.write_He_OB(data)


# BH/NS+OB ------------------------------------------------------------ 
s2_ch1_BH_formation=d2['center_h1'][len(d1)]
if s2_ch1_BH_formation < 1e-5:
    print( 'No OB + BH phase')
else:
    data['BHOB_s1_He00_MHe']=round(d1['he_core_mass'][-1],4) # 'he_core_mass'
    data['BHOB_s1_He00_MC']=round(d1['c_core_mass'][-1],4)  # 'c_core_mass'
    data['BHOB_s1_He00_M']=round(d1['star_mass'][-1],4) # 'star_mass'
    data['BHOB_s2_He00_M']=round(d2['star_mass'][len(d1)],4) # 'star_mass'
    data['BHOB_s1_He00_Porb']=round(d1['period_days'][-1],4) # period_days

    if data['BHOB_s1_He00_MHe'] > 35.28 and data['BHOB_s1_He00_MHe'] < 61.1:
        data['BHOB_PPISN_flag']='YES'
    elif data['BHOB_s1_He00_MHe'] <= 35.28:
        data['BHOB_PPISN_flag']='NO (not massive enough)'
    elif data['BHOB_s1_He00_MHe'] >= 61.1:
        data['BHOB_PPISN_flag']='NO (PISN occurs)'
    else:
        print('STOP: something wrong with final He core mass (primary)')
        exit()

    if not data['PPISN_flag']:
        data['BHOB_PPISN_flag']='turned off'

    if data['BHOB_s1_He00_MC'] < 0.1 and data['BHOB_PPISN_flag'] != 'YES' and data['BH_mass_calculation'] != 'He-core':
        print('Primary does not have carbon core')
        print("try data['BH_mass_calculation']='He-core' option")
        data['BH_mass_calculation']='He-core'

    data['BHOB_s1_He00_Rstar']=round(d1['photosphere_r'][-1],4) # 'he_core_mass'
    data['BHOB_s1_He00_Rstar_div_RL']=round(d1['photosphere_r'][-1]/d1['rl_1'][-1],4) # 'he_core_mass'
    data['BHOB_s1_He00_RHe']=round(d1['he_core_radius'][-1],4) # 'he_core_mass'
    data['BHOB_s1_He00_logL']=round(d1['log_L'][-1],4)
    data['BHOB_s1_He00_logTeff']=round(d1['log_Teff'][-1],4)
    data['BHOB_s1_He00_Xsurf']=round(d1['surface_h1'][-1],4)
    data['BHOB_s1_He00_logMdot']=round(d1['lg_wind_mdot_1'][-1],4)
    data['BHOB_s1_He00_logMdot_mtr']=round(d1['lg_mtransfer_rate'][-1],4)
    data['BHOB_s1_He00_logL']=round(d1['log_L'][-1],4)
    data['BHOB_s1_He00_logTeff']=round(d1['log_Teff'][-1],4)
    data['BHOB_s1_He00_Xsurf']=round(d1['surface_h1'][-1],4)
    data['BHOB_s1_He00_Ysurf']=round(d1['surface_he4'][-1],4)
    data['BHOB_s1_He00_N14surf']="%.4E" % d1['surface_n14'][-1]
    data['BHOB_s1_He00_Xcent']=round(d1['center_h1'][-1],4)
    data['BHOB_s1_He00_XHecent']=round(d1['center_he4'][-1],4)
    data['BHOB_s1_He00_XCcent']=round(d1['center_c12'][-1],4)
    data['BHOB_s1_He00_Vrot']=round(d1['surf_avg_v_rot'][-1],4)
    data['BHOB_s1_He00_v_div_vc']=round(d1['surf_avg_omega_div_omega_crit'][-1],4)

    result = evo.get_BHNS_OB(d1,d2,data)
    names=['mbh',
            'm2',
            'q_ratio',
            'porb',
            'K2',
            'e',
            'm1',
            'a0',
            'a',
            'tau_OBBH',
            'ch1[i]',
            'r2[i]',
            'rl2'
            ]
    #for x1,x2 in zip(names,result):
    #    print('{:10s} \t {:.3f}'.format(x1,x2))

    data['BHOB_MBH']=round(result[0],4)
    data['BHOB_MOB']=round(result[1],4)
    data['BHOB_ROB']=round(d2['photosphere_r'][len(d1)],4)
    data['BHOB_q']=round(result[2],4)
    data['BHOB_Porb']=round(result[3],4)
    data['BHOB_K2']=round(result[4],4)
    data['BHOB_e']=round(result[5],4)
    data['BHOB_a_without_circ']=round(result[7],4)
    data['BHOB_a']=round(result[8],4)
    data['BHOB_lifetime']=round(result[9],4)
    data['BHOB_s2_final_core_H1']=round(result[10],4)
    data['BHOB_s2_final_r2']=round(result[11],4)
    data['BHOB_s2_final_rl2']=round(result[12],4) # at periastron
    data['BHOB_age_He00']=round(d1['star_age'][-1],4)

    temp=data['BHOB_s2_final_r2']/data['BHOB_s2_final_rl2']
    data['BHOB_check_periastron']="%.4E" % temp
    if temp > 0.99:
        data['BHOB_check_periastron']=data['BHOB_check_periastron']+' (\\textbf{WARNING:} OB star fills its Roche Lobe during periastron passage)'

    # circularized rl2
    data['BHOB_s2_final_circ_rl2']=data['BHOB_s2_final_rl2']/(data['BHOB_a_without_circ'] * (1-data['BHOB_e'])) * data['BHOB_a']

    data['BHOB_s2_M']=round(d2['star_mass'][len(d1)],4)
    data['BHOB_s2_logL']=round(d2['log_L'][len(d1)],4)
    data['BHOB_s2_logTeff']=round(d2['log_Teff'][len(d1)],4)
    data['BHOB_s2_Xsurf']=round(d2['surface_h1'][len(d1)],4)
    data['BHOB_s2_logMdot']=round(d1['lg_wind_mdot_2'][len(d1)-1],4)
    data['BHOB_s2_M']=round(d2['star_mass'][len(d1)],4)
    data['BHOB_s2_logL']=round(d2['log_L'][len(d1)],4)
    data['BHOB_s2_logTeff']=round(d2['log_Teff'][len(d1)],4)
    data['BHOB_s2_Xsurf']=round(d2['surface_h1'][len(d1)],4)
    data['BHOB_s2_Ysurf']=round(d2['surface_he4'][len(d1)],4)
    data['BHOB_s2_N14surf']="%.4E" % d2['surface_n14'][len(d1)]
    data['BHOB_s2_Xcent']=round(d2['center_h1'][len(d1)],4)
    data['BHOB_s2_Vrot']=round(d2['surf_avg_v_rot'][len(d1)],4)
    data['BHOB_s2_v_div_vc']=round(d2['surf_avg_omega_div_omega_crit'][len(d1)],4)

    make_pdf_report.write_BHNS_OB(data)

    data['BHWR_s2_RLO_idx']=int(result[-1])


# BH/NS+He ---------------------------------------------------------------------

x1=data['BHOB_s2_final_circ_rl2'] # circularized rl2
x2=d2['photosphere_r'][-1]
if x2 < x1:
    print('Terminated: No interaction after OB+BH phase')
    exit()

ch1 =d2['center_h1']
che4=d2['center_he4']
for s2_idx_He05,y in enumerate(che4):
    if ch1[s2_idx_He05] > 1e-6:
        continue
    if y > 0.5 and che4[s2_idx_He05+1] < 0.5:
        break

if che4[s2_idx_He05] > 0.6:
    print('secondary termated before He05')
    exit()

data['BHWR_s2_He05_MHe']=d2['he_core_mass'][s2_idx_He05]
data['BHWR_s2_He05_RHe']=d2['he_core_radius'][s2_idx_He05]
data['BHWR_MHe']=d2['he_core_mass'][s2_idx_He05]
data['BHWR_s2_RLO_M']=d2['star_mass'][data['BHWR_s2_RLO_idx']]
data['BHWR_s2_RLO_ch1']=d2['center_h1'][data['BHWR_s2_RLO_idx']]
if data['BHWR_fix_lambda_flag']:
    data['BHWR_s2_RLO_lam_ce']=data['BHWR_fix_lambda']
else:
    try:
        data['BHWR_s2_RLO_lam_ce']=d2['lambda_g'][data['BHWR_s2_RLO_idx']]
    except:
        print('#------------------------------------------------------')
        print('can not find lambda_g in history file')
        print('usuing BHWR_fix_lmabda option (default: lambda_g=1)')
        print('#------------------------------------------------------')
        data['BHWR_s2_RLO_lam_ce']=data['BHWR_fix_lambda']
        data['BHWR_fix_lambda_flag']=True

result = evo.get_BHNS_He(d1,d2,data)
# flagCE,q0,porb0,a0/rsun,q1,porbf,af/rsun,merger,mbh,mhe,rl_He,tauWRBH

data['BHWR_flagCE']=result[0]
data['BHWR_q0']=round(result[1],4)
data['BHWR_porb0']=round(result[2],4)
data['BHWR_a0']=round(result[3],4)
data['BHWR_qf']=round(result[4],4)
data['BHWR_porbf']=round(result[5],4)
data['BHWR_af']=round(result[6],4)
data['BHWR_flag_merger']=result[7]
data['BHWR_mbh']=result[8]
data['BHWR_mhe']=round(result[9],4)
data['BHWR_rl_He']=round(result[10],4)
data['BHWR_lifetime']=max([result[11],0]) 
data['BHWR_He05_age']=d2['star_age'][s2_idx_He05]
data['BHWR_K2']=round(result[12],4)

data['BHWR_s2_He05_MHe']=round(d2['he_core_mass'][s2_idx_He05],4)
data['BHWR_s2_He05_RHe']=round(d2['he_core_radius'][s2_idx_He05],4)
data['BHWR_s2_RLO_lam_ce']="%.4E" % data['BHWR_s2_RLO_lam_ce']
data['BHWR_MHe']=round(data['BHWR_MHe'],4)
data['BHWR_s2_RLO_M']=round(data['BHWR_s2_RLO_M'],4)
data['BHWR_s2_RLO_ch1']=round(data['BHWR_s2_RLO_ch1'],4)

if data['BHWR_flagCE']:
    data['BHWR_MT_type']='CE'
else:
    data['BHWR_MT_type']='Stable MT'

if data['BHWR_flag_merger']:
    data['BHWR_merger']='YES'
else:
    data['BHWR_merger']='NO'

make_pdf_report.write_BHNS_He(data)

# BBH ---------------------------------------------------

data['BBH_MBH1']=data['BHWR_mbh']
data['BBH_s2_He05_MHe']=data['BHWR_s2_He05_MHe']
data['BBH_s2_He00_MC']=round(d2['c_core_mass'][-1],4)
if data['BBH_s2_He00_MC'] < 1e-3:
    print('secondary terminated before developing carbon core')
    print('using fitting formula')
    if data['BBH_s2_He05_MHe'] < 1e-3:
        print('terminated: He core mass < 1e-3')
        exit()
    data['BBH_s2_He00_MC']=round(support.mhe_mc_relation(data['BBH_s2_He05_MHe']),4)
    data['BBH_s2_MC_method']='fitting formula (SMC)' 
    # for massive secondary star, it can be terminated during core He burning (no well developed carbon core)
    # to avoid problem with "data['BH_mass_calculation']='ComBinE'" option,
    # I made a fitting formula basing on the SMC grid to get MC from MHe
else:
    data['BBH_s2_MC_method']='MESA output'
if data['BBH_s2_He05_MHe'] > 35.28 and data['BBH_s2_He05_MHe'] < 61.1:
    data['BBH_PPISN_flag']='YES'
elif data['BBH_s2_He05_MHe'] <= 35.28:
    data['BBH_PPISN_flag']='NO (not massive enough)'
elif data['BBH_s2_He05_MHe'] >= 61.1:
    data['BBH_PPISN_flag']='NO (PISN occurs)'

if not data['PPISN_flag']:
    data['BBH_PPISN_flag']='turned off'


result = evo.get_BHBH(d1,d2,data)
# result=[mbh2,tauM,tau_delay,mchirp,q1,q2,redshift,Xeff,ecc]

data['BBH_MBH2']=round(result[0],4)
#data['BBH_tau_merger']=round(result[1],4)
#data['BBH_tau_merger0']=round(result[9],4)
#data['BBH_tau_delay']=round(result[2],4)
data['BBH_tau_merger']="%.4E" % result[1]
data['BBH_tau_merger0']="%.4E" % result[9]
data['BBH_tau_delay']="%.4E" % result[2]
data['BBH_Mchirp']=round(result[3],4)
data['BBH_q1']=round(result[4],4)
data['BBH_q2']=round(result[5],4)
data['BBH_birthz']=round(result[6],4)
data['BBH_Xeff']=round(result[7],4)
data['BBH_ecc']=round(result[8],4)
data['BBH_ecc_factor']=round(result[1]/result[9],4)
if float(data['BBH_tau_merger']) < 0.0:
    data['BBH_ecc_factor'] = -1 # merger before BBH 

if data['BBH_birthz'] < -0.99:
    data['BBH_birthz'] = '[Hubble time $<$ delay time]'


make_pdf_report.write_BHBH(data)

# BH wind-fed X-ray binary ---------------------------------

# accretion disk can form around BH if Rdisk/RISCO > 1
# 

# OB+BH
inputs=[
        data['BHOB_MBH'],
        data['BHOB_MOB'],
        data['BHOB_ROB'],
        data['BHOB_Porb'],
        data['BHOB_s2_logMdot'],
        d2['surf_avg_Lrad_div_Ledd'][len(d1)],
        data['BHOB_s2_Xsurf']
        ]


# gamma = 1/6,1,3/2
# beta = 0.8,1
# eta0 = 1, 1/3


if  data['Wind_fed_BHHMXB']:

    result = evo.cal_disk_criterion(inputs,eta0=1.0/3.0,beta=1.0,coef_w=2.6,gamma=1)
    data=support.add_Wind_fed_XRB(result,data,'BHOB','0')
    result = evo.cal_disk_criterion(inputs,eta0=1.0,beta=1.0,coef_w=2.6,gamma=1)
    data=support.add_Wind_fed_XRB(result,data,'BHOB','1')
    result = evo.cal_disk_criterion(inputs,eta0=1.0/3.0,beta=0.8,coef_w=2.6,gamma=1)
    data=support.add_Wind_fed_XRB(result,data,'BHOB','2')
    result = evo.cal_disk_criterion(inputs,eta0=1.0/3.0,beta=1.0,coef_w=2.6,gamma=1.0/6)
    data=support.add_Wind_fed_XRB(result,data,'BHOB','3')
    result = evo.cal_disk_criterion(inputs,eta0=1.0/3.0,beta=1.0,coef_w=2.6,gamma=3.0/2)
    data=support.add_Wind_fed_XRB(result,data,'BHOB','4')
    
    def func_y(x,a,b,c,d):
    #    a,b,c,d = par
        y = a + b*x + c*x**2 + d*x**3
        return y
    
    def get_He_wind(mhe):
        popt1=[-10.44730985,   4.56657325,  -1.02414871,   0.19863583]
        mdot_w=(func_y(np.log10(mhe),*popt1)) # log msun/secyr
        return mdot_w # fitting formula based on SMC binary models (sc=1)
    
    # He+BH
    inputs=[
            data['BHWR_mbh'],
            data['BHWR_s2_He05_MHe'],
            data['BHWR_s2_He05_RHe'],
            data['BHWR_porbf'],
            get_He_wind(data['BHWR_s2_He05_MHe']), # only works for SMC metallicity!!!
            0.0,    # I simply take Eddington factor to be zero since we do not have detailed model for this phase
            0.0     # set surface H abundance to be zero (assuming H-rich is completely lost during MT)
            ]
    
    
    result = evo.cal_disk_criterion(inputs,eta0=1.0/3.0,beta=1.0,coef_w=1.3,gamma=1)
    data=support.add_Wind_fed_XRB(result,data,'BHWR','0')
    result = evo.cal_disk_criterion(inputs,eta0=1.0,beta=1.0,coef_w=1.3,gamma=1)
    data=support.add_Wind_fed_XRB(result,data,'BHWR','1')
    result = evo.cal_disk_criterion(inputs,eta0=1.0/3.0,beta=0.8,coef_w=1.3,gamma=1)
    data=support.add_Wind_fed_XRB(result,data,'BHWR','2')
    result = evo.cal_disk_criterion(inputs,eta0=1.0/3.0,beta=1.0,coef_w=1.3,gamma=1.0/6)
    data=support.add_Wind_fed_XRB(result,data,'BHWR','3')
    result = evo.cal_disk_criterion(inputs,eta0=1.0/3.0,beta=1.0,coef_w=1.3,gamma=3.0/2)
    data=support.add_Wind_fed_XRB(result,data,'BHWR','4')
    
    make_pdf_report.write_HMXB(data)
    
    # -------------------------------------------------------
    
if  data['Wind_fed_BHHMXB']:
    make_pdf_report.write_summary_with_HMXB(data)
else:
    make_pdf_report.write_summary(data)

if data['open_pdf_report_after_calculation']:
    os.system(data['open_pdf_cmd']+' main.pdf &')

os.chdir(data['home_path'])
if not os.path.exists(data['output']):
    os.mkdir(data['output'])


#temp=data['output']+'/'+data['file_name']+'%.3f_%.3f_%.3f' % (data['lgm1i'],data['qi'],data['logpi'])
temp=data['output']+'/'+work_dir.strip('/')
if not overwrite_mode:
    while os.path.exists(temp+'/'):
        temp=temp+'_new'
else:
    if os.path.exists(temp+'/'):
        os.system('rm -r '+temp)
os.system('mv '+work_dir+'/ '+temp+'/')
os.system('mv '+work_dir.strip('/')+'.pdf '+data['output']+'/')

#os.system('mv '+data['file_name']+'%.3f_%.3f_%.3f/' % (data['lgm1i'],data['qi'],data['logpi'])+ '  '+temp+'/')
#os.system('mv '+data['file_name']+'%.3f_%.3f_%.3f.pdf' % (data['lgm1i'],data['qi'],data['logpi'])+ '  '+temp+'.pdf')

#os.system('mv '+data['file_name']+'%.3f_%.3f_%.3f/' % (data['lgm1i'],data['qi'],data['logpi'])+ '  '+data['output'])
#os.system('mv '+data['file_name']+'%.3f_%.3f_%.3f.pdf' % (data['lgm1i'],data['qi'],data['logpi'])+ '  '+data['output'])
#print data['home_path']
#print os.getcwd() 
    
    
    

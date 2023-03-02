import argparse
import os
import subprocess

figure_template=r'''
\begin{figure}
\centering
\includegraphics[width=\linewidth]{%s}
\end{figure}
'''


def write_summary(data):
    fp=open('main.tex','w')
    fp0=open('../tex_template/main_template.tex','r')

    for line in fp0:
        fp.write(line)
    fp.close()
    fp0.close()


    cmd = ['pdflatex', '-interaction', 'nonstopmode', 'main.tex']

    proc = subprocess.Popen(cmd,stdout=subprocess.PIPE)
    print('save '+cmd[-1].strip('\.tex'))
    proc.communicate()

    os.system('cp main.pdf ../%s%.3f_%.3f_%.3f.pdf' % (data['file_name'],data['lgm1i'],data['qi'],data['logpi']))
    print('cp main.pdf ../%s%.3f_%.3f_%.3f.pdf' % (data['file_name'],data['lgm1i'],data['qi'],data['logpi']))

def write_summary_with_HMXB(data):
    fp=open('main.tex','w')
    fp0=open('../tex_template/main_with_HMXB_template.tex','r')

    for line in fp0:
        fp.write(line)
    fp.close()
    fp0.close()


    cmd = ['pdflatex', '-interaction', 'nonstopmode', 'main.tex']

    proc = subprocess.Popen(cmd,stdout=subprocess.PIPE)
    #print('save '+os.getcwd()+'/'+cmd[-1])
    print('save '+cmd[-1].strip('\.tex'))
    proc.communicate()

    os.system('cp main.pdf ../%s%.3f_%.3f_%.3f.pdf' % (data['file_name'],data['lgm1i'],data['qi'],data['logpi']))
    print('cp main.pdf ../%s%.3f_%.3f_%.3f.pdf' % (data['file_name'],data['lgm1i'],data['qi'],data['logpi']))

def write_He_OB(data):
    fp=open('He_OB.tex','w')
    fp0=open('../tex_template/He_OB_template.tex','r')

    end_line=''
    if data['HeOB_vsini']:
        fig1=figure_template % 'HeOB_fig1'
        fig2=figure_template % 'HeOB_fig2'
        end_line=end_line+fig1+fig2+'\n\end{document}'

    for line in fp0:

        if "log M$_{\\rm 1,i}$ = %.3f (M$_{\\rm 1,i}$=%.3f Msun)" in line:
            fp.write(line % (data['lgm1i'],data['m1i']))
        elif "M$_{\\rm 2,i}$ = %.3f Msun ($q_{\\rm i}$= %.3f)" in line:
            fp.write(line % (data['m2i'],data['qi']))
        elif "log P$_{\\rm orb,i}$ = %.3f (P$_{\\rm orb,i}= %.3f$ days)" in line:
            fp.write(line % (data['logpi'],data['porbi']))
        elif "Age at the middle of the core He burning of primary: %.3f Myrs" in line:
            fp.write(line % (data['HeOB_age_He05']/1e6))
        elif "lifetime of He + OB phase: %.3f Myrs" in line:
            fp.write(line % (data['HeOB_lifetime']/1e6))
        elif "{HeOB_" in line:
            try:
                fp.write(line.format(**data))
            except:
                print(line)
        elif "end{document}" in line and data['HeOB_vsini']:
            fp.write(end_line)
        else:
            fp.write(line)
    fp.close()
    fp0.close()

    cmd = ['pdflatex', '-interaction', 'nonstopmode', 'He_OB.tex']
    proc = subprocess.Popen(cmd,stdout=subprocess.PIPE)
    #print('save '+os.getcwd()+'/'+cmd[-1])
    print('save '+cmd[-1].strip('\.tex'))
    proc.communicate()


def write_BHNS_OB(data):
    fp=open('BHNS_OB.tex','w')
    fp0=open('../tex_template/BHNS_OB_template.tex','r')

#    end_line=''
#    if data['HeOB_vsini']:
#        fig1=figure_template % 'HeOB_fig1'
#        fig2=figure_template % 'HeOB_fig2'
#        end_line=end_line+fig1+fig2+'\n\end{document}'

    for line in fp0:

        if "log M$_{\\rm 1,i}$ = %.3f (M$_{\\rm 1,i}$=%.3f Msun)" in line:
            fp.write(line % (data['lgm1i'],data['m1i']))
        elif "M$_{\\rm 2,i}$ = %.3f Msun ($q_{\\rm i}$= %.3f)" in line:
            fp.write(line % (data['m2i'],data['qi']))
        elif "log P$_{\\rm orb,i}$ = %.3f (P$_{\\rm orb,i}= %.3f$ days)" in line:
            fp.write(line % (data['logpi'],data['porbi']))
        elif "Age at the core He depletiopn of primary: %.3f Myrs" in line:
            fp.write(line % (data['BHOB_age_He00']/1e6))
        elif "lifetime of BH/NS + OB phase: %.3f Myrs" in line:
            fp.write(line % (data['BHOB_lifetime']/1e6))
        elif "{BHOB_" in line:
            fp.write(line.format(**data))
        elif "{BH_mass_" in line:
            fp.write(line.format(**data))
#        elif "end{document}" in line and data['HeOB_vsini']:
#            fp.write(end_line)
        else:
            fp.write(line)
    fp.close()
    fp0.close()

    cmd = ['pdflatex', '-interaction', 'nonstopmode', 'BHNS_OB.tex']
    proc = subprocess.Popen(cmd,stdout=subprocess.PIPE)
    #print('save '+os.getcwd()+'/'+cmd[-1])
    print('save '+cmd[-1].strip('\.tex'))
    proc.communicate()


def write_BHNS_He(data):
    fp=open('BHNS_WR.tex','w')
    fp0=open('../tex_template/BHNS_WR_template.tex','r')

#    end_line=''
#    if data['HeOB_vsini']:
#        fig1=figure_template % 'HeOB_fig1'
#        fig2=figure_template % 'HeOB_fig2'
#        end_line=end_line+fig1+fig2+'\n\end{document}'

    for line in fp0:

        if "log M$_{\\rm 1,i}$ = %.3f (M$_{\\rm 1,i}$=%.3f Msun)" in line:
            fp.write(line % (data['lgm1i'],data['m1i']))
        elif "M$_{\\rm 2,i}$ = %.3f Msun ($q_{\\rm i}$= %.3f)" in line:
            fp.write(line % (data['m2i'],data['qi']))
        elif "log P$_{\\rm orb,i}$ = %.3f (P$_{\\rm orb,i}= %.3f$ days)" in line:
            fp.write(line % (data['logpi'],data['porbi']))
        elif "Age at the middle of core He burning of secondary:" in line:
            fp.write(line % (data['BHWR_He05_age']/1e6))
        elif "lifetime of BH/NS + He phase: %.3f Myrs" in line:
            fp.write(line % (data['BHWR_lifetime']/1e6))
        elif "{BHWR_" in line:
            fp.write(line.format(**data))
#        elif "end{document}" in line and data['HeOB_vsini']:
#            fp.write(end_line)
        else:
            fp.write(line)
    fp.close()
    fp0.close()

    cmd = ['pdflatex', '-interaction', 'nonstopmode', 'BHNS_WR.tex']
    proc = subprocess.Popen(cmd,stdout=subprocess.PIPE)
    #print('save '+os.getcwd()+'/'+cmd[-1])
    print('save '+cmd[-1].strip('\.tex'))
    proc.communicate()

def write_BHBH(data):
    fp=open('BHBH.tex','w')
    fp0=open('../tex_template/BHBH_template.tex','r')


    for line in fp0:

        if "log M$_{\\rm 1,i}$ = %.3f (M$_{\\rm 1,i}$=%.3f Msun)" in line:
            fp.write(line % (data['lgm1i'],data['m1i']))
        elif "M$_{\\rm 2,i}$ = %.3f Msun ($q_{\\rm i}$= %.3f)" in line:
            fp.write(line % (data['m2i'],data['qi']))
        elif "log P$_{\\rm orb,i}$ = %.3f (P$_{\\rm orb,i}= %.3f$ days)" in line:
            fp.write(line % (data['logpi'],data['porbi']))
        elif "{BBH_" in line:
            fp.write(line.format(**data))
#        elif "end{document}" in line and data['HeOB_vsini']:
#            fp.write(end_line)
        else:
            fp.write(line)
    fp.close()
    fp0.close()

    cmd = ['pdflatex', '-interaction', 'nonstopmode', 'BHBH.tex']
    proc = subprocess.Popen(cmd,stdout=subprocess.PIPE)
    #print('save '+os.getcwd()+'/'+cmd[-1])
    print('save '+cmd[-1].strip('\.tex'))
    proc.communicate()

def write_HMXB(data):
    fp=open('HMXB.tex','w')
    fp0=open('../tex_template/HMXB_template.tex','r')


    for line in fp0:

        if "log M$_{\\rm 1,i}$ = %.3f (M$_{\\rm 1,i}$=%.3f Msun)" in line:
            fp.write(line % (data['lgm1i'],data['m1i']))
        elif "M$_{\\rm 2,i}$ = %.3f Msun ($q_{\\rm i}$= %.3f)" in line:
            fp.write(line % (data['m2i'],data['qi']))
        elif "log P$_{\\rm orb,i}$ = %.3f (P$_{\\rm orb,i}= %.3f$ days)" in line:
            fp.write(line % (data['logpi'],data['porbi']))
        elif "{BHOB_" in line:
            try:
                fp.write(line.format(**data))
            except:
                print('wrong with',line)
        elif "{BHWR_" in line:
            fp.write(line.format(**data))
#        elif "end{document}" in line and data['HeOB_vsini']:
#            fp.write(end_line)
        else:
            fp.write(line)
    fp.close()
    fp0.close()

    cmd = ['pdflatex', '-interaction', 'nonstopmode', 'HMXB.tex']
    proc = subprocess.Popen(cmd,stdout=subprocess.PIPE)
    #print('save '+os.getcwd()+'/'+cmd[-1])
    print('save '+cmd[-1].strip('\.tex'))
    proc.communicate()

def write_info(data):
    fp=open('info.tex','w')
    fp0=open('../tex_template/info_template.tex','r')


    for line in fp0:

        if "log M$_{\\rm 1,i}$ = %.3f (M$_{\\rm 1,i}$=%.3f Msun)" in line:
            fp.write(line % (data['lgm1i'],data['m1i']))
        elif "M$_{\\rm 2,i}$ = %.3f Msun ($q_{\\rm i}$= %.3f)" in line:
            fp.write(line % (data['m2i'],data['qi']))
        elif "log P$_{\\rm orb,i}$ = %.3f (P$_{\\rm orb,i}= %.3f$ days)" in line:
            fp.write(line % (data['logpi'],data['porbi']))
        elif "{summary_file" in line:
            try:
                fp.write(line.format(**data))
            except:
                print('wrong with',line)
        elif "{Rbirth_" in line:
            fp.write(line.format(**data))
        elif "{model_path}" in line:
            fp.write(line.format(**data))
#        elif "end{document}" in line and data['HeOB_vsini']:
#            fp.write(end_line)
        else:
            fp.write(line)
    fp.close()
    fp0.close()

    cmd = ['pdflatex', '-interaction', 'nonstopmode', 'info.tex']
    proc = subprocess.Popen(cmd,stdout=subprocess.PIPE)
    #print('save '+os.getcwd()+'/'+cmd[-1])
    print('save '+cmd[-1].strip('\.tex'))
    proc.communicate()



























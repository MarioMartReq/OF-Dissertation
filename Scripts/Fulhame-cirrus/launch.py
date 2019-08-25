import exec_foam as ex
import os
import commands

def change_two_pbs(name_dec, name_rest, list):
    first_elem=list.pop(0)
    # last_elem=list.pop(len(list)-1)

    prev_procnum=36
    

    node=first_elem
    procnum=node*36

    os.system("cp "+name_dec+".pbs "+name_dec+"-copy-"+str(node)+".pbs")

    ex.write_decomposeParDict(procnum)
    os.system("sed -i 's/total_proc="+str(prev_procnum)+"/total_proc="+str(procnum)+"/g' "+name_dec+"-copy-"+str(node)+".pbs")

    jobname=name_dec+"-job-"+str(node)
    output = commands.getoutput("qsub -N "+jobname+" "+name_dec+"-copy-"+str(node)+".pbs")
    prev_jobname=jobname

    os.system("cp "+name_rest+".pbs "+name_rest+"-copy-"+str(node)+".pbs")

    # ex.write_decomposeParDict(procnum)
    os.system("sed -i 's/total_proc="+str(prev_procnum)+"/total_proc="+str(procnum)+"/g' "+name_rest+"-copy-"+str(node)+".pbs")
    jobname=name_rest+"-job-"+str(node)
    output = commands.getoutput("qsub  -W depend=afterany:"+output+" -N "+jobname+" -l select="+str(node)+":ncpus=36 "+name_rest+"-copy-"+str(node)+".pbs")

    for elem in list:
        node=elem
        procnum=node*36

        os.system("cp "+name_dec+".pbs "+name_dec+"-copy-"+str(node)+".pbs")

        ex.write_decomposeParDict(procnum)
        os.system("sed -i 's/total_proc="+str(prev_procnum)+"/total_proc="+str(procnum)+"/g' "+name_dec+"-copy-"+str(node)+".pbs")

        jobname=name_dec+"-job-"+str(node)
        output = commands.getoutput("qsub -W depend=afterany:"+output+" -N "+jobname+" "+name_dec+"-copy-"+str(node)+".pbs")
        prev_jobname=jobname

        os.system("cp "+name_rest+".pbs "+name_rest+"-copy-"+str(node)+".pbs")

        # ex.write_decomposeParDict(procnum)
        os.system("sed -i 's/total_proc="+str(prev_procnum)+"/total_proc="+str(procnum)+"/g' "+name_rest+"-copy-"+str(node)+".pbs")
        jobname=name_rest+"-job-"+str(node)
        output = commands.getoutput("qsub  -W depend=afterany:"+output+" -N "+jobname+" -l select="+str(node)+":ncpus=36 "+name_rest+"-copy-"+str(node)+".pbs")

        prev_node=node
        prev_procnum=procnum
        prev_jobname=jobname




if __name__ == "__main__":
    list=[10,15,20]
    # list.reverse()
    change_two_pbs("foam-decompose","foam-rest",list)
    
# qsub -N job1 bla.pbs
# qsub -N job2 -hold_jib job1 bla.pbs

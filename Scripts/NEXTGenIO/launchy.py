import exec_foam as ex
import os
import commands

def changing_dictionary(name_rest_list, list_values):
    start=1
    for name_rest in name_rest_list:
        prev_val=50
        # os.system("rm "+name_rest+"-copy.sh && cp "+name_rest+".sh "+name_rest+"-copy.sh")
        os.system("cp "+name_rest+".sh "+name_rest+"-copy.sh")
        for value in list_values:
            os.system("sed -i 's/dict="+str(prev_val)+"/dict="+str(value)+"/g' "+name_rest+"-copy.sh")
            print "sustituido "+str(prev_val)+"por "+str(value)
            prev_val=value
            if(start==1):
                output = commands.getoutput("sbatch --workflow-start "+name_rest+"-copy.sh ")
                # output = commands.getoutput("sbatch --workflow-prior-dependency=11234 "+name_dec+"-copy.sh ")
                job_id=output.split("Submitted batch job ")[1]
                print "first job "+str(job_id)
                start=0
            else:
                output = commands.getoutput("sbatch --workflow-prior-dependency="+job_id+" "+name_rest+"-copy.sh ")
                job_id=output.split("Submitted batch job ")[1]
                print "first job "+str(job_id)
        
def change_two_slurm(name_dec_list, name_rest_list, list):
    start=1
# for i in range(0,len(name_dec)):
    # name_rest=name_rest_list[i]
    # name_dec=name_dec_list[i]
    name_rest=name_rest_list
    name_dec=name_dec_list
    prev_procnum=96
    prev_node=2
    # prev_method="scotch"
    os.system("rm "+name_dec+"-copy.sh && cp "+name_dec+".sh "+name_dec+"-copy.sh")
    os.system("rm "+name_rest+"-copy.sh && cp "+name_rest+".sh "+name_rest+"-copy.sh")

    # os.system("cp "+name_dec+".sh "+name_dec+"-copy.sh")
    # os.system("cp "+name_rest+".sh "+name_rest+"-copy.sh")
    for value in list:
        # for method in second_list:
        node=value
        procnum=node*48

        print "Submitting jobs for procnum: "+str(procnum)

        # ex.write_decomposeParDict(procnum,"decomposeParDict")

        os.system("sed -i 's/total_proc="+str(prev_procnum)+"/total_proc="+str(procnum)+"/g' "+name_dec+"-copy.sh")
        # os.system("sed -i 's/method='"+prev_method+"'/method="+method+"/g' "+name_dec+"-copy.sh")

        if start is 1:
            # output = commands.getoutput("sbatch --workflow-start "+name_dec+"-copy.sh ")
            output = commands.getoutput("sbatch --workflow-prior-dependency=12207 "+name_dec+"-copy.sh ")
            
            job_id=output.split("Submitted batch job ")[1]
            # print "first job "+str(job_id)
            start=0
        else:
            output = commands.getoutput("sbatch --workflow-prior-dependency="+str(job_id)+" "+name_dec+"-copy.sh ")
            job_id=output.split("Submitted batch job ")[1]
            # print "job "+str(job_id)

        os.system("sed -i 's/#SBATCH --nodes="+str(prev_node)+"/#SBATCH --nodes="+str(node)+"/g' "+name_rest+"-copy.sh")
        os.system("sed -i 's/total_proc="+str(prev_procnum)+"/total_proc="+str(procnum)+"/g' "+name_rest+"-copy.sh")
        # os.system("sed -i 's/method='"+prev_method+"'/method="+method+"/g' "+name_rest+"-copy.sh")

        output = commands.getoutput("sbatch --workflow-prior-dependency="+str(job_id)+" "+name_rest+"-copy.sh")
        job_id=output.split("Submitted batch job ")[1]

        prev_node=node
        prev_procnum=procnum
        # prev_method=method

    # for elem in list:
    #     node=elem
    #     procnum=node*48
        
    #     ex.write_decomposeParDict(procnum)

    #     os.system("sed -i 's/total_proc="+str(prev_procnum)+"/total_proc="+str(procnum)+"/g' "+name_dec+"-copy.sh")

    #     output = commands.getoutput("sbatch --workflow-prior-dependency="+str(job_id)+" "+name_dec+"-copy.sh")
    #     job_id=output.split("Submitted batch job ")[1]   

    #     os.system("sed -i 's/#SBATCH --nodes="+str(prev_node)+"/#SBATCH --nodes="+str(node)+"/g' "+name_rest+"-copy.sh")
    #     os.system("sed -i 's/total_proc="+str(prev_procnum)+"/total_proc="+str(procnum)+"/g' "+name_rest+"-copy.sh")

    #     output = commands.getoutput("sbatch --workflow-prior-dependency="+str(job_id)+" "+name_rest+"-copy.sh")
    #     job_id=output.split("Submitted batch job ")[1]

    #     prev_node=node
    #     prev_procnum=procnum

    # node=last_elem
    # procnum=node*48
    
    # ex.write_decomposeParDict(procnum)

    # os.system("sed -i 's/total_proc="+str(prev_procnum)+"/total_proc="+str(procnum)+"/g' "+name_dec+"-copy.sh")

    # output = commands.getoutput("sbatch --workflow-prior-dependency="+str(job_id)+" "+name_dec+"-copy.sh")
    # job_id=output.split("Submitted batch job ")[1]   

    # os.system("sed -i 's/#SBATCH --nodes="+str(prev_node)+"/#SBATCH --nodes="+str(node)+"/g' "+name_rest+"-copy.sh")
    # os.system("sed -i 's/total_proc="+str(prev_procnum)+"/total_proc="+str(procnum)+"/g' "+name_rest+"-copy.sh")

    # # output = commands.getoutput("sbatch --workflow-prior-dependency="+str(job_id)+" --workflow-end "+name_rest+"-copy.sh")
    # output = commands.getoutput("sbatch --workflow-prior-dependency="+str(job_id)+" "+name_rest+"-copy.sh")
    
    # job_id=output.split("Submitted batch job ")[1]

    # print "job "+job_id
    # print "Last job submitted"


def change_one_slurm(name, list):

    first_elem=list.pop(0)
    last_elem=list.pop(len(list)-1)

    prev_node=4
    prev_procnum=192

    node=first_elem
    procnum=node*48

    os.system("rm "+name+"-copy.sh && cp "+name+".sh "+name+"-copy.sh")

    write_decomposeParDict(procnum)
    os.system("sed -i 's/#SBATCH --nodes="+str(prev_node)+"/#SBATCH --nodes="+str(node)+"/g' "+name+"-copy.sh")
    os.system("sed -i 's/total_proc="+str(prev_procnum)+"/total_proc="+str(procnum)+"/g' "+name+"-copy.sh")

    # output = commands.getoutput("sbatch --workflow-start "+name+"-copy.sh ")
    output = commands.getoutput("sbatch --workflow-prior-dependency=11229 "+name+"-copy.sh ")
    job_id=output.split("Submitted batch job ")[1]
    print "first job "+str(job_id)

    prev_node=node
    prev_procnum=procnum

    for elem in list:
        node=elem
        procnum=node*48
        
        write_decomposeParDict(procnum)
        print(node)

        os.system("sed -i 's/#SBATCH --nodes="+str(prev_node)+"/#SBATCH --nodes="+str(node)+"/g' "+name+"-copy.sh")
        os.system("sed -i 's/total_proc="+str(prev_procnum)+"/total_proc="+str(procnum)+"/g' "+name+"-copy.sh")

        output = commands.getoutput("sbatch --workflow-prior-dependency="+str(job_id)+" "+name+"-copy.sh")
        job_id=output.split("Submitted batch job ")[1]
        print "job "+job_id

        prev_node=node
        prev_procnum=procnum

    node=last_elem
    procnum=node*48
    
    write_decomposeParDict(procnum)
    os.system("sed -i 's/#SBATCH --nodes="+str(prev_node)+"/#SBATCH --nodes="+str(node)+"/g' "+name+"-copy.sh")
    os.system("sed -i 's/total_proc="+str(prev_procnum)+"/total_proc="+str(procnum)+"/g' "+name+"-copy.sh")

    # output = commands.getoutput("sbatch --workflow-prior-dependency="+str(job_id)+" --workflow-end "+name+"-copy.sh")
    output = commands.getoutput("sbatch --workflow-prior-dependency="+str(job_id)+" "+name+"-copy.sh")
    job_id=output.split("Submitted batch job ")[1]
    print "job "+job_id
    print "Last job submitted"

def just_launch(sh_list):
    start=1
    for elem in sh_list:
        if start is 1:
            output = commands.getoutput("sbatch --workflow-start "+elem+".sh ")
            # output = commands.getoutput("sbatch --workflow-prior-dependency=11234 "+name_dec+"-copy.sh ")
            print output
            job_id=output.split("Submitted batch job ")[1]
            print "first job "+str(job_id)
            start=0
        else:
            output = commands.getoutput("sbatch --workflow-prior-dependency="+str(job_id)+" "+elem+".sh ")
            print output
            job_id=output.split("Submitted batch job ")[1]
            print "job "+str(job_id)


if __name__ == "__main__":
    # # name_rest_list=['foam-rest-rail-h1-IO','foam-rest-rail-IO','foam-rest-under-IO','foam-rest-gecko-IO']
    # # list_values=['100','50','25','20']
    # # changing_dictionary(name_rest_list,list_values)
    list_2lm=[8,10]
    # list_2lm.reverse()
    change_two_slurm("foam-decompose-under","foam-rest-under",list_2lm)
    

    # list=[2,4]
    # second_list=['kahip','metis']
    # change_two_slurm('foam-decompose-decomp', 'foam-rest-decomp', list,second_list)
    # "foam-rest-gecko-IO-sim"
    # sh_list=["foam-rest-under-IO-sim","foam-rest-rail-h1-IO-sim","foam-rest-rail-IO-sim"]
    # just_launch(sh_list)


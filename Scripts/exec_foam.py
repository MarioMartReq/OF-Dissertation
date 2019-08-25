import csv
import os
import numpy as np
import time
from timeit import default_timer as timer
import sys
import commands

# returns the execution time of one log. file
def extract_exec_time(filename):
    with open (filename) as f:
        lines = reversed(f.readlines())#.reverse()
        for line in lines:
            if line.startswith("ExecutionTime") or line.startswith("Finished meshing in"):
                return str(line.split("=")[1].split("s")[0].strip())
        return -1

def extract_clock_time(filename):
    with open (filename) as f:
        lines = reversed(f.readlines())#.reverse()
        for line in lines:
            if "ClockTime" in line:
                return str(line.split("ClockTime = ")[1].split("s")[0].strip())
        return -1

def get_time_for_iter(iter):
    with open("log.simpleFoam") as f:
        lines = f.readlines()
        aux = 0
        for line in lines:
            if line.startswith("Time = "+str(iter)):
                aux = 1
                continue
            if aux==1 and line.startswith("ExecutionTime"):
                return str(line.split("=")[1].split("s")[0].strip())
        return -1

def get_clock_for_iter(iter):
    with open("log.simpleFoam") as f:
        lines = f.readlines()
        aux = 0
        for line in lines:
            if line.startswith("Time = "+str(iter)):
                aux = 1
                continue
            if aux==1 and "ClockTime" in line:
                return str(line.split("ClockTime = ")[1].split("s")[0].strip())
        return -1

# picks the number of processes from log.simpleFoam
def get_num_proc():
    with open("log.simpleFoam") as f:
        lines = f.readlines()
        for line in lines:
            if "nProcs : " in line:
                return line.split('nProcs : ')[1].split("\n")[0]

def get_iter():
    with open("log.simpleFoam") as f:
        lines = f.readlines()
        invert_lines = reversed(lines)
        time_init=0
        time_final=0
        for line in lines:
            if line.startswith("Time = "):
                time_init=int(line.split('Time = ')[1].split("\n")[0])
                break
        
        for line in invert_lines:
            if line.startswith("Time = "):
                time_final=int(line.split('Time = ')[1].split("\n")[0])
                break

        return str((time_final-time_init)+1)


# counts the number of entries in specified csv
def count_rows(filename):
    with open (filename) as f:
        row_count = sum(1 for row in f)
        return row_count

# get the number of cells out of log.checkMesh
def get_num_cells():
    with open("log.checkMesh") as f:
        lines = f.readlines()
        for line in lines:
            if 'cells:            ' in line:
                return line.split('cells:            ')[1].split('\n')[0]

# function that changes the
def modify_allrun_decomposeParDict(number):
    with open("Allrun" , 'r+b') as f:
        lines = f.readlines()
        for idx, line in enumerate(lines):
            if ('decompDict="-decomposeParDict system/' in line):
                line = line.split(".")[0]+"."+str(number)+'"\n'
                lines[idx]=line
                f.seek(0, 0)
                f.truncate()
                f.write("".join(lines))
                f.close()
                return

def extract_lines(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
        f.close()
    return lines

def substitute_lines(filename, lines):
    with open(filename, 'r+b') as f:
        f.writelines(lines)
        f.close()

# this requires the spefecied line to contain a point between the filenam  and the number of processes
def read_allrun_decomposeParDict():
    with open("Allrun",'rt') as f:
        lines = f.readlines()
        for line in lines:
            if 'decompDict="-decomposeParDict system/' in line:
                return line.split('.')[1].split('"')[0]

# if the decomposepardict exists, it is deleted and substituted with the new one.
# it creates new files from a template decomposepardict
def write_decomposeParDict(number,orig=None):
    number=str(number)
    if orig is None:
        orig="decomposeParDict"
    if os.path.isfile("/system/"+orig+"."+number):
        os.system("rm -f system/"+orig+"."+number)

    os.system("cp system/"+orig+" system/"+orig+"."+number)
    modify_file(orig+"."+number, "numberOfSubdomains", str(number))

# modifies file filename, changing variable to the specified value
# if line_number is provided, it will modify that specific line
def modify_file(filename, variable, value,line_number=None):
    with open("system/"+filename , 'r+b') as f:
        lines = f.readlines()

        newline=None
        print line_number
        if line_number is None:
            for idx, line in enumerate(lines):
                if variable in line and "//" not in line:
                    newline = line.split(variable + " ")[0]+variable+" "+str(value)+";\n"
                    lines[idx]=newline
                    break
        else:
            line_number-=1
            newline = lines[line_number].split(variable + " ")[0]+variable+" "+str(value)+";\n"
            lines[line_number]=newline

        if newline is None:
            return -1
        else:
            print("File modified. Variable '"+variable+"' set up as '"+str(value)+"'")
            f.seek(0, 0)
            f.truncate()
            f.write("".join(lines))
            f.close()
            return
    return -1

def pick_info(iter,name=None,comment=None):
    print("\nCollecting execution info for "+str(iter)+"iterations\n\n")
    if (name==None):
        filenamecsv = 'collected_info_under.csv'
    else:
        filenamecsv=name+'.csv'
    with open (filenamecsv, 'a') as table:
        row_count = count_rows(filenamecsv)
        first_line="Number,procNum,simpleFoam,simpleFoamClock,totalsimpleFoam,totalsimpleFoamClock,potentialFoam,combineP+S,NumberIter,IterFrom,sec/iter,clock/iter,Comment"
        # Counting the number of experiments.
        if row_count==0:
            another_line = "1"
        else:
            another_line = str(row_count)
        
        if iter is None:
            time_simple=extract_exec_time("log.simpleFoam")
            num_iter=get_iter()
            iterfrom="0"
        else:
            num_iter=str(iter)
            iterfrom=str(int(get_iter())-iter)
            time_simple=str(float(extract_exec_time("log.simpleFoam"))-float(get_time_for_iter(int(iterfrom))))
            clock_simple=str(int(extract_clock_time("log.simpleFoam"))-int(get_clock_for_iter(int(iterfrom))))
            time_simple_total=extract_exec_time("log.simpleFoam")
            clock_total=extract_clock_time("log.simpleFoam")

        
        # total execution time, number of proc used and number of cells
        another_line+=','+get_num_proc()+','+time_simple+','+clock_simple+','+time_simple_total+','+clock_total

        # adding execution times for pontetialFoam and simpleFoam. If more variables wanted to be added,
        # this is when it should be done
        another_line+=','+extract_exec_time("log.potentialFoam")+','+str(float(extract_exec_time("log.potentialFoam"))+ float(extract_exec_time("log.simpleFoam")))+','+num_iter+','+iterfrom
        another_line+=','+str(float(time_simple)/float(num_iter))+','+str(float(clock_simple)/float(num_iter))+','
        if comment==None:
            another_line+='""'
        else:
            another_line+='"'+comment+'"'
        
        if row_count==0:
            table.write(first_line)
        table.write("\n"+another_line)
    print("\nCSV file modified/created")

# excutes without arguments, recording info contained in various log files
def execution_raw():
    print("\nBegining execution\n\n")
    os.system("./Allclean")
    start = timer()
    os.system("./Allrun")
    end = timer()
    measured = end-start
    measured = "%.4f" % measured
    print("\n\n Execution ended. Measured time: " +measured)

    filenamecsv = 'default_exec.csv'
    with open (filenamecsv, 'a') as table:
        row_count = count_rows(filenamecsv)
        first_line="Number,MeasuredTime,procNum,numCells,potentialFoam,simpleFoam,combineP+S,snappyHexMesh,Comment"
        # Counting the number of experiments.
        if row_count==0:
            another_line = "1"
        else:
            another_line = str(row_count)

        # total execution time, number of proc used and number of cells
        another_line+=','+measured+','+read_allrun_decomposeParDict()+','+get_num_cells()

        # adding execution times for potetialFoam and simpleFoam. If more variables wanted to be added,
        # this is when it should be done
        another_line+=','+extract_exec_time("log.potentialFoam")+','+extract_exec_time("log.simpleFoam")+','+str(float(extract_exec_time("log.potentialFoam"))+ float(extract_exec_time("log.simpleFoam")))+','+extract_exec_time("log.snappyHexMesh")+',""'

        if row_count==0:
            table.write(first_line)
        table.write("\n"+another_line)
    print("\nCSV file modified/created")


# the idea behind this function is that it will invoque the modification of the function
# and then clean and execute the foam experiment. After completition, it will record the excution time
# of the whole execution, simple and potential foam, and what have been modified in for this execution.
# the variables message, line and decomp are optional

# message = if none, the csv message field will be left blank
# line =  if specified, it will modified an specific line number
# decomp=-1 implies that the parameter that is going to be changed is not in allrun. other number means that allrun is going to be changed


def exec_with_modification(output_filename,filename, variable, value, message=None,line=None,decomp=-1):
    print("\nCleaning and begining execution\n")
    print("Printing to "+output_filename+".csv. Changes to "+filename+" , variable: '"+variable+"', value: "+str(value)+"\n\n")
    if decomp is -1:
        default_lines = extract_lines("system/"+filename)
        if modify_file(filename, variable, value, line) is -1:
            print "Error modifying the file. It does not exist or the variable cannot be found."
            return 1
        substitute_lines("system/"+filename, default_lines)
    else:
        # default_lines = extract_lines("system/"+filename)
        modify_allrun_decomposeParDict(decomp)
        # substitute_lines("system/"+filename, default_lines)

    os.system("./Allclean")
    start = timer()
    os.system("./Allrun")
    end = timer()
    measured = end-start
    measured = "%.4f" % measured
    print("\n\n Execution ended. Measured total time: " +measured)

    with open (output_filename+'.csv', 'a') as table:
        row_count = count_rows(output_filename+'.csv')
        first_line="Number,Message,MeasuredTime,procNum,numCells,potentialFoam,simpleFoam,combineP+S,snappyHexMesh,fileModified,Variable,newValue"
        # Counting the number of experiments.
        if row_count==0:
            another_line = "1"
        else:
            another_line = str(row_count)

        # If no message was provided, won't write anything
        if message is None:
            another_line+=','
        else:
            another_line+=',"'+message+'"'

        # total execution time, number of proc used and number of cells
        another_line+=','+measured+','+read_allrun_decomposeParDict()+','+get_num_cells()

        # adding execution times for potetialFoam and simpleFoam. If more variables wanted to be added,
        # this is when it should be done
        another_line+=','+extract_exec_time("log.potentialFoam")+','+extract_exec_time("log.simpleFoam")+','+str(float(extract_exec_time("log.potentialFoam"))+ float(extract_exec_time("log.simpleFoam")))+','+extract_exec_time("log.snappyHexMesh")

        # variables modified for in this execution
        another_line+=','+filename+','+variable+',"'+str(value)+'"'
        if row_count==0:
            table.write(first_line)
        table.write("\n"+another_line)
    print("\nCSV file modified/created")



def main():
    os.system("rm foam-queue-copy.sh && cp foam-queue.sh foam-queue-copy.sh")
    list=(14,12,10,8,6,4,2,1)
    prev_node=4
    prev_procnum=192
    # prev_decompDict='decompDict="-decomposeParDict system/decomposeParDict.{}"'.format(prev_procnum)
    prev_decompDict="system/decomposeParDict.192"
    for elem in list:
        procnum=48*elem
        node=elem
        # decompDict='decompDict="-decomposeParDict system/decomposeParDict.{}"'.format(procnum)
        decompDict="system/decomposeParDict."+str(procnum)
        # os.system("sed -i 's/#SBATCH --nodes="+str(prev_node)+"/#SBATCH --nodes="+str(node)+"/g' foam-queue-copy.sh")
        os.system("sed -i 's/total_proc="+str(prev_procnum)+"/total_proc="+str(procnum)+"/g' foam-queue-copy.sh")
        # os.system("sed -i 's/decomposeParDict."+str(prev_procnum)+"/decomposeParDict."+str(procnum)+"/g' foam-queue-copy.sh")
        write_decomposeParDict(procnum)
        print(node)
        os.system("sbatch foam-queue-copy.sh")
        prev_node=node
        prev_procnum=procnum
        prev_decompDict=decompDict

def workflow():
    os.system("rm foam-decompose-copy.sh && cp foam-decompose.sh foam-decompose-copy.sh")
    os.system("rm foam-rest-copy.sh && cp foam-rest.sh foam-rest-copy.sh")

    output = commands.getoutput("sbatch --workflow-start foam-decompose-copy.sh ")
    job_id=output.split("Submitted batch job ")[1]
    print "first job "+str(job_id)

    output = commands.getoutput("sbatch --workflow-prior-dependency="+str(job_id)+" foam-rest-copy.sh")
    job_id=output.split("Submitted batch job ")[1]
    print "job "+job_id
    list=(12,10,8,6,4,2)
    prev_node=14
    prev_procnum=672

    for elem in list:
        procnum=48*elem
        node=elem
        
        write_decomposeParDict(procnum)
        print(node)

        os.system("sed -i 's/total_proc="+str(prev_procnum)+"/total_proc="+str(procnum)+"/g' foam-decompose-copy.sh")

        os.system("sed -i 's/#SBATCH --nodes="+str(prev_node)+"/#SBATCH --nodes="+str(node)+"/g' foam-rest-copy.sh")
        os.system("sed -i 's/total_proc="+str(prev_procnum)+"/total_proc="+str(procnum)+"/g' foam-rest-copy.sh")

        output = commands.getoutput("sbatch --workflow-prior-dependency="+str(job_id)+" foam-decompose-copy.sh")
        job_id=output.split("Submitted batch job ")[1]
        print "job "+job_id

        output = commands.getoutput("sbatch --workflow-prior-dependency="+str(job_id)+" foam-rest-copy.sh")
        job_id=output.split("Submitted batch job ")[1]
        print "job "+job_id

        prev_node=node
        prev_procnum=procnum

    procnum=48*1
    node=1
    
    write_decomposeParDict(procnum)
    print(node)

    os.system("sed -i 's/total_proc="+str(prev_procnum)+"/total_proc="+str(procnum)+"/g' foam-decompose-copy.sh")

    os.system("sed -i 's/#SBATCH --nodes="+str(prev_node)+"/#SBATCH --nodes="+str(node)+"/g' foam-rest-copy.sh")
    os.system("sed -i 's/total_proc="+str(prev_procnum)+"/total_proc="+str(procnum)+"/g' foam-rest-copy.sh")

    output = commands.getoutput("sbatch --workflow-prior-dependency="+str(job_id)+" foam-decompose-copy.sh")
    job_id=output.split("Submitted batch job ")[1]
    print "job "+job_id
    output = commands.getoutput("sbatch --workflow-prior-dependency="+str(job_id)+" --workflow-end foam-rest-copy.sh")
    job_id=output.split("Submitted batch job ")[1]
    print "job "+job_id

def underpopulating():
    num_nodes=22

    prev=1
    accum_left=0
    accum_right=0

    ppn=48
    prev_output="0-47"
    prev_ppn=48
    prev_num_proc=ppn*num_nodes

    write_decomposeParDict(prev_num_proc)

    os.system("rm foam-decompose-under-copy.sh && cp foam-decompose-under.sh foam-decompose-under-copy.sh")
    os.system("rm foam-rest-under-copy.sh && cp foam-rest-under.sh foam-rest-under-copy.sh")

    output = commands.getoutput("sbatch --workflow-start empty.sh ")
    job_id=output.split("Submitted batch job ")[1]
    print "first job: empty "+str(job_id)
    # output = commands.getoutput("sbatch --workflow-start foam-decompose-under-copy.sh ")
    # job_id=output.split("Submitted batch job ")[1]
    # print "first job "+str(job_id)

    # output = commands.getoutput("sbatch --workflow-prior-dependency="+str(job_id)+" foam-rest-under-copy.sh")
    # job_id=output.split("Submitted batch job ")[1]

    
    
    print "numproc: {}, proc:{}".format(prev_num_proc,prev_output)
    for i in range(0,20):
        ppn-=2
        num_proc=ppn*num_nodes
        if prev==1:
            prev=0
            accum_right+=1 
        else:
            prev=1
            accum_left+=1 
        
        output=("0-"+str(11-accum_left)+",12-"+str(23-accum_right)+",24-"+str(35-accum_left)+",36-"+str(47-accum_right))

        print "ppn: {}, proc:{}".format(num_proc,output)

        os.system("sed -i 's/total_proc="+str(prev_num_proc)+"/total_proc="+str(num_proc)+"/g' foam-decompose-under-copy.sh")

        os.system("sed -i 's/total_proc="+str(prev_num_proc)+"/total_proc="+str(num_proc)+"/g' foam-rest-under-copy.sh")
        os.system("sed -i 's/ppn="+str(prev_ppn)+"/ppn="+str(ppn)+"/g' foam-rest-under-copy.sh")
        os.system("sed -i 's/I_MPI_PIN_PROCESSOR_LIST="+str(prev_output)+"/I_MPI_PIN_PROCESSOR_LIST="+str(output)+"/g' foam-rest-under-copy.sh")
        os.system("sed -i 's/--tasks-per-node="+str(prev_ppn)+"/--tasks-per-node="+str(ppn)+"/g' foam-rest-under-copy.sh")
        
        write_decomposeParDict(num_proc)

        output = commands.getoutput("sbatch --workflow-prior-dependency="+str(job_id)+" foam-decompose-under-copy.sh")
        job_id=output.split("Submitted batch job ")[1]
        print "job "+job_id

        output = commands.getoutput("sbatch --workflow-prior-dependency="+str(job_id)+" foam-rest-under-copy.sh")
        job_id=output.split("Submitted batch job ")[1]
        print "job "+job_id

        prev_output=output
        prev_ppn=ppn
        prev_num_proc=num_proc
        

    ppn=6
    num_proc=ppn*num_nodes
    output="0-1,12,24-25,36"
    print "numproc: {}, proc:{}".format(num_proc,output)
    os.system("sed -i 's/total_proc="+str(prev_num_proc)+"/total_proc="+str(num_proc)+"/g' foam-decompose-under-copy.sh")

    os.system("sed -i 's/total_proc="+str(prev_num_proc)+"/total_proc="+str(num_proc)+"/g' foam-rest-under-copy.sh")
    os.system("sed -i 's/ppn="+str(prev_ppn)+"/ppn="+str(ppn)+"/g' foam-rest-under-copy.sh")
    os.system("sed -i 's/I_MPI_PIN_PROCESSOR_LIST="+str(prev_output)+"/I_MPI_PIN_PROCESSOR_LIST="+str(output)+"/g' foam-rest-under-copy.sh")
    os.system("sed -i 's/--tasks-per-node="+str(prev_ppn)+"/--tasks-per-node="+str(ppn)+"/g' foam-rest-under-copy.sh")

    write_decomposeParDict(num_proc)
    output = commands.getoutput("sbatch --workflow-prior-dependency="+str(job_id)+" foam-decompose-under-copy.sh")
    job_id=output.split("Submitted batch job ")[1]
    print "job "+job_id

    output = commands.getoutput("sbatch --workflow-prior-dependency="+str(job_id)+" foam-rest-under-copy.sh")
    job_id=output.split("Submitted batch job ")[1]
    print "job "+job_id

    prev_output=output
    prev_ppn=ppn
    prev_num_proc=num_proc


    ppn=4
    num_proc=ppn*num_nodes
    output="0,12,24,36"
    print "numproc: {}, proc:{}".format(num_proc,output)
    os.system("sed -i 's/total_proc="+str(prev_num_proc)+"/total_proc="+str(num_proc)+"/g' foam-decompose-under-copy.sh")

    os.system("sed -i 's/total_proc="+str(prev_num_proc)+"/total_proc="+str(num_proc)+"/g' foam-rest-under-copy.sh")
    os.system("sed -i 's/ppn="+str(prev_ppn)+"/ppn="+str(ppn)+"/g' foam-rest-under-copy.sh")
    os.system("sed -i 's/I_MPI_PIN_PROCESSOR_LIST="+str(prev_output)+"/I_MPI_PIN_PROCESSOR_LIST="+str(output)+"/g' foam-rest-under-copy.sh")
    os.system("sed -i 's/--tasks-per-node="+str(prev_ppn)+"/--tasks-per-node="+str(ppn)+"/g' foam-rest-under-copy.sh")

    write_decomposeParDict(num_proc)
    output = commands.getoutput("sbatch --workflow-prior-dependency="+str(job_id)+" foam-decompose-under-copy.sh")
    job_id=output.split("Submitted batch job ")[1]
    print "job "+job_id

    output = commands.getoutput("sbatch --workflow-prior-dependency="+str(job_id)+" foam-rest-under-copy.sh")
    job_id=output.split("Submitted batch job ")[1]
    print "job "+job_id

    prev_output=output
    prev_ppn=ppn
    prev_num_proc=num_proc
    
    ppn=2
    num_proc=ppn*num_nodes
    output="0,24"
    print "numproc: {}, proc:{}".format(num_proc,output)
    os.system("sed -i 's/total_proc="+str(prev_num_proc)+"/total_proc="+str(num_proc)+"/g' foam-decompose-under-copy.sh")

    os.system("sed -i 's/total_proc="+str(prev_num_proc)+"/total_proc="+str(num_proc)+"/g' foam-rest-under-copy.sh")
    os.system("sed -i 's/ppn="+str(prev_ppn)+"/ppn="+str(ppn)+"/g' foam-rest-under-copy.sh")
    os.system("sed -i 's/I_MPI_PIN_PROCESSOR_LIST="+str(prev_output)+"/I_MPI_PIN_PROCESSOR_LIST="+str(output)+"/g' foam-rest-under-copy.sh")
    os.system("sed -i 's/--tasks-per-node="+str(prev_ppn)+"/--tasks-per-node="+str(ppn)+"/g' foam-rest-under-copy.sh")
    
    write_decomposeParDict(num_proc)
    output = commands.getoutput("sbatch --workflow-prior-dependency="+str(job_id)+" foam-decompose-under-copy.sh")
    job_id=output.split("Submitted batch job ")[1]
    print "job "+job_id

    output = commands.getoutput("sbatch --workflow-prior-dependency="+str(job_id)+" --workflow-end foam-rest-under-copy.sh")
    job_id=output.split("Submitted batch job ")[1]
    print "job "+job_id

    prev_output=output
    prev_ppn=ppn
    prev_num_proc=num_proc

# instructions
if __name__ == "__main__":
    # main()
    # workflow()
    # underpopulating()
    # list=[1,2,4,6,8,10,12,14,16,18,20,22]
    # change_one_slurm("foam-rest-gecko",list)
    list=[2,4,6,8,10,]
    list_2lm=[2,4,6,8,10,12,14,16]
    list_2lm.reverse()
    # list=[12,14,16,18,20,22]
    list.reverse()
    # change_one_slurm("foam-rest-gecko",list)
    # change_two_slurm("foam-decompose-rail-h1","foam-rest-rail-h1",list)
    # change_two_slurm("foam-decompose-rail","foam-rest-rail",list)
   
import csv
import os
import numpy as np
from timeit import default_timer as timer

# returns the execution time of one log. file
def extract_exec_time(filename):
    with open (filename) as f:
        lines = reversed(f.readlines())#.reverse()
        for line in lines:
            if line.startswith("ExecutionTime") or line.startswith("Finished meshing in"):
                return str(line.split("=")[1].split("s")[0].strip())
        return -1


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
        os.system("rm -f sytem/"+orig+"."+number)

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
    filename_csv = "exec.csv"

    with open (filename_csv, 'a') as table:
        row_count = count_rows(filename_csv)

        #decomposeParDict
        decomp = 6 # default
        decomp = decomposeParDict()
        # print decomp
        info = execinfo()
        # for case in info:
        #     print case

        first_line="Number,MeasuredTime,decomp"
        if row_count==0:
            another_line = "1"
        else:
            another_line = str(row_count)

        another_line=another_line+","+measured+","+str(decomp)

        for inf in info:
            first_line=first_line+","+inf[0]
            another_line=another_line+","+inf[1]

        files = [filename for filename in os.listdir('.') if filename.startswith("log")]
        auxtime=0
        for file in files:
            # print file
            time = extractExecTime(file)
            # print time
            if time!=-1:
                if row_count == 0:
                    first_line=first_line+","+file.split(".")[1]
                time = time.replace(" ","")
                another_line=another_line+","+time
                auxtime=auxtime+float(time)
        if row_count==0:
            table.write(first_line+",readtime")
        table.write("\n"+another_line+","+str(auxtime))
        print another_line
    print("\nCSV file modified/created")


# the idea behind this function is that it will invoque the modification of the function
# and then clean and execute the foam experiment. After completition, it will record the excution time 
# of the whole execution, simple and potential foam, and what have been modified in for this execution. 
# the variables message, line and decomp are optional
def exec_with_modification(output_filename,filename, variable, value, message=None,line=None,decomp=-1):
    print("\nCleaning and begining execution\n")
    print("Printing to "+output_filename+".csv. Changes to "+filename+" , variable: '"+variable+"', value: "+str(value)+"\n\n")
    if decomp is -1:
        if modify_file(filename, variable, value) is -1:
            print "Error modifying the file. It does not exist or the variable cannot be found."
            return 1
    else:
        modify_allrun_decomposeParDict(decomp)
    
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
    # exec_with_modification(output_filename,filename, variable, value, message=None,line=None,decomp=-1)
    print ("hi")
    # for i in range(6,26,2):
    #     exec_with_modification("orig_proc_number","allrun","decomposeParDict",i,"Experiment with original meshing testing more procs",None,i)

if __name__ == "__main__":
    main()
    
import csv
import os
from timeit import default_timer as timer


""""
os.system("./Allclean")
start = time.time()
os.system("./Allrun")
end = time.time()
print("Measured time: %s" %(time.time()-start))
"""

def decomposeParDict():
    with open("Allrun") as f:
        lines = f.readlines()
        for line in lines:
            if line.startswith("decompDict"):
                numberelem = line.split(".")[1].split('"')[0]
                return numberelem

#       0          1         2       3       4       5         6             7           8           9           10              11              12          13              14
# application startFrom startTime stopAt endTime deltaT writeControl writeInterval purgeWrite writeFormat writePrecision writeCompression timeFormat timePrecision runTimeModifiable

def execinfo():
    stuff = []
    with open ("system/controlDict") as f:
        lines = f.readlines()
        begin_info = 0
        for line in lines:
            if line.startswith("functions"):
                return stuff
            elif begin_info == 1 and len(line.strip()) >= 3:
                stuff.append([line.split(" ")[0], line.split(";")[0].split(" ")[-1]])
                # print line.split(" ")[0]
                # print line.split(";")[0].split(" ")[-1]
            elif line.startswith("// * * * * *"):
                begin_info = 1


def extractExecTime(filename):
    with open (filename) as f:
        lines = reversed(f.readlines())#.reverse()
        for line in lines:
            if line.startswith("ExecutionTime"):
                return line.split("=")[1].split("s")[0]
        return -1

def count_rows(filename):
    with open (filename) as f:
        row_count = sum(1 for row in f)
        return row_count


def main():
    print(" Begining execution\n\n")
    os.system("./Allclean")
    start = timer()
    os.system("./Allrun")
    end = timer()
    measured = end-start
    print("\n\n Execution ended. Measured time: %s\n" %measured)
    filename_csv = "exec.csv"

    with open (filename_csv, 'a') as table:
        measured = 0
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

        another_line=another_line+","+str(measured)+","+str(decomp)

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
            table.write(first_line+",readtime\n")
        table.write(another_line+","+str(auxtime)+"\n")

    print("\nCSV file modified/created")


if __name__ == "__main__":
    main()

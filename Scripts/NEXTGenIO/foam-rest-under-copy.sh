#!/bin/bash --login
#SBATCH --nodes=22
#SBATCH --tasks-per-node=2
#SBATCH --job-name=foam-rest_under
#SBATCH --output=foam_execution.txt
#SBATCH -D ##/path/to/script/directory
##SBATCH --nodelist=nextgenio-cn[01-04]
#SBATCH -p normal

#SBATCH -o ##/path/to/script/directory.out.%A.%N.log
#SBATCH -e ##/path/to/script/directory.err.%A.%N.log

export KMP_AFFINITY=scatter #,verbose
export I_MPI_DEBUG=5
export OMP_NUM_THREADS=1
export PSM2_MULTIRAIL=1
export PSM2_MULTIRAIL_MAP=0:1,1:1
export I_MPI_DEBUG_OUTPUT=debug_output.txt
export PSM2_DEVICES="self,hfi,shm"
export I_MPI_HYDRA_TOPOLIB=
export I_MPI_PIN_PROCESSOR_LIST=0-11,12-22,24-35,36-46
# source ~/.bash_profile

source ~/intel-vanilla-19/OpenFOAM-v1812/etc/bashrc

total_proc=44
ppn=2

decompDict="-decomposeParDict system/decomposeParDict.$total_proc"
echo $decompDict

# foamDictionary -entry endTime -set 2000 -disableFunctionEntries system/controlDict

# Comment all of it
# rm -rf 0
# cp -rf 0.orig 0
# decomposePar -force $decompDict > log.decomposePar

mpirun -n ${total_proc} -ppn ${ppn} renumberMesh -frontWidth -latestTime -constant -dict system/renumberMeshDict -overwrite -parallel ${decompDict} > log.renumberMesh
mpirun -n ${total_proc} -ppn ${ppn} potentialFoam -parallel ${decompDict} > log.potentialFoam
mpirun -n ${total_proc} -ppn ${ppn} simpleFoam -parallel ${decompDict} > log.simpleFoam

# mpirun -n ${total_proc} -ppn ${ppn} simpleFoam -parallel ${decompDict} ${controlDict}> log.simpleFoam

python -c "import exec_foam as ex; ex.pick_info(100)"

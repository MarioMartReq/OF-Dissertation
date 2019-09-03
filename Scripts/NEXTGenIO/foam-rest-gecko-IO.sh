#!/bin/bash --login
#SBATCH --nodes=14
#SBATCH --tasks-per-node=48
#SBATCH --job-name=foam-rest-gekko-IO
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
export I_MPI_PIN_PROCESSOR_LIST=0-47
# source ~/.bash_profile


#### Load GekkoFS
module use /home/nx01/shared/GekkoFS-BSC/modules/
module load GekkoFS/latest
 
# Where do we put the data in the computation node
export TMP_PATH1="/mnt/pmem_fsdax0/gkfs${USER}"
export TMP_PATH2="/mnt/pmem_fsdax1/gkfs${user}"

# Where we put the GekkoFS Mount point
export GKFS_MNT="${HOME}/gkfs_mnt"

# Where we put the data files of GekkoFS (This directory should be persisted if we want to keep the data)
export GKFS_ROOT1="${TMP_PATH1}/gkfs_root"
export GKFS_ROOT2="${TMP_PATH2}/gkfs_root"

# Where the shared HOSTS file will be. It needs to be a shared path. Due to a bug with bash -c that does not see the environment variable if we use the export in srun we need to use the default one. If you don't do it, you will see a file not found message.
export GKFS_HOSTS_FILE="${HOME}/gkfs_hosts.txt"

# LOG FILES : Put them on a PFS as each client server appends info
export GKFS_PRELOAD_LOG_PATH=${HOME}/gkfs_client.log
export GKFS_DAEMON_LOG_PATH=${HOME}/gkfs_server.log

# LOG LEVEL : Increase to 4 to see if interception fails
export GKFS_LOG_LEVEL=1

# LAUNCH COMMAND FOR THE DAEMON, EACH one on a interface
CMD1="${GKFS_DAEMON} --mountdir=${GKFS_MNT:?} --rootdir=${GKFS_ROOT1:?} -l ib0:5000"
CMD2="${GKFS_DAEMON} --mountdir=${GKFS_MNT:?} --rootdir=${GKFS_ROOT2:?} -l ib1:5000"

# We clean the system, just in case the previous execution hang!
# Notice that we only want 1 launch per node for the daemon related processes
 
echo Erasing old files in the job nodes
srun \
    -n ${SLURM_JOB_NUM_NODES:?} \
    -N ${SLURM_JOB_NUM_NODES:?} \
    bash -c "rm -rf ${TMP_PATH1} ; mkdir -p ${TMP_PATH1}; rm -rf ${TMP_PATH2}; mkdir -p ${TMP_PATH2}"
 
# DELETE OLD FILES AND PREPARE THE NEW SYSTEM (AS THIS IS THE PFS) WE CAN DO IT DIRECTLY
 
echo Erasing Old Files
rm -rf ${GKFS_MNT} ${GKFS_HOSTS_FILE} ${GKFS_PRELOAD_LOG_PATH} ${GKFS_DAEMON_LOG_PATH}
 
echo Creating Gekko Mount Point
mkdir -p ${GKFS_MNT}
 
echo "Starting GEKKOFS_DAEMON " $SLURM_JOB_NUM_NODES
 
# Start Daemon 1, we use taskset to bind it to the correct socket.
srun \
    -N ${SLURM_JOB_NUM_NODES:?} \
    -n ${SLURM_JOB_NUM_NODES:?} \
    --export="ALL" \
    /bin/bash -c "echo Starting Daemon \${SLURMD_NODENAME}; taskset 0x000000FFFFFF000000FFFFFF ${CMD1}" &
 
# Start Daemon 2, we use taskset to bind it to the correct socket
srun -N ${SLURM_JOB_NUM_NODES:?} -n ${SLURM_JOB_NUM_NODES:?} \
    --export=ALL \
    /bin/bash -c "echo Starting Daemon \${SLURMD_NODENAME}; taskset 0xFFFFFF000000FFFFFF000000 ${CMD2}" &
 
sleep 15s



export LD_LIBRARY_PATH=##/path/to/script/directory:$LD_LIBRARY_PATH
pythonexamp="import exec_foam as ex; ex.pick_info(100,'collected_gecko')"

total_proc=672
ppn=48


decompDict="-decomposeParDict system/decomposeParDict.$total_proc"
echo $decompDict
source ~/intel-vanilla-19/OpenFOAM-v1812/etc/bashrc

echo "DF test"
srun -n 1 -N 1 --export="ALL" /bin/bash -c "LD_PRELOAD=${GKFS_PRLD} df -h ${GKFS_MNT}"

dict=50
foamDictionary -entry writeInterval -set ${dict} -disableFunctionEntries system/controlDict
name="gekko,$dict"

srun -n 1 -N 1 --export="ALL" /bin/bash -c "LD_PRELOAD=${GKFS_PRLD} decomposePar -force ${decompDict} > log.decomposePar"
srun -n ${total_proc} --ntasks-per-node ${ppn} --export="ALL" /bin/bash -c "LD_PRELOAD=${GKFS_PRLD} renumberMesh -frontWidth -latestTime -constant -dict system/renumberMeshDict -overwrite -parallel ${decompDict} > log.renumberMesh"
srun -n ${total_proc} --ntasks-per-node ${ppn} --export="ALL" /bin/bash -c "LD_PRELOAD=${GKFS_PRLD} potentialFoam -parallel ${decompDict} >log.potentialFoam" 
srun -n ${total_proc} --ntasks-per-node ${ppn}  --export="ALL" /bin/bash -c "LD_PRELOAD=${GKFS_PRLD} simpleFoam -parallel ${decompDict} > log.simpleFoam"

# srun -n 1 -N 1 --export="ALL" /bin/bash -c "LD_PRELOAD=${GKFS_PRLD} python -c ${pythonexamp}"

python -c "import exec_foam as ex; ex.pick_info(100,'collected_IO','$name')"

# We remove left over files in the computation node
echo Removing files
srun -n ${SLURM_JOB_NUM_NODES:?} \
    -N ${SLURM_JOB_NUM_NODES:?} \
    /bin/bash -c "rm -rf ${TMP_PATH1} ${TMP_PATH2}"
 
# We remove the other files, and the log (if we don't need it!)
rm -rf ${GKFS_HOSTS_FILE} ${GKFS_PRELOAD_LOG_PATH} ${GKFS_DAEMON_LOG_PATH} ${GKFS_MNT}

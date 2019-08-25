#!/bin/bash --login
#SBATCH --nodes=8
#SBATCH --tasks-per-node=48
#SBATCH --job-name=foam-motorbike
#SBATCH --output=foam_execution.txt
#SBATCH -D /home/m1819/m1819/s1888807/OpenFOAM/s1888807-v1812/run/motorBike
##SBATCH --nodelist=nextgenio-cn[01-04]
#SBATCH -p normal

#SBATCH -o /home/m1819/m1819/s1888807/OpenFOAM/s1888807-v1812/run/motorBike/mot.out.%A.%N.log
#SBATCH -e /home/m1819/m1819/s1888807/OpenFOAM/s1888807-v1812/run/motorBike/mot.err.%A.%N.log

export KMP_AFFINITY=scatter #,verbose
export I_MPI_DEBUG=0
export OMP_NUM_THREADS=1
export PSM2_MULTIRAIL=0
# export PSM2_MULTIRAIL_MAP=0:1,1:1
export I_MPI_DEBUG_OUTPUT=debug_output.txt
export PSM2_DEVICES="self,hfi,shm"
export I_MPI_HYDRA_TOPOLIB=
export HFI_UNIT=1
# export I_MPI_PIN_PROCESSOR_LIST=0-47
# source ~/.bash_profile


# module load arm-forge 
source ~/intel-vanilla-19/OpenFOAM-v1812/etc/bashrc

total_proc=384
ppn=48

#### Set some profiling flags
export ALLINEA_ENABLE_DSL=0
export ALLINEA_SAMPLER_ENABLE_HISTOGRAMS=1
module load arm-forge/h2020

dec="kahip"

decompDict="-decomposeParDict system/decomposeParDict-$dec.$total_proc"
echo $decompDict

# foamDictionary -entry writeInterval -set ${dict} -disableFunctionEntries system/controlDict
name="$dec"

# # srun -n 1 -N 1 cp $FOAM_TUTORIALS/resources/geometry/motorBike.obj.gz constant/triSurface/
# srun -n 1 -N 1 surfaceFeatureExtract > log.last
# srun -n 1 -N 1 blockMesh > log.last
# srun -n 1 -N 1 decomposePar $decompDict -force > log.last

# if foamDictionary -entry geometry -value system/snappyHexMeshDict | \
#    grep -q distributedTriSurfaceMesh
# then
#     mpirun -n ${total_proc} -ppn ${ppn} surfaceRedistributePar motorBike.obj independent -parallel $decompDict
# fi

# mpirun -n ${total_proc} -ppn ${ppn} snappyHexMesh -overwrite -parallel $decompDict  > log.snappy-$dec

# restore0Dir -processor

# mpirun -n ${total_proc} -ppn ${ppn}  patchSummary -parallel $decompDict > log.patch-$dec
# mpirun -n ${total_proc} -ppn ${ppn}  potentialFoam -parallel $decompDict > log.potentialFoam
# mpirun -n ${total_proc} -ppn ${ppn}  checkMesh -writeFields '(nonOrthoAngle)' -constant -parallel $decompDict > log.check-$dec

ALLINEA_SLURM_USE_PRELOAD=ALTERNATE ALLINEA_SAMPLER_KEEP_PRELOADS=1 ALLINEA_PRESERVE_LD_PRELOAD=1 map --profile srun -n ${total_proc} --ntasks-per-node ${ppn}  simpleFoam -parallel $decompDict > log.simpleFoam


# srun -n 1 -N 1 reconstructParMesh -constant
# srun -n 1 -N 1 reconstructPar -latestTime


# python -c "import exec_foam as ex; ex.pick_info(100,'collected_motor','$name')"


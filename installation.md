# Environment setup and OpenFOAM installation notes.

This document contains notes taken during the initial environment setup in the cluster provided by the SCC sponsor, Boston Limited, and the posterior OpenFOAM installation.

#### Intel Compilers

Both for the competition, and for diverse testing and tuning later, we used Intel Parallel Studio XE, obtained under a student license. It can be found and downloaded in the following link:

[Intel software for students](https://software.intel.com/en-us/qualify-for-free-software/student "Free software for students").

After installing the package, the following lines need can be added to `~/.bash_profile` in order to be able to use and make default Intel compilers and MPI.

```bash
source /opt/intel/compilers_and_libraries_2019.2.187/linux/bin/compilervars.sh i$
source /opt/intel/parallel_studio_xe_2019.2.057/bin/psxevars.sh intel64;
source /opt/intel/impi/2019.2.187/intel64/bin/mpivars.sh intel64;
source /opt/intel/mkl/bin/mklvars.sh intel64
export MPI_ROOT=/opt/intel/compilers_and_libraries_2019.2.187/linux/mpi/intel64/$
export MPI_HOME=/opt/intel/impi/2019.2.187/intel64/;
export MPI_ARCH_PATH=$MPI_HOME
```

#### OpenFOAM installation

The following instructions are given to install OpenFOAM in **Centos 7.x with Intel compilers and MPI**.

##### Environment setup

First, we need are going to install some packages required to install OpenFOAM.

```
yum install gcc-c++ gcc-gfortran gmp flex flex-devel boost zlib zlib-devel  fftw
```

Additionally, we need to install **CMAKE**.

```bash
wget https://cmake.org/files/v3.13/cmake-3.13.3.tar.gz && tar -xzf cmake-3.13.3.tar.gz
cd cmake-3.13.3
./bootstrap
make
sudo make install
```

In case that **./bootstrap** prints that there is errors with the compilers, the following might be required
```bash
export CC='../gcc'
export CXX='../g++'
#You might need to export as well the following
export LD_LIBRARY_PATH=/../lib64
```

##### OpenFOAM download

According to the [2019 SCC benchmarking rules](http://hpcadvisorycouncil.com/events/student-cluster-competition/Benchmarking/ "SCC website"), during the competition, the OpenFOAM version will be the 1812, available to download in its main page. The following steps are required to download and install OpenFOAM.

```bash
#First, create a folder named OpenFOAM in your home directory.
mkdir OpenFOAM
#Download both OpenFOAM and complimentary software
wget https://sourceforge.net/projects/openfoamplus/files/v1812/OpenFOAM-v1812.tgz && wget https://sourceforge.net/projects/openfoamplus/files/v1812/ThirdParty-v1812.tgz
#Extract both files and eliminate them
tar -xzf OpenFOAM-v1812.tgz -C $HOME/OpenFOAM && tar -xzf ThirdParty-v1812.tgz -C $HOME/OpenFOAM && rm -rf OpenFOAM-v1812.tgz ThirdParty-v1812.tgz
#Source OpenFOAM
source $HOME/OpenFOAM/OpenFOAM-v1812/etc/bashrc;
```

##### OpenFOAM installation
Once the folders are extracted, and in order to proceed with the installation, some files need to be modified.

In the `~/OpenFOAM/OpenFOAM-v1812/etc/bashrc`, the following lines should be changed:
```bash
export WM_COMPILER_TYPE=system
export WM_ARCH_OPTION=64
export WM_MPLIB=INTELMPI
```

Lastly, file `~/OpenFOAM/OpenFOAM-v1812/wmake/rules/linux64Icc/mplibINTELMPI` needs to be modified as well.
```bash
PINC	   = -I $(MPI_ARCH_PATH)include
PLIBS	   = -L$(MPI_ARCH_PATH)lib/release -lmpi
```

Lastly, before proceeding with the installation, we can add the following lines to `~/.bash_profile`. Exit the SSH connection, and re-enter, and those changes will take places.

```bash
alias load_openfoam="source $HOME/OpenFOAM/OpenFOAM-v1812/etc/bashrc;
export WM_COMPILER=Icc;
export WM_MPLIB=INTELMPI;
export LD_PRELOAD="libmpi.so";
export FOAM_MPI=INTELMPI";
```

After executing the command `load_openfoam` and `foam` (that will bring us to the main OpenFOAM folder), the compilation and installation can start simply by executing the following command.

```bash
export WM_NCOMPPROCS=24
./Allwmake
```

#### Additional installations.

Non-essential but useful packages.

##### Screen forwarding.

In order to be able to forward the screen from the server to your local machine, the following packages need to be installed.

```bash
#Sometimes, these packages are already installed. Test them with the following command.
xeyes
#If not, install X11 with the following command
yum install -y xorg-x11-server-Xorg xorg-x11-xauth xorg-x11-apps
```

##### Paraview

Paraview is a visualization tool that is already included in the `~/OpenFOAM/ThirdParty-v1812/` but needs to be installed. Follow the next steps to install it.

```bash
#Install Qt5 with the following command
yum install qt5-qtx11extras-devel qt5-qttools-devel
#Install Paraview
./makeParaView
wmRefresh
```

#### Testing the installation

Use the following commands to check if the installation was correctly completed.


```bash
#The next command gives a general overview of all installed OpenFOAM parts
foamInstallationTest
#In order to execute an example tutorial the run folder needs to be created
mkdir -p $FOAM_RUN
#Executing the pitzDaily tutorial
run
cp -r $FOAM_TUTORIALS/incompressible/simpleFoam/pitzDaily ./
cd pitzDaily
blockMesh
simpleFoam
#This last command will only work if the steps explained in "Additional installations" have been completed.
paraFoam
```

#### Post-installation process (needs to be tested)

cc in /root/OpenFOAM/OpenFOAM-v1812/wmake/rules/linux64Icc/c and c++ needs to be modified to be mpiicc
809  wcleanBuild -h
810  wcleanBuild -a
811  ./Allwmake

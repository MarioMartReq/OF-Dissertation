# Comment this "if" to download and extract in the same folder
if [ -z $1 ]
then
    mkdir OpenFOAM
    cd OpenFOAM
else
    mkdir $1
    cd $1
fi

version=1812

wget https://sourceforge.net/projects/openfoamplus/files/v${version}/OpenFOAM-v${version}.tgz
wget https://sourceforge.net/projects/openfoamplus/files/v${version}/ThirdParty-v${version}.tgz
tar -xf OpenFOAM-v${version}.tgz
tar -xf ThirdParty-v${version}.tgz
rm -rf OpenFOAM-v${version}.tgz ThirdParty-v${version}.tgz
source OpenFOAM-v${version}/etc/bashrc

# Metis download. Comment if it is not requried. 
cd ThirdParty-v${version} && wget http://glaros.dtc.umn.edu/gkhome/fetch/sw/metis/metis-5.1.0.tar.gz && tar -xf metis-5.1.0.tar.gz 

exec bash

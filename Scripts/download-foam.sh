if [ -z $1 ]
then
    mkdir OpenFOAM
    cd OpenFOAM
else
    mkdir $1
    cd $1
fi

wget https://sourceforge.net/projects/openfoamplus/files/v1812/OpenFOAM-v1812.tgz
wget https://sourceforge.net/projects/openfoamplus/files/v1812/ThirdParty-v1812.tgz
tar -xf OpenFOAM-v1812.tgz
tar -xf ThirdParty-v1812.tgz
rm -rf OpenFOAM-v1812.tgz ThirdParty-v1812.tgz
source OpenFOAM-v1812/etc/bashrc
exec bash

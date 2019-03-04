# Misc information

Initial set up for installing centOS
Downloaded the DVD iso from the oficial website.
In VirtualBox, we create a new virtual machine. VHD,  RedHat, 2 GB of ram and 30 gb of static memory, 2 cores, motherboard→ pointing device usb tablet.  Create the virtual disk.
Open settings from this created virtual machine, click on storage, empty, click on the cd and select the iso.
go to system and in boot order, place first the optical.
in display, set video memory to the maximum.
in general, advanced, set bidirectional both options.
save and execute
once the virtual machine is launched, in the configuration, we are going to choose the "gnome desktop" and system administration.
once centos is installed and we are on the desktop, make sure that the wired connection is connected.
go to settings of the virtual machine, network, advanced, port forwarding, add a new rule with: Host IP="127.0.0.1", Host Port="2222", Guest IP="10.0.2.15", Guest Port="22"
From host terminal:  ssh -p2222 root@127.0.0.1 (pass: banana) or ssh -p2222 mario@127.0.0.1 (pass: boniatoperdido)
Copy from host to vb

Update kernel sudo yum update kernel*
https://www.if-not-true-then-false.com/2010/install-virtualbox-guest-additions-on-fedora-centos-red-hat-rhel/ follow instructions
intel mpi export LD_PRELOAD="libmpi.so"
Foam tricks
http://www.wolfdynamics.com/wiki/OFtipsandtricks.pdf

https://linuxcluster.wordpress.com/2018/06/04/compiling-openfoam-5-with-intel-mpi/

http://www.hpcadvisorycouncil.com/pdf/OpenFOAM_Best_Practices.pdf

# Scripts description.

This folder contains the different scripts used during the development of the dissertation. Folders [NEXTGenIO](https://github.com/MarioMartReq/OF-Dissertation/tree/master/Scripts/NEXTGenIO) and [Fulhame-cirrus](https://github.com/MarioMartReq/OF-Dissertation/tree/master/Scripts/Fulhame-cirrus) contain some scripts adapted to SLURM and PBS that launch of chained jobs. [runParallelNodes.txt](https://github.com/MarioMartReq/OF-Dissertation/blob/master/Scripts/runParallelNodes.txt) contains a OpenFOAM modified version that launches a parallel job distributing it accross the nodes specified in a hostfile file (note that it might need to be changed depending on your MPI version.)

 ---
### [exec_foam.py](https://github.com/MarioMartReq/OF-Dissertation/blob/master/Scripts/exec_foam.py)

Script containing various functions to launch and collect information about executions. 


### [download_foam.sh](https://github.com/MarioMartReq/OF-Dissertation/blob/master/Scripts/download_foam.py)

Script that automatically downloads and decompresses the specified OpenFOAM version. 



---

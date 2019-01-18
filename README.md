# Search and Sample Return Project

This project is modeled after the [NASA sample return challenge](https://www.nasa.gov/directorates/spacetech/centennial_challenges/sample_return_robot/index.html) and forked from Udacity's Robotics Nanodegree program, project 1. 

My plan for this repository is for fulfillment of the challenge, and then further forking to create a dog-excrement search and retreival bot for my back yard. 

## The Simulator
The first step is to download the simulator build that's appropriate for your operating system.  Here are the links for [Linux](https://s3-us-west-1.amazonaws.com/udacity-robotics/Rover+Unity+Sims/Linux_Roversim.zip), [Mac](	https://s3-us-west-1.amazonaws.com/udacity-robotics/Rover+Unity+Sims/Mac_Roversim.zip), or [Windows](https://s3-us-west-1.amazonaws.com/udacity-robotics/Rover+Unity+Sims/Windows_Roversim.zip).  

You can test out the simulator by opening it up and choosing "Training Mode".  Use the mouse or keyboard to navigate around the environment and see how it looks.

## Installing Anaconda, creating runtime environment, and executing

## Overview
Using Anaconda consists of the following:

1. Install [`miniconda`](http://conda.pydata.org/miniconda.html) on your computer
2. Create a new `conda` [environment](http://conda.pydata.org/docs/using/envs.html) using this project
3. Each time you wish to work, activate your `conda` environment

---

## Installation

**Download** the version of `miniconda` that matches your system. Make sure you download the version for Python 3.6.1

**NOTE**: There have been reports of issues creating an environment using miniconda `v4.3.13`. If it gives you issues try versions `4.3.11` or `4.2.12` from [here](https://repo.continuum.io/miniconda/).

|        | Linux | Mac | Windows | 
|--------|-------|-----|---------|
| 64-bit | [64-bit (bash installer)][lin64] | [64-bit (bash installer)][mac64] | [64-bit (exe installer)][win64]
| 32-bit | [32-bit (bash installer)][lin32] |  | [32-bit (exe installer)][win32]

[win64]: https://repo.continuum.io/miniconda/Miniconda3-latest-Windows-x86_64.exe
[win32]: https://repo.continuum.io/miniconda/Miniconda3-latest-Windows-x86.exe
[mac64]: https://repo.continuum.io/miniconda/Miniconda3-latest-MacOSX-x86_64.sh
[lin64]: https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
[lin32]: https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86.sh

**Install** [miniconda](http://conda.pydata.org/miniconda.html) on your machine. Detailed instructions:

- **Linux:** http://conda.pydata.org/docs/install/quick.html#linux-miniconda-install
- **Mac:** http://conda.pydata.org/docs/install/quick.html#os-x-miniconda-install
- **Windows:** http://conda.pydata.org/docs/install/quick.html#windows-miniconda-install

**Setup** your the `Sample-Search-And-Retrieve` environment. 

```sh
git clone https://github.com/ergoego/Sample-Search-And-Retrieve.git  
cd RoboND-Python-StarterKit
```

If you are on Windows, **rename**   
`meta_windows_patch.yml` to   
`meta.yml`

**Create** Sample-Search-And-Retrieve.  Running this command will create a new `conda` environment that is provisioned with all libraries you need to be successful in this program.  
**NOTE:** if you get an error when you try to run this command that `conda` doesn't exist, try closing and re-opening your terminal window.
```
conda env create -f environment.yml
```
**NOTE:** If the above command fails due to internet issues or timed out HTTP request then remove the partially built environment using the following command (then run the above `create` command again):
```
conda env remove -n Sample-Search-And-Retrieve
conda env create -f environment.yml 
```
**Verify** that the Sample-Search-And-Retrieve environment was created in your environments:

```sh
conda info --envs
```

**Cleanup** downloaded libraries (remove tarballs, zip files, etc):

```sh
conda clean -tp
```
## Installing OpenCV
The Udacity project this is forked from suggests installing miniconda with `python==3.5.1`, and specifying `opencv3` in `environment.yml`, however this was giving me problems that moving to `python==3.6.1` solved. 

However, `opencv3` no longer wanted to work with that version, so the workaround I came up with was to: remove `opencv3` and change to `python==3.6.1`, build the environment, install pip in the environment, and then use pip in the environment to install `opencv-contrib-python` (opencv doesn't mantain a pip package for their library, so the open-source `opencv-python-contrib` is basically a mirror). I'm sure there is a way to have this done automatically when the environment is built and what I have done is by no means optimal. 

So this boils down to:

```
conda install -n Sample-Search-And-Retrieve pip
activate Sample-Search-And-Retrieve
pip install opencv-contrib-python
```
## Using Anaconda

Now that you have created an environment, in order to use it, you will need to activate the environment. This must be done **each** time you begin a new working session i.e. open a new terminal window. 

**Activate** the `Sample-Search-And-Retrieve` environment:

### OS X and Linux
```sh
$ source activate Sample-Search-And-Retrieve
```
### Windows
Depending on shell either:
```sh
$ source activate Sample-Search-And-Retrieve
```
or

```sh
$ activate Sample-Search-And-Retrieve
```

That's it. Now all of the `Sample-Search-And-Retrieve` libraries are available to you.

To exit the environment when you have completed your work session, simply close the terminal window.

### Uninstalling
If you ever want to delete or remove an environment 

To **delete/remove** the "Sample-Search-And-Retrieve" environment:
```
conda env remove -n Sample-Search-And-Retrieve
```

## Data Analysis
Included is the IPython notebook called `Rover_Project_Test_Notebook.ipynb`, which was used for initial prototyping and image analysis. 

## Navigating Autonomously
The file called `drive_rover.py` is what you will use to navigate the environment in autonomous mode.  This script calls functions from within `perception.py` and `decision.py`.  The functions defined in the IPython notebook are all included in`perception.py`. `decision.py` includes another function called `decision_step()`, which uses conditional statements evaluating the rover's state and the results of the `perception_step()` analysis to navigate autonomously. 

Launch the program:

```sh
python drive_rover.py
```  

Then launch the simulator and choose "Autonomous Mode". 

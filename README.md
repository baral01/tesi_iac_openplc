![ansible-lint](https://github.com/baral01/tesi_iac_openplc/actions/workflows/ansible-lint.yml/badge.svg?branch=master)
# IaC OpenPLC
Automates the deployment of [OpenPLC Runtime](https://github.com/thiagoralves/OpenPLC_v3) to a virtual environment using Vagrant and Ansible.

Vagrant will create a virtual machine running Debian/bullseye64, which will be provisioned with Ansible by executing the tasks listed in the playbook.  
At the end of the provisioning, the virtual machine will have the OpenPLC runtime installed and its webserver running and accessible at `127.0.0.1:8080`.
## Steps
- Install Oracle VM VirtualBox v6.1.36
- Install [Vagrant](https://releases.hashicorp.com/vagrant/2.3.0/) latest version
- Install [Ansible](https://docs.ansible.com/ansible/latest/installation_guide/installation_distros.html) latest version
- Clone the project
- Move to the `vagrant` or the `vagrant-wsl` folder
- If using WSL, run `set_variables.sh` (change `VAGRANT_HOME` to the correct user's home directory)
- Run `vagrant up`  

It's possible to choose where to install OpenPLC runtime inside the virtual machine by changing the value of the variable `working_directory` (from playbook.yml) with another path.  

## Demo with a modbus server
It's possible to test if the runtime is working correctly by running the code in `testing/example/demo.st` and seeing if it behaves as intended.  
`demo.st` was generated using [OpenPLC Editor](https://openplcproject.com/docs/installing-openplc-editor/) and it describes a situation with two power buttons and a lamp: the lamp is initially off and it can be turned on by pressing the the first button and it can be turned off only by pressing the second button.  
Since I'm running OpenPLC Runtime in a linux virtual machine, I'm lacking the necessary I/O points to test my code, but thankfully it's possible to expand them by attaching Modbus slave devices to the runtime.  
We can use software to emulate a Modbus slave device able to expose its inputs, coils and registers which OpenPLC Runtime can use to run the code written in `demo.st`. By changing the two input values (the power buttons) in our emulated device, the code correctly changed the output value (the lamp). It's possible to follow what is happening from the "Monitoring" tab of the dashboard.  

Software that can be used to emulate a Modbus server:  
- `updating_server.py` implemented in this repository (can be found inside the `testing` folder), which uses Python 3.10 and [pymodbus v3](https://pypi.org/project/pymodbus/) **\*\*Working\*\***
- [pyModSlave](https://pypi.org/project/pyModSlave/) which uses Python 3.7 and offers a GUI (last updated in January 2021) **\*\*Tested on Win10, Working\*\***
- [ModRSsim2](https://sourceforge.net/projects/modrssim2/) GUI application for Windows (last updated in October 2019) **\*\*Not Tested\*\***
- [Modbus Simulator](https://github.com/riptideio/modbus-simulator) which uses Python 2.7 (should also work with version <=3.6, after some working with the requirements) and offers a GUI (last updated in May 2019) **\*\*Tested on Win10, Working\*\***
- [ModbusPal](https://sourceforge.net/projects/modbuspal/) which uses Java and offers a GUI (last updated in November 2020, status "abandoned") **\*\*Not Tested\*\***  

### `updating_server.py` usage
- Create a Python3.10 virtual environment using virtualenv  
```
python -m pip install virtualenv
virtualenv -p path/to/python3.10/executable path/to/modbus-server
cd path/to/modbus-server
./Scripts/activate
```  
- Install requirements  (/testing/modbus-testing/requirements.txt)
```
python -m pip install -r requirements.txt
```  
- Run the server
```
python updating_server.py [-h] [--host HOST] [--port PORT] [--log {critical,error,warning,info,debug}]
```  
### pyModSlave usage
- Create a Python3.7 virtual environment using virtualenv  
```
python -m pip install virtualenv
virtualenv -p path/to/python3.10/executable path/to/pyModSlave
cd path/to/pyModSlave
./Scripts/activate
```  
- Install requirements
```
python -m pip install pyModSlave
python -m pip install pyserial
python -m pip install modbus-tk
python -m pip install PyQt5
```  
- Run the server
```
python ./Lib/site-packages/pyModSlave/pyModSlave.py
```  
### Modbus Simulator usage on Win10
- Create a Python2.7 virtual environment using virtualenv  
```
python -m pip install virtualenv
virtualenv -p path\to\python2.7\executable path\to\modbus-sim
cd path\to\modbus-sim
.\Scripts\activate
```  
- Clone repo inside the the modbus-sim folder  
```
git clone https://github.com/riptideio/modbus-simulator.git
```
- Install Cython  
```
python -m pip install Cython==0.29.2
```
- Install Kivy and its dependencies
```
python -m pip install docutils pygments pypiwin32 kivy.deps.sdl2 kivy.deps.glew
python -m pip install kivy.deps.gstreamer
python -m pip install kivy==1.10.1
```  
- Install Modbus Simulator requirements  
```
python -m pip install -r .\modbus-simulator\requirements
```  
with them being:
```
Click==7.0
Cython==0.29.2
docutils==0.13.1
Kivy==1.10.1
Kivy-Garden==0.1.4
pygame==1.9.4
pyglet==1.2.4
Pygments==2.1.3
pymodbus==2.1.0
pyserial==3.4
requests==2.12.4
six==1.11.0
```  
- Start the simulator from a bash terminal (opened in the modbus-sim folder)
```
source ./Scripts/activate
export PATH=/path/to/modbus-sim/share/sdl2/bin:$PATH
export PATH=/path/to/modbus-sim/share/glew/bin:$PATH
cd modbus-simulator
./tools/launcher
```
- Select TCP and choose a port (default is fine)  
- Open settings and type the correct private IP. Close settings and then click "Start"  
- Add a slave device, two discrete inputs and a coil ([example](https://www.youtube.com/watch?v=a5-OridSlt8))

### Run `demo.st`
- Open OpenPLC Runtime dashboard (default credentials are `openplc`)
- From the tab "Slave Devices", add the simulator by filling the fields (id is `0` for `updating_server.py`, `1` for the others)
- From the tab "Programs", upload the `demo.st` to the runtime
- Click "Start PLC"  

From the "Monitoring" tab, it's possible to see the current values of the two discrete inputs and the coil. Value changes from the server will be reflected here, so by editing the inputs' values it's possible to see how the coil's value changes as specified by the demo code.
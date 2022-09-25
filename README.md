# IaC OpenPLC
Automates the deployment of OpenPLC runtime to a virtual environment using Vagrant and Ansible.

Vagrant will create a virtual machine running Debian/bullseye64, which will be provisioned with Ansible by executing the tasks listed in the playbook.  
At the end of the provisioning, the virtual machine will have the OpenPLC runtime installed and its webserver running and accessible at `127.0.0.1:8080`.
## Steps
- Install Oracle VM VirtualBox v6.1.36
- Install [Vagrant](https://releases.hashicorp.com/vagrant/2.3.0/) latest version
- Install [Ansible](https://docs.ansible.com/ansible/latest/installation_guide/installation_distros.html) latest version
- Clone the project
- Move to the `vagrant` or the `vagrant-wsl` folder
- If using WSL, run `set_variables.sh`
- Run `vagrant up`  

It's possible to choose where to install OpenPLC runtime inside the virtual machine by changing the value of the variable `working_directory` (from playbook.yml) with another path.  

## Demo with modbus simulator
It's possible to test if the runtime is working correctly by running the code in `example/demo.st` and seeing if it behaves as intended.  
`demo.st` was generated using [OpenPLC Editor](https://openplcproject.com/docs/installing-openplc-editor/) and it describes a situation with two power buttons and a lamp: the lamp is initially off and it can be turned on by pressing the the first button and it can be turned off only by pressing the second button.  
Since I'm running OpenPLC Runtime in a linux virtual machine, I'm lacking the necessary I/O points to test my code, but thankfully it's possible to expand them by attaching Modbus slave devices to the runtime.  
I used [Modbus Simulator](https://github.com/riptideio/modbus-simulator) to emulate a Modbus slave device able to expose its inputs, coils and registers which OpenPLC Runtime can use to run the code written in `demo.st`. By changing the two input values (the power buttons) in the simulator, the code correctly changed the output value (the lamp). I was able to follow what was happening from the "Monitoring" tab of the dashboard.  
### Modbus Simulator usage on Win10
- Create a Python2.7 virtual environment using virtualenv in `modbus-sim` path and activate it  
```
python -m pip install virtualenv
virtualenv -p path\to\python2.7\executable path/to/modbus-sim
cd path/to/modbus-sim
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
- Install Python for Windows packages  
```
python -m pip install pywin32
python -m pip install pypiwin32
```
- Install Modbus Simulator requirements  
```
python -m pip install -r modbus-simulator\requirements
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
- Start the simulator from a bash terminal
```
export PATH=/path/to/modbus-sim/share/sdl2/bin:$PATH
export PATH=/path/to/modbus-sim/share/glew/bin:$PATH
cd modbus-simulator
./tools/launcher
```
- Select TCP and port (default is fine), open settings and type correct private IP. Click "Start"  
- Add a slave device, two discrete inputs and a coil ([example](https://www.youtube.com/watch?v=a5-OridSlt8))

### Run `demo.st`
- Open OpenPLC Runtime dashboard (default credentials are `openplc`)
- From the tab "Slave Devices", add the simulator by filling the fields
- Upload the `demo.st` to the runtime
- Click "Start PLC"  

From the "Monitoring" tab, it's possible to see the current values of the two discrete inputs and the coil. Value changes from the simulator will be reflected here, so by editing the inputs' values it's possible to see how the coil's value changes as specified by the demo code.
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
from pyVmomi import vim 
from pyVim.connect import SmartConnect
import ssl
import getpass

passw = getpass.getpass()

# Function to Clone The VM
def clone_vm(service_instance, vm_name, clone_name, folder_name):
    content = service_instance.content
    datacenter = content.rootFolder.childEntity[0]
    vm_folder = None

    # Find where VM exists
    for folder in datacenter.vmFolder.childEntity:
        if folder.name == folder_name:
            vm_folder = folder
            break

    if vm_folder is None:
        raise Exception(f"Folder '{folder_name}' not found.")
    vm = None

# Find VM to Clone
for 

# Connecting to the vCenter server
s = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
s.verify_mode = ssl.CERT_NONE

si = SmartConnect(host = "vcenter2.micah.local", user = "micah.adm", pwd = passw, sslContext=s)



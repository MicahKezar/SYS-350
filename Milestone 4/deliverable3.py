from pyVmomi import vim 
from pyVim.connect import SmartConnect
import ssl
import getpass
import warnings
from termcolor import colored
import time

# Mute Deprecation (Thank u David <3)
warnings.filterwarnings("ignore", category=DeprecationWarning)

def main_menu():
    while True:
        print("\n Main Menu:")
        print("1. Connect to vCenter")
        print("2. Connection info")
        print("3. Session info")
        print("4. Search for VM")
        print("5. Power On VM")
        print("6. Power Off VM")
        print("7. Clone VM")
        print("8. Create Snapshot")
        print("9. Delete Snapshot")
        print("10. Exit")

        selection = input("\nSelect an Option ")

        if selection == '1':
            print("\n")
            vmConnect()
        elif selection == '2':
            print("\n")
            connectionInfo()
        elif selection == '3':
            print("\n")
            sessionInfo()
        elif selection == '4':
            print("\n")
            vmSearch()
        elif selection == '5':
            print("\n")
            powerOn()
        elif selection == '6':
            print("\n")
            powerOff()
        elif selection == '7':
            print("\n")
            cloneVM()
        elif selection == '8':
            print("\n")
            createSnapshot()
        elif selection == '9':
            print("\n")
            delSnapshot()
        elif selection == '10':
            print(colored('Goodbye!', 'green'))
            exit()

def vmConnect():
    s = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    s.verify_mode = ssl.CERT_NONE

    global si
    passw = getpass.getpass()
    si = SmartConnect(host = "vcenter2.micah.local", user = "micah.adm", pwd = passw, sslContext=s)
    print(colored('\nConnected!', 'green'))
    input(colored('\nPress ENTER to go back to the Main Menu', 'yellow'))
    main_menu()

def powerOn():
    search = input("Enter a VM to Power On: ")
    content = si.RetrieveContent()
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)
    for managed_object in container.view:
        if search in managed_object.name:
            vm = managed_object
            break
    container.Destroy()
    vm.PowerOnVM_Task()
    print(colored('\n' + vm.name + ' has been Powered On!', 'green'))
    main_menu()

def powerOff():
    search = input("Enter a VM to Power Off: ")
    content = si.RetrieveContent()
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)
    for managed_object in container.view:
        if search in managed_object.name:
            vm = managed_object
            break
    container.Destroy()
    vm.PowerOffVM_Task()
    print(colored('\n' + vm.name + ' has been Powered Off!', 'red'))
    main_menu()

def cloneVM():
    source_vm_name = input("Enter the name of the VM to clone: ")
    clone_name = input("Enter the name for the new clone: ")
    datastore_name = input("Enter the name of the target datastore for the clone: ")

    content = si.RetrieveContent()
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)

    source_vm = None
    for managed_object in container.view:
        if source_vm_name in managed_object.name:
            source_vm = managed_object
            break

    container.Destroy()

    if source_vm:
        target_datastore = None
        for datastore in content.viewManager.CreateContainerView(content.rootFolder, [vim.Datastore], True).view:
            if datastore_name in datastore.name:
                target_datastore = datastore
                break

        if target_datastore:
            clone_spec = vim.vm.CloneSpec(location=vim.vm.RelocateSpec(datastore=target_datastore))
            clone_folder = source_vm.parent
            clone_task = source_vm.CloneVM_Task(folder=clone_folder, name=clone_name, spec=clone_spec)
            print(colored(f'\nVM {clone_name} has been successfully cloned from {source_vm_name}!', 'green'))
        else:
            print(colored(f'\nDatastore {datastore_name} not found. Clone operation canceled.', 'red'))
    else:
        print(colored(f'\nVM {source_vm_name} not found. Clone operation canceled.', 'red'))

    main_menu()

def createSnapshot():
    vm_name = input("Enter the name of the VM to snapshot: ")
    snapshot_name = input("Enter the name for the new snapshot: ")
    description = input("Enter a description for the snapshot: ")

    content = si.RetrieveContent()
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)

    source_vm = None
    for managed_object in container.view:
        if vm_name == managed_object.name:
            source_vm = managed_object
            break

    container.Destroy()

    if source_vm:
        snapshot_task = source_vm.CreateSnapshot_Task(name=snapshot_name, description=description, memory=False, quiesce=False)
        print(f"Creating snapshot {snapshot_name} for VM {vm_name}...")

        task_info = snapshot_task.info
        if task_info.state == "running":
            print(f"Snapshot {snapshot_name} created successfully for VM {vm_name}.")
        else:
            print(f"Snapshot creation task completed with state: {task_info.state}")
            if task_info.error:
                print(f"Error message: {task_info.error}")
            else:
                print("No error message provided.")
    else:
        print(f"VM {vm_name} not found. Snapshot creation canceled.")    
    main_menu()

def connectionInfo():
    currentSession = si.content.sessionManager.currentSession
    print ("\nAgent: " + currentSession.userAgent)
    print ("Username: " + currentSession.userName)
    print ("Server: " + si.content.about.name)
    print ("Key: " + currentSession.key)
    input(colored('\nPress ENTER to go back to the Main Menu', 'yellow'))
    main_menu()

def delSnapshot():
    vm_name = input("Enter the name of the VM with the snapshot to delete: ")

    content = si.RetrieveContent()
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)

    source_vm = None
    for managed_object in container.view:
        if vm_name == managed_object.name:
            source_vm = managed_object
            break

    container.Destroy()

    if source_vm:
        if source_vm.snapshot is not None:
            snapshots = source_vm.snapshot.rootSnapshotList
            if snapshots:
                print("Snapshots for VM:")
                for idx, snapshot in enumerate(snapshots):
                    print(f"{idx + 1}. {snapshot.name}")

                snapshot_idx = int(input("Enter the number of the snapshot to delete: ")) - 1

                if 0 <= snapshot_idx < len(snapshots):
                    snapshot_to_delete = snapshots[snapshot_idx]
                    snapshot_name = snapshot_to_delete.name
                    snapshot_task = snapshot_to_delete.snapshot.RemoveSnapshot_Task(removeChildren=False)
                    task_info = snapshot_task.info

                    if task_info.state == "running":
                        print(f"Deleting snapshot {snapshot_name} for VM {vm_name}...")
                    else:
                        print(f"Snapshot deletion task completed with state: {task_info.state}")\
                        if task_info.error:
                            print(f"Error message: {task_info.error}")
                        else:
                            print("No error message provided.")
                else:
                    print("Invalid snapshot index selected.")
            else:
                print(f"No snapshots found for VM {vm_name}.")
        else:
            print(f"VM {vm_name} does not have any snapshots.")
    else:
        print(f"VM {vm_name} not found. Snapshot deletion canceled.")
    main_menu()

def sessionInfo():
    aboutInfo=si.content.about
    print(aboutInfo)
    input(colored('\nPress ENTER to go back to the Main Menu', 'yellow'))
    main_menu()

def vmSearch():

    search = input("Enter a VM: ")

    container_view = si.content.viewManager.CreateContainerView(
        si.content.rootFolder, [vim.VirtualMachine], True
    )

    vm_list = container_view.view

    if not search:
        for vm in vm_list:
            print_vm_info(vm)
            print("-" * 30)
    else:
        matching_vms = [vm for vm in vm_list if search.lower() in vm.name.lower()]

        if matching_vms:
            print(colored(f"\nMatching VM's with '{search}':", 'yellow'))
            for vm in matching_vms:
                print_vm_info(vm)
                print("-" * 30)
        else:
            print(colored(f"\nNo Matching VM's found for '{search}'. Here is a list of all available VM's.", 'red'))
            time.sleep(1)
            for vm in vm_list:
                print_vm_info(vm)
                print("-" * 30)
    main_menu()


def print_vm_info(vm): 

    print(colored("VM Name:", 'green'), vm.name) 
    print(colored("Power State:", 'green'), vm.runtime.powerState) 
    print(colored("Number of CPUs:", 'green'), vm.config.hardware.numCPU) 
    memory_in_gb = vm.config.hardware.memoryMB / 1024 
    print(colored("Memory (GB):", 'green'), f"{memory_in_gb:.2f}") 
    print(colored("IP Address:", 'green'), vm.guest.ipAddress) 
    #if vm.guest and vm.guest.ipAddress:
         
         

main_menu()


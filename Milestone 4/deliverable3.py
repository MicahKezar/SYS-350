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
        print("5. Exit")

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



def connectionInfo():
    currentSession = si.content.sessionManager.currentSession
    print ("\nAgent: " + currentSession.userAgent)
    print ("Username: " + currentSession.userName)
    print ("Server: " + si.content.about.name)
    print ("Key: " + currentSession.key)
    input(colored('\nPress ENTER to go back to the Main Menu', 'yellow'))
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

def print_vm_info(vm): 

    print(colored("VM Name:", 'green'), vm.name) 
    print(colored("Power State:", 'green'), vm.runtime.powerState) 
    print(colored("Number of CPUs:", 'green'), vm.config.hardware.numCPU) 
    memory_in_gb = vm.config.hardware.memoryMB / 1024 
    print(colored("Memory (GB):", 'green'), f"{memory_in_gb:.2f}") 
    print(colored("IP Address:", 'green'), vm.guest.ipAddress) 
    #if vm.guest and vm.guest.ipAddress:
         
         

main_menu()


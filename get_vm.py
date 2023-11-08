from pyVim import connect
from pyVmomi import vim

# Connect to the ESXi host
host = 'your_esxi_host'
user = 'root'
password = '2002romial'

try:
    connection = connect.SmartConnectNoSSL(host=host, user=user, pwd=password)
    content = connection.RetrieveContent()

    # Get the VMs
    vm_view = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)
    vm_list = vm_view.view

    # Print the VM details
    for vm in vm_list:
        print("VM Name:", vm.name)
        print("VM Power State:", vm.runtime.powerState)
        print("VM CPU Count:", vm.config.hardware.numCPU)
        print("VM Memory Size (MB):", vm.config.hardware.memoryMB)
        print("VM Guest OS:", vm.guest.guestFullName)
        print("VM IP Address:", vm.summary.guest.ipAddress)
        print("--------------------------------------")

except Exception as e:
    print("An error occurred:", e)

finally:
    # Disconnect from the ESXi host
    try:
        connect.Disconnect(connection)
    except NameError:
        pass

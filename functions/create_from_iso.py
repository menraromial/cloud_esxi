# Import the required libraries
from pyVim import connect
from pyVmomi import vim
from pyVim.task import WaitForTask
import sys
from utils import service_instance
# Create a new virtual machine from an ISO file
def main(args):
    #si = connect.SmartConnect(host=host_ip, user=username, pwd=password,disableSslCertValidation=True)
    json_config_path = args['json_config_path']
    try:
        with open(json_config_path, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("File not found")
        raise SystemExit(-1)
    except json.JSONDecodeError:
        print("The file is not a valid JSON file.")
        raise SystemExit(-1)
    except Exception as e:
        print(f"An unspecified error occurred: {e}")
        raise SystemExit(-1)

    si = service_instance.connect(args)
    content = si.RetrieveContent()
    datacenter = content.rootFolder.childEntity[0]
    datastore = datacenter.datastore[0]
    
    spec = vim.vm.ConfigSpec()
    spec.name = data['vm_name']
    spec.memoryMB = data['memory']  # Spécifier la mémoire (en Mo) pour la machine virtuelle
    spec.numCPUs = data['num_cpus'] 
    spec.deviceChange = []
    # Ajouter un contrôleur à la machine virtuelle
    controller_spec = vim.vm.device.VirtualDeviceSpec()
    controller_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.add
    controller_spec.device = vim.vm.device.ParaVirtualSCSIController()
    controller_spec.device.sharedBus = vim.vm.device.VirtualSCSIController.Sharing.noSharing
    
    # Ajouter le contrôleur à la configuration de la machine virtuelle
    spec.deviceChange.append(controller_spec)

    cd_spec = vim.vm.device.VirtualDeviceSpec()
    cd_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.add
    cd_spec.device = vim.vm.device.VirtualCdrom()
    cd_spec.device.key = 2000
    cd_spec.device.backing = vim.vm.device.VirtualCdrom.IsoBackingInfo()
    cd_spec.device.backing.fileName = data['iso_path']
    cd_spec.device.connectable = vim.vm.device.VirtualDevice.ConnectInfo()
    cd_spec.device.connectable.startConnected = True
    cd_spec.device.connectable.connected = False
    spec.deviceChange.append(cd_spec)

    # Créer la spécification du disque dur
    disk_spec = vim.vm.device.VirtualDeviceSpec()
    disk_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.add
    disk_spec.device = vim.vm.device.VirtualDisk()
    disk_spec.device.backing = vim.vm.device.VirtualDisk.FlatVer2BackingInfo()
    disk_spec.device.backing.diskMode = data['disk_mode']
    disk_spec.device.backing.thinProvisioned = True
    disk_spec.device.backing.datastore = datastore
    disk_spec.device.unitNumber = data['unit_number']
    disk_spec.device.capacityInKB = data['capacity']  # Spécifier la capacité du disque dur (en KB)
    spec.deviceChange.append(disk_spec)

    files = vim.vm.FileInfo()
    files.vmPathName = "["+datastore.name+"]"+data['vm_name']
    files.logDirectory=data['log_directory']
    files.snapshotDirectory=data['snapshot_directory']
    files.suspendDirectory=data['suspend_directory']
    spec.files = files



    vmfolder = datacenter.vmFolder
    print(spec)
    #vm = vmfolder.CreateVM_Task(config=spec, pool=datacenter.hostFolder.childEntity[0].resourcePool)
    try:
        WaitForTask(vmfolder.CreateVM_Task(config=spec, pool=datacenter.hostFolder.childEntity[0].resourcePool))
        print("VM created: %s" % data['vm_name'])
    except vim.fault.DuplicateName:
        print("VM duplicate name: %s" % data['vm_name'], file=sys.stderr)
    except vim.fault.AlreadyExists:
        print("VM name %s already exists." % data['vm_name'], file=sys.stderr)
        #print("Virtual Machine {} created successfully".format(vm_name))

# Call the function with the appropriate parameters
#iso_path="https://192.168.8.101/folder/test.iso?dcPath=ha-datacenter&dsName=datastore1&VMware-CSRF-Token=7jons1lr0ga4ifx9vxm0btlxugydne0v"
#iso_path = "https://192.168.8.101/folder/test.iso?dcPath=ha-datacenter&dsName=datastore1"
#iso_path="https://192.168.8.101/folder/test.iso"
#iso_path="[datastore1] test.iso"
#create_vm_from_iso('192.168.8.101', 'root', '2002romial', iso_path, 'test_iso')
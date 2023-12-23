import sys
from pyVmomi import vim
from pyVim.task import WaitForTask
from utils import helper, service_instance



def get_dc(si, name):
    for datacenter in si.content.rootFolder.childEntity:
        if datacenter.name == name:
            return datacenter
    raise Exception('Failed to find datacenter named %s' % name)


# Returns the first cdrom if any, else None.
def get_physical_cdrom(host):
    for lun in host.configManager.storageSystem.storageDeviceInfo.scsiLun:
        if lun.lunType == 'cdrom':
            return lun
    return None


def find_free_ide_controller(vm):
    for dev in vm.config.hardware.device:
        if isinstance(dev, vim.vm.device.VirtualIDEController):
            # If there are less than 2 devices attached, we can use it.
            if len(dev.device) < 2:
                return dev
    return None


def find_device(vm, device_type):
    result = []
    for dev in vm.config.hardware.device:
        if isinstance(dev, device_type):
            result.append(dev)
    return result


def new_cdrom_spec(controller_key, backing):
    connectable = vim.vm.device.VirtualDevice.ConnectInfo()
    connectable.allowGuestControl = True
    connectable.startConnected = True

    cdrom = vim.vm.device.VirtualCdrom()
    cdrom.controllerKey = controller_key
    cdrom.key = -1
    cdrom.connectable = connectable
    cdrom.backing = backing
    return cdrom

def create_cd_rom(si,iso_path,vm_name):
    datacenter = si.content.rootFolder.childEntity[0]

    vm = si.content.searchIndex.FindChild(datacenter.vmFolder, vm_name)
    
    if vm is None:
        raise Exception('Failed to find VM %s in datacenter %s' %
                        ("vm_iso", datacenter.name))

    controller = find_free_ide_controller(vm)
    if controller is None:
        raise Exception('Failed to find a free slot on the IDE controller')

    cdrom = None

    cdrom_lun = get_physical_cdrom(vm.runtime.host)
    if cdrom_lun is not None:
        backing = vim.vm.device.VirtualCdrom.AtapiBackingInfo()
        backing.deviceName = cdrom_lun.deviceName
        device_spec = vim.vm.device.VirtualDeviceSpec()
        device_spec.device = new_cdrom_spec(controller.key, backing)
        device_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.add
        config_spec = vim.vm.ConfigSpec(deviceChange=[device_spec])
        WaitForTask(vm.Reconfigure(config_spec))

        cdroms = find_device(vm, vim.vm.device.VirtualCdrom)
        # TODO isinstance(x.backing, type(backing))
        cdrom = next(filter(lambda x: type(x.backing) == type(backing) and
                     x.backing.deviceName == cdrom_lun.deviceName, cdroms))
    else:
        print('Skipping physical CD-Rom test as no device present.')

    cdrom_operation = vim.vm.device.VirtualDeviceSpec.Operation
    #iso = args.iso
    if iso_path is not None:
        device_spec = vim.vm.device.VirtualDeviceSpec()
        if cdrom is None:  # add a cdrom
            backing = vim.vm.device.VirtualCdrom.IsoBackingInfo(fileName=iso_path)
            cdrom = new_cdrom_spec(controller.key, backing)
            device_spec.operation = cdrom_operation.add
        else:  # edit an existing cdrom
            backing = vim.vm.device.VirtualCdrom.IsoBackingInfo(fileName=iso_path)
            cdrom.backing = backing
            device_spec.operation = cdrom_operation.edit
        device_spec.device = cdrom
        config_spec = vim.vm.ConfigSpec(deviceChange=[device_spec])
        WaitForTask(vm.Reconfigure(config_spec))

        cdroms = find_device(vm, vim.vm.device.VirtualCdrom)
        # TODO isinstance(x.backing, type(backing))
        cdrom = next(filter(lambda x: type(x.backing) == type(backing) and
                     x.backing.fileName == iso_path, cdroms))
    else:
        print('Skipping ISO test as no iso provided.')


def create_vm(si, vm_name, datacenter_name, host_ip, datastore_name=None,iso_path=None):

    content = si.RetrieveContent()
    destination_host = helper.get_obj(content, [vim.HostSystem], host_ip)
    source_pool = destination_host.parent.resourcePool
    if datastore_name is None:
        datastore_name = destination_host.datastore[0].name

    config = create_config_spec(datastore_name=datastore_name, name=vm_name)
    datacenter = si.content.rootFolder.childEntity[0]
    #datacenter = helper.get_obj(content, [vim.Datacenter], datacenter_name)
    for child in content.rootFolder.childEntity:
        if child.name == datacenter.name:
            vm_folder = child.vmFolder  # child is a datacenter
            break
    else:
        print("Datacenter %s not found!" % datacenter_name)
        sys.exit(1)

    try:
        WaitForTask(vm_folder.CreateVm(config, pool=source_pool, host=destination_host))
        print("VM created: %s" % vm_name)
        #Create cdrom
        create_cd_rom(si,iso_path,vm_name)
    except vim.fault.DuplicateName:
        print("VM duplicate name: %s" % vm_name, file=sys.stderr)
    except vim.fault.AlreadyExists:
        print("VM name %s already exists." % vm_name, file=sys.stderr)


def create_config_spec(datastore_name, name, memory=256, guest="ubuntuGuest",
                       annotation="Sample", cpus=1):
    #debian9_64Guest
    config = vim.vm.ConfigSpec()
    config.annotation = annotation
    config.memoryMB = int(memory)
    config.guestId = guest
    config.name = name
    config.numCPUs = cpus
    files = vim.vm.FileInfo()
    files.vmPathName = "["+datastore_name+"]"
    config.files = files
    return config

def main():
    args = {
            "host":"192.168.100.204",
            "user":"root",
            "pwd":"2002romial",
            "disable_ssl_verification":True
        }
    si = service_instance.connect(args)
    create_vm(
                si=si, 
                vm_name="vm_iso", 
                datacenter_name=None, 
                host_ip="localhost.localdomain", 
                datastore_name=None,
                iso_path='[datastore1] test/Core-5.4.iso')



if __name__ == "__main__":
    main()
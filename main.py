from pyVim import connect
from pyVmomi import vim

host = 'your_esxi_host'
user = 'your_username'
password = 'your_password'

connection = connect.SmartConnectNoSSL(host=host, user=user, pwd=password)
content = connection.RetrieveContent()

def create_vm(vm_name, datacenter_name, cluster_name, datastore_name, vm_folder, cpu_count, memory_mb, network_name):
    vm_folder = content.viewManager.CreateContainerView(content.rootFolder, [vim.Folder], True).view[0]
    datacenter = content.rootFolder.childEntity[0]
    cluster = datacenter.hostFolder.childEntity[0]
    resource_pool = cluster.resourcePool
    datastore = [ds for ds in datacenter.datastore if ds.summary.name == datastore_name][0]
    network = [net for net in datacenter.network if net.name == network_name][0]

    vm_config = vim.vm.ConfigSpec(name=vm_name, numCPUs=cpu_count, memoryMB=memory_mb, guestId='otherGuest')
    vm_create_spec = vim.vm.FileInfo(logDirectory=None, snapshotDirectory=None, suspendDirectory=None, vmPathName='[' + datastore.name + ']')
    vm_file_spec = vim.vm.FileInfo(logDirectory=None, snapshotDirectory=None, suspendDirectory=None, vmPathName='[' + datastore.name + ']')
    
    clone_spec = vim.vm.RelocateSpec(datastore=datastore, pool=resource_pool)
    clone_spec.config = vm_create_spec
    clone_spec.datastore = datastore
    clone_spec.diskMoveType = 'createNewChildDiskBacking'
    clone_spec.host = None

    vm = vm_folder.CreateVM_Task(config=vm_config, pool=resource_pool, host=resource_pool.host[0])
    
    return vm

def delete_vm(vm_name):
    vm = content.searchIndex.FindByInventoryPath(vm_name)
    if vm:
        vm.Destroy_Task()
    else:
        print("Virtual machine not found")

def power_on_vm(vm_name):
    vm = content.searchIndex.FindByInventoryPath(vm_name)
    if vm:
        vm.PowerOn()
    else:
        print("Virtual machine not found")

def deploy_vm(template_name, vm_name, datacenter_name, cluster_name, datastore_name, vm_folder):
    root_res_pool = content.rootFolder.childEntity[0].resourcePool
    template = content.searchIndex.FindByInventoryPath(template_name)
    dest_folder = content.searchIndex.FindByInventoryPath(vm_folder)

    relocate_spec = vim.vm.RelocateSpec()
    relocate_spec.datastore = content.searchIndex.FindByInventoryPath(datastore_name)
    relocate_spec.pool = root_res_pool

    clone_spec = vim.vm.CloneSpec(powerOn=True, template=False, location=relocate_spec)
    task = template.Clone(folder=dest_folder, name=vm_name, spec=clone_spec)

    return task

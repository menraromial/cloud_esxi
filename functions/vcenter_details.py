from pyVmomi import vmodl
from pyVmomi import vim

from utils import service_instance, vm


def parse_service_instance(si):
    """
    Print some basic knowledge about your environment as a Hello World
    equivalent for pyVmomi
    """

    content = si.RetrieveContent()
    object_view = content.viewManager.CreateContainerView(content.rootFolder,
                                                          [], True)
    for obj in object_view.view:
        print(obj)
        if isinstance(obj, vim.VirtualMachine):
            vm.print_vm_info(obj)

    object_view.Destroy()
    return 0


def main(args):
    """
    Simple command-line program for listing the virtual machines on a system.
    """


    try:
        si = service_instance.connect(args)

        # ## Do the actual parsing of data ## #
        parse_service_instance(si)

    except vmodl.MethodFault as ex:
        print("Caught vmodl fault : {}".format(ex.msg))
        return -1

    return 0

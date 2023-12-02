import questionary
import sys
from functions import deploy_ova, renamer,getallvms,\
    list_datastores, destroy_vm, vcenter_details,vm_power_on,\
    upload_file,create_from_iso
import json

if __name__=="__main__":

    """
    The main function of the VM Deployment Application.
    This function displays a welcome message and provides a menu of available options for managing virtual machines.
    It prompts the user for input and executes the corresponding actions based on the user's choice.
    """
    print("Welcome to the VM Deployment Application!")
    print("========================================")
    print("")

    choices = ["Deploy Vm from ova file", 
            "Create VM from iso file", 
            "Get All VM",
            "Rename VM",
            "List datastore",
            "Upload File",
            "Destroy VM",
            "Vcenter details",
            "Vm power on",
            "Deploy vm to many esxi",
            "Exit"
    ]



    host = questionary.text("Enter the host").ask()
    user = questionary.text("Enter the username").ask()
    pwd = questionary.password("Your password").ask()
    ssl = questionary.confirm("Disable SSL ?").ask()

    #Default args for connection(all are required)
    args = {
            "host":host,
            "user":user,
            "pwd":pwd,
            "disable_ssl_verification":ssl
        }

    choice = "Get All VM" # Default choice

    while choice != "Exit":
        choice = questionary.select(
            "What do you want to do?",
            choices=choices,
            use_indicator=True
        ).ask()
        
        choice=str(choice).strip()
        #The deploy need another arguments (ova path, datacenter name, resource pool, datastore name)
        if choice == "Deploy Vm from ova file":
            json_path = questionary.path("Enter the config file path").ask()
            #Try to read the json file and get configurations
            try:
                with open(json_path, 'r') as f:
                    
                    data = json.load(f)
                    args['ova_path']=data['ova_path']
                    args['datacenter_name']=data['datacenter_name']
                    args['resource_pool']=data['resource_pool']
                    args['datastore_name']=data['datastore_name']
                    num_instance = data['num_instance']
                    for _ in range(num_instance):
                        deploy_ova.main(args)
                    print(args)
            except FileNotFoundError:
                print("The file was not found.")
            except json.JSONDecodeError:
                print("The file is not a valid JSON file.")
            except Exception as e:
                print(f"An unspecified error occurred: {e}")
                
        elif choice=="Create VM from iso file":
            json_config_path = questionary.path("Enter the json config file path").ask()
            args['json_config_path']=json_config_path
            create_from_iso.main(args)

        elif choice=="List datastore":
            json = questionary.confirm("Output to JSON ?").ask()
            args['json']=json
            list_datastores.main(args)
        
        elif choice=="Rename VM":
            name = questionary.text("What is the vm name ?").ask()
            new_name = questionary.text("what is the new name ?").ask()
            args['name']=name
            args['new_name']=new_name
            renamer.renamer(args)

        elif choice=="Get All VM":
            find = questionary.text("Enter the name if you want to find by name").ask()
            args['find']=find
            getallvms.main(args)

        elif choice=="Destroy VM":
            vm_name = questionary.text('Find vm by name ?').ask()
            uuid = questionary.text('Find vm by uuid ?').ask()
            dns_name = questionary.text('Find vm by DNS name ?').ask()
            vm_ip = questionary.text('Find vm by IP address ?').ask()
            args['vm_name']=vm_name
            args['uuid']=uuid
            args['dns_name']=dns_name
            args['vm_ip']=vm_ip
            destroy_vm.main(args)

        elif choice=="Vcenter details":
            vcenter_details.main(args)

        elif choice=="Vm power on":
            vm_name= questionary.text('Names of the Virtual Machines to power on').ask()
            args['vm_name']=vm_name
            vm_power_on.main(args)
        
        elif choice=="Upload File":
            datastore_name = questionary.text('Enter the datastore name').ask()
            remote_file_path = questionary.path('Enter the remote file path').ask()
            local_file_path = questionary.path('Enter the local file path').ask()
            args['datastore_name']=datastore_name
            args['remote_file_path']=remote_file_path
            args['local_file_path']=local_file_path
            upload_file.main(args)
        
        elif choice == "Deploy vm to many esxi":
            json_path = questionary.path("Enter the json config file path").ask()
            #Try to read the json file and get configurations
            try:
                with open(json_path, 'r') as f:
                    data = json.load(f)
                    for key,value in data.items():
                        deploy_ova.main(value)
            except FileNotFoundError:
                print("The file was not found.")
            except json.JSONDecodeError:
                print("The file is not a valid JSON file.")
            except Exception as e:
                print(f"An unspecified error occurred: {e}")

        else:
            sys.exit(1)



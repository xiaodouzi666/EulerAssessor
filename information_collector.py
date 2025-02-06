import os
import json
import platform
import subprocess


def collect_system_info(output_file="system_info.json"):
    """
    Collect system information and save to a JSON file.
    """
    system_info = {}
    
    try:
        # Common information
        system_info["os_version"] = platform.system() + " " + platform.release()
        system_info["kernel_version"] = platform.version()
        system_info["architecture"] = platform.architecture()[0]
        system_info["hostname"] = platform.node()

        if platform.system() == "Linux":
            # Linux-specific information
            system_info["cpu_info"] = subprocess.getoutput("lscpu")
            system_info["memory_info"] = subprocess.getoutput("free -h")
            system_info["disk_info"] = subprocess.getoutput("lsblk -o NAME,FSTYPE,SIZE,MOUNTPOINT")
            system_info["network_info"] = subprocess.getoutput("ss -tuln")
            system_info["services_info"] = subprocess.getoutput("systemctl list-units --type=service --state=running")
            system_info["pci_devices"] = subprocess.getoutput("lspci")
            system_info["usb_devices"] = subprocess.getoutput("lsusb")
            system_info["drivers"] = subprocess.getoutput("lsmod")
            system_info["processes"] = subprocess.getoutput("ps -aux")
            try:
                with open("/etc/fstab", "r") as f:
                    system_info["fstab"] = f.read()
            except FileNotFoundError:
                system_info["fstab"] = "No /etc/fstab file found."

        elif platform.system() == "Windows":
            # Windows-specific information
            system_info["cpu_info"] = subprocess.getoutput("wmic cpu get Name,NumberOfCores,MaxClockSpeed /format:list")
            system_info["memory_info"] = subprocess.getoutput("wmic OS get TotalVisibleMemorySize,FreePhysicalMemory /format:list")
            system_info["disk_info"] = subprocess.getoutput("wmic logicaldisk get name,freespace,size /format:list")
            system_info["network_info"] = subprocess.getoutput("netstat -ano")
            system_info["services_info"] = subprocess.getoutput("powershell Get-Service | Format-Table -AutoSize")

        # Environment variables
        system_info["environment_variables"] = dict(os.environ)

        # Save to JSON
        with open(output_file, "w") as json_file:
            json.dump(system_info, json_file, indent=4, ensure_ascii=False)
        print(f"System information collected and saved to {output_file}.")
    
    except Exception as e:
        print(f"Error collecting system information: {e}")


# Example usage
if __name__ == "__main__":
    collect_system_info()

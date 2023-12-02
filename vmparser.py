# vmparser created by Jason Canfield
"""Modules for main os related actions"""
import os
import subprocess
import gzip
import zipfile
import tarfile
import tkinter as tk
from tkinter import filedialog, ttk
from tabulate import tabulate
import requests

selected_folder_path = os.getcwd()
VMWARE_VERSION = ""

# Track build version
BUILDVER = "0.7.5"

# Setup Review Folder for output text files
export_path = "Review"

# Check if the folder exists
if not os.path.exists(export_path):
    # Create the folder
    os.makedirs(export_path)
    print(f"Parsed files will be stored in '{export_path}' Folder.")
else:
    print(f"Parsed files will be stored in '{export_path}' Folder.")

def get_new_version(url):
    """
    Get the version string from the file at the given URL.

    Parameters:
    url (str): The URL of the file to be downloaded.

    Returns:
    str: The content of the file (new version string) if successful, None otherwise.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Ensure the request was successful
        return response.text.strip()
    except Exception as e:
        print(f"An error occurred: {e}")
        return None



def driver_info():
    """Display driver info"""
    module_file_path = os.path.join(selected_folder_path, "commands", "esxcfg-module_-q.txt")
    vib_file_path = os.path.join(selected_folder_path, "commands", "localcli_software-vib-list.txt")
    svtag_path = os.path.join(selected_folder_path, "commands", "smbiosDump.txt")
    driver_file_path = "Review/drivers.txt"

    matching_lines = []
    del_lines = []
    svtag_info = []

    # Read the contents of module file and replace "_" with "-"
    with open(module_file_path, 'r') as esx_file:
        esx_lines = [line.strip().replace("_", "-") for line in esx_file.readlines()]

    # Read the contents of vib_file_path and search for matching lines
    with open(vib_file_path, 'r') as vib_file:
        for line in vib_file:
            if any(esx_line in line for esx_line in esx_lines):
                matching_lines.append(line.strip())
            if "DEL" in line:
                del_lines.append(line.strip())

    # Read svtag info
    with open(svtag_path, 'r') as svtag_file:
        lines = svtag_file.readlines()
        for i, line in enumerate(lines):
            if "System Info" in line:
                svtag_info = lines[i + 1:i + 4]  # Get the next 3 lines
                break

    # Convert svtag_info list to string
    svtag_info_str = ''.join(svtag_info)

    # Display the matching lines and svtag_info in the window
    matching_text.delete(1.0, tk.END)
    matching_text.insert(tk.END, "ESXi version:  \n" + "----------------\n" + VMWARE_VERSION + "\n")
    matching_text.insert(tk.END, "System Info:\n" + "----------------\n" + svtag_info_str + "\n")
    matching_text.insert(tk.END, "Drivers in use:\n" + "----------------\n" + "\n".join(matching_lines))
    matching_text.insert(tk.END, "\n\nDell Packages Installed:\n" + "-------------------------\n" + "\n".join(del_lines))

    # Save the matching lines to the output file
    with open(driver_file_path, 'w') as output_file:
        output_file.write("ESXi version: \n" + VMWARE_VERSION + "\n")
        output_file.write("System Info: \n" + svtag_info_str + "\n")
        output_file.write("Drivers in use: \n" + "\n".join(matching_lines))
        output_file.write("\n\nDell Packages Installed: \n" + "\n".join(del_lines))


def network_info():
    """Display Network files"""
    network_file_path = "Review/network.txt"
    nicinfo_file = selected_folder_path + "/commands/nicinfo.sh.txt"
    vswitch_file = selected_folder_path + "/commands/esxcfg-vswitch_-l.txt"
    vmknic_file = selected_folder_path + "/commands/esxcfg-vmknic_-l.txt"

    matching_text.tag_configure("bold", font=("Arial", 10, "bold"))
    matching_text.delete(1.0, tk.END)

#       Read nicinfo_file contents

    try:
        with open(nicinfo_file, 'r') as file:
            lines = file.readlines()
            for line in lines:
                if 'NIC:' in line:
                    break
                matching_text.insert(tk.END, line.strip() + "\n")

#       Read contents of vmkernel port

        with open(vmknic_file, 'r') as file:
            matching_text.insert(tk.END, "----------------------\n")
            matching_text.insert(tk.END, "    VM Kernel Port Info:       |\n", "bold")
            matching_text.insert(tk.END, "----------------------\n\n")
            lines = file.readlines()
            for line in lines:
                matching_text.insert(tk.END, line.strip() + "\n")
                matching_text.insert(tk.END, "----------------------------------------------------------------------"
                                             "----------------------------------------------------------------------"
                                             "-------------------------------------------------------------------\n")


#       Read vsiwtch_file contents

        with open(vswitch_file, 'r') as file:
            matching_text.insert(tk.END, "\n")
            matching_text.insert(tk.END, "----------------------\n")
            matching_text.insert(tk.END, "         vSwitch Info:              |\n", "bold")
            matching_text.insert(tk.END, "----------------------\n\n")

            # Read the data into a list of lists
            data = [line.strip().split() for line in file]

            # Convert the data into a table
            table = tabulate(data, headers='firstrow', tablefmt='simple')

            # Insert the table into the text widget
            matching_text.insert(tk.END, table + "\n")

        # Save the matching lines to the output file
        with open(network_file_path, 'w') as output_file:
            output_file.write(matching_text.get(1.0, tk.END))

#   Show error if files aren't found
    except FileNotFoundError:
        matching_text.delete(1.0, tk.END)
        matching_text.insert(tk.END, "One of the command files not found.")


def storage_info():
    """Display storage Info"""
    adapters_path = selected_folder_path + "/commands/localcli_storage-core-adapter-list.txt"
    disk_volume_path = selected_folder_path + "/commands/df.txt"
    storage_disks = selected_folder_path + "/commands/localcli_storage-core-path-list.txt"
    nvme_info = selected_folder_path + "/commands/localcli_nvme-namespace-list.txt"
    disk_info = selected_folder_path + "/commands/localcli_storage-core-device-list.txt"
    storage_file_path = "Review/storage.txt"

    adapters_content = ""
    disk_volume_lines = []
    storage_disks_lines = []
    disk_info_lines = []
    nvme_content = ""


#       Make sure things continue when files aren't seen

    try:
        with open(adapters_path, 'r') as adapters_file:
            adapters_content = adapters_file.read()
    except FileNotFoundError:
        matching_text.insert(tk.END, "Adapters file not found.\n")

    try:
        with open(disk_volume_path, 'r') as disk_volume_file:
            disk_volume_lines = disk_volume_file.readlines()
    except FileNotFoundError:
        matching_text.insert(tk.END, "Disk volume file not found.\n")

    try:
        with open(storage_disks, 'r') as storage_disks_file:
            storage_disks_lines = storage_disks_file.readlines()
    except FileNotFoundError:
        matching_text.insert(tk.END, "Storage disks file not found.\n")

    try:
        with open(nvme_info, 'r') as nvme_file:
            nvme_content = nvme_file.read()
    except FileNotFoundError:
        matching_text.insert(tk.END, "NVMe info file not found.\n")

    try:
        with open(disk_info, 'r') as disk_info_file:
            disk_info_lines = disk_info_file.readlines()
    except FileNotFoundError:
        matching_text.insert(tk.END, "Disk info file not found.\n")

    # Configure the tag for bold formatting
    matching_text.tag_configure("bold", font=("Arial", 10, "bold"))

    # Custom lines of text to be displayed above the adapters' content
    custom_header_adapters = [
        "--------------------------------------------------",
        "  === Storage Adapters ===",
        "--------------------------------------------------",
        "",
    ]

    custom_header_storage_disks = [
        "--------------------------------------------------------------------",
        "  === Physical Disk SAS Address ===",
        "--------------------------------------------------------------------",
        "",
    ]

    custom_lines = [
        "------------------------------------------------",
        "   === Mounted Volumes ===     ",
        "------------------------------------------------",
        "",
    ]

    custom_header_nvme_info = [
        "----------------------------------",
        " === NVMe Info ===",
        "----------------------------------",
        "",
    ]

    custom_header_disk_info = [
        "---------------------------------------------------",
        "  === Physical Disk Info ===",
        "---------------------------------------------------",
        "",
    ]

    disk_info_filtered_lines = []
    # Specify the keywords to filter
    disk_keywords = ['Size:', 'Display Name:', 'Vendor', 'Model:', 'Devfs', 'Device Type:', 'Is SSD', 'Is SAS', ]

    for line in disk_info_lines:
        if any(line.lstrip().startswith(keyword) for keyword in disk_keywords):
            disk_info_filtered_lines.append(line)
            if 'Is SAS:' in line:
                disk_info_filtered_lines.append(
                    "-------------------------------------------------------------------------\n")

# -----------------------------------------------------------------------------------------------------

    # Process the disk_volume info and split them into columns
    table_data = []
    for line in disk_volume_lines:
        columns = line.strip().split()
        table_data.append(columns)

    # Format the table
    table = tabulate(table_data, headers='firstrow', tablefmt='grid')

    # Specify the keywords to filter
    keywords = ['Device:', 'Target Identifier:', 'Display Name:', 'Adapter:']

    # Filter the lines based on keywords
    filtered_lines = []
    for line in storage_disks_lines:
        if any(keyword in line for keyword in keywords):
            filtered_lines.append(line)
            if 'Target Identifier:' in line:
                filtered_lines.append("-------------------------------------------------------------------------\n")

    matching_text.delete(1.0, tk.END)

    # Insert the custom headers with the bold tag
    for line in custom_header_adapters:
        matching_text.insert(tk.END, line + "\n", "bold")

    # Insert the adapters_content
    matching_text.insert(tk.END, adapters_content + "\n\n")

    # Insert the custom lines with the bold tag
    for line in custom_lines:
        matching_text.insert(tk.END, line + "\n", "bold")

    # Insert the table
    matching_text.insert(tk.END, table + "\n\n\n")

    # Insert the custom headers for NVMe info with the bold tag
    for line in custom_header_nvme_info:
        matching_text.insert(tk.END, line + "\n", "bold")

    # Insert the NVMe content
    matching_text.insert(tk.END, nvme_content + "\n\n")

    # Insert the custom headers for disk info with the bold tag
    for line in custom_header_disk_info:
        matching_text.insert(tk.END, line + "\n", "bold")

    # Insert the disk info filtered text
    matching_text.insert(tk.END, "\n".join(disk_info_filtered_lines) + "\n\n")

    # Insert the custom headers for storage disks with the bold tag
    for line in custom_header_storage_disks:
        matching_text.insert(tk.END, line + "\n", "bold")

    # Insert the filtered text
    matching_text.insert(tk.END, "\n".join(filtered_lines))

    # Concatenate the lines of text with the file contents for saving to a file
    display_text = "\n".join(custom_header_adapters) + "\n" + adapters_content + "\n\n" + \
                   "\n".join(custom_lines) + "\n" + table + "\n\n\n" + \
                   "\n".join(custom_header_nvme_info) + "\n" + nvme_content + "\n\n" + \
                   "\n".join(custom_header_disk_info) + "\n" + "\n".join(disk_info_filtered_lines) + "\n\n" + \
                   "\n".join(custom_header_storage_disks) + "\n" + "\n".join(filtered_lines)

    # Save the matching lines to the output file
    with open(storage_file_path, 'w') as storage_file:
        storage_file.write(display_text)


def open_folder_explorer():
    """Open review folder using file explorer"""
    # Set Review folder in CWD
    folder_path = os.path.join(os.getcwd(), "Review")
    # Use the 'explorer' command in Windows to open the folder in File Explorer
    subprocess.Popen(f'explorer "{folder_path}"')


def show_filtered_logs():
    """Show vmkernel logs"""
    log_files = []
    log_file_path = selected_folder_path + "/var/run/log/vmkernel"
    filter_text = filter_entry.get()

    # Find and unzip vmkernel log files from vmkernel.0.gz to vmkernel.7.gz
    for i in range(8):
        gz_file_path = log_file_path + "." + str(i) + ".gz"
        if os.path.exists(gz_file_path):
            log_files.append(gz_file_path)
            unzipped_file_path = log_file_path + "_" + str(i)
            with gzip.open(gz_file_path, 'rb') as gz_file:
                with open(unzipped_file_path, 'wb') as unzipped_file:
                    unzipped_file.write(gz_file.read())

    # Find all log files that start with 'vmkernel'
    for file in os.listdir(selected_folder_path + "/var/run/log"):
        if file.startswith("vmkernel"):
            log_files.append(os.path.join(selected_folder_path + "/var/run/log", file))

    filtered_lines = []
    for log_file_path in log_files:
        if log_file_path.endswith(".gz"):
            continue  # Skip the compressed files that were not found

        with open(log_file_path, 'r') as log_file:
            lines = log_file.readlines()

        filtered_lines.extend([line.strip() for line in lines if filter_text in line])

    if filtered_lines:
        matching_text.delete(1.0, tk.END)
        matching_text.insert(tk.END, "\n".join(filtered_lines))
    else:
        matching_text.delete(1.0, tk.END)
        matching_text.insert(tk.END, "No matching lines found.")


def boot_log_info():
    """Show vmksummary boot info"""
    file_path = selected_folder_path + "/var/run/log/vmksummary.log"

    try:
        with open(file_path, 'r') as file:
            matching_lines = []
            for line in file:
                if 'boot' in line:
                    matching_lines.append(line.strip())

        # Display the matching lines in the window
        matching_text.delete(1.0, tk.END)
        matching_text.insert(tk.END, "\n".join(matching_lines))

    except FileNotFoundError:
        matching_text.delete(1.0, tk.END)
        matching_text.insert(tk.END, "File not found: " + file_path)


def vsan_disk_info():
    """Display vsan disk files"""
    file_path = selected_folder_path + "/commands/vdq_-q--H.txt"
    output_file_path = "Review/vsan_output.txt"

    try:
        with open(file_path, 'r') as file:
            # Read the contents of the file
            lines = file.readlines()

        # Configure the tag for red formatting
        matching_text.tag_configure("red", foreground="red")

        # Clear the text box
        matching_text.delete(1.0, tk.END)

        flagged_words = set()  # Store "naa." words flagged red

        for line in lines:
            stripped_line = line.strip()
            if "Size(MB):  0" in stripped_line or "IsPDL?:  1" in stripped_line:
                matching_text.insert(tk.END, stripped_line + "\n", "red")
            else:
                words = stripped_line.split()
                for word in words:
                    if word.startswith('naa.') and word in flagged_words:
                        matching_text.insert(tk.END, word + ' ', 'red')
                    elif "/naa." in word or "error" in stripped_line.lower() or "Failed" in stripped_line:
                        subwords = word.split('/')
                        for subword in subwords:
                            if subword.startswith('naa.'):
                                flagged_words.add(subword)
                                matching_text.insert(tk.END, '/' + subword + ' ', 'red')
                            else:
                                matching_text.insert(tk.END, '/' + subword + ' ')
                        # delete the leading '/' from the text widget
                        matching_text.delete('end - 2c')
                    else:
                        matching_text.insert(tk.END, word + ' ')
                matching_text.insert(tk.END, '\n')

        # Save the content to a separate file
        with open(output_file_path, 'w') as output_file:
            output_file.writelines(lines)

    except FileNotFoundError:
        matching_text.delete(1.0, tk.END)
        matching_text.insert(tk.END, "File not found: " + file_path)


def update_progress(progressbar, value, maximum):
    """Setup progress bar widget"""
    progressbar["value"] = value
    progressbar["maximum"] = maximum
    progressbar.update()


def extract_zip(file_path):
    """Extract ZIP file"""
    matching_text.delete(1.0, tk.END)
    matching_text.insert(tk.END, "Selected File: " + file_path + "\n")

    if not file_path:
        return

    extract_path = os.path.join(os.getcwd(), 'Extracted')

    if not os.path.exists(extract_path):
        os.makedirs(extract_path)

    matching_text.insert(tk.END, "Extracting .zip file...\n")

    tgz_files_extracted = []  # List to store the names of the .tgz files extracted from the .zip

    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        members = zip_ref.namelist()
        total_members = len(members)
        for i, member in enumerate(members):
            with open(os.path.join(extract_path, member), 'wb') as f_out:
                f_out.write(zip_ref.read(member))
            if member.endswith('.tgz'):
                tgz_files_extracted.append(member)  # Add the name of the .tgz file to the list
            update_progress(progress, i + 1, total_members)

        matching_text.insert(tk.END, "Extracted .zip, now extracting .tgz\n\n")

    for file in tgz_files_extracted:  # Only extract the .tgz files that came from the .zip
        with tarfile.open(os.path.join(extract_path, file), errorlevel=1) as tar_ref:
            members = tar_ref.getmembers()
            root_dirs = {member.name.split('/')[0] for member in members if '/' in member.name}  # Get root directories from the .tgz file
            for i, member in enumerate(members):
                    try:
                        member.name = member.name.replace(':', '_')  # Replace colons with underscore
                        tar_ref.extract(member, path=extract_path)
                        update_progress(progress, i + 1, len(members))
                    except FileNotFoundError as e:
                        print(f"File {member.name} not found: {str(e)}")
                    except PermissionError as e:
                        print(f"No permission to extract {member.name}: {str(e)}")
                    except tarfile.TarError as e:
                        print(f"Error occurred while extracting {member.name}: {str(e)}")
                    except Exception as e:
                        print(f"An unexpected error occurred while extracting {member.name}: {str(e)}")

    # messagebox.showinfo("Success", f"Files extracted successfully to {extract_path}")
    # matching_text.insert(tk.END, "Files extracted to" + extract_path + "\n\n")

    # List all directories under the extraction path
    extracted_dirs = [d for d in os.listdir(extract_path) if os.path.isdir(os.path.join(extract_path, d)) and d in root_dirs]

    global selected_folder_path

    # Check if there are any directories in the list
    if extracted_dirs:
        selected_folder_path = os.path.join(extract_path, extracted_dirs[0])
        matching_text.delete(1.0, tk.END)
        matching_text.insert(tk.END, "Extracted folder path is: " + selected_folder_path + "\n\n")
    else:
        matching_text.insert(tk.END, "No directories found inside the extracted path.")
        return

    vm_version_path = selected_folder_path + "/commands/vmware_-vl.txt"
    profile_path = selected_folder_path + "/commands/localcli_software-profile-get.txt"

    try:
        with open(vm_version_path, 'r') as vm_version_file:
            vm_version_content = vm_version_file.read()
        matching_text.insert(tk.END, "Discovered VMware Build:\n")
        matching_text.insert(tk.END, vm_version_content)
        global VMWARE_VERSION
        VMWARE_VERSION = vm_version_content

    except FileNotFoundError:
        matching_text.insert(tk.END, "VM Version file not found.")

    try:
        with open(profile_path, 'r') as profile_file:
            for line in profile_file:
                if "Name:" in line:
                    name = line.strip().split(" ", 1)[1]
                    matching_text.insert(tk.END, "\n")
                    matching_text.insert(tk.END, "Image: " + name)
                    break
    except FileNotFoundError:
        matching_text.insert(tk.END, "\n\nCustom Image not found.")


def extract_tgz(file_path):
    """Extract TGZ file"""

    matching_text.delete(1.0, tk.END)
    matching_text.insert(tk.END, "Selected File: " + file_path + "\n")
    if not file_path:
        return

    extract_path = os.path.join(os.getcwd(), 'Extracted')

    if not os.path.exists(extract_path):
        os.makedirs(extract_path)

    matching_text.insert(tk.END, "Extracting .tgz file...\n")

    with tarfile.open(file_path, 'r') as tar_ref:
        members = tar_ref.getmembers()
        root_dirs = {member.name.split('/')[0] for member in members if
                     '/' in member.name}  # Get root directories from the .tgz file
        for i, member in enumerate(members):
            try:
                member.name = member.name.replace(':', '_')  # Replace colons with underscore
                tar_ref.extract(member, path=extract_path)
                update_progress(progress, i + 1, len(members))
            except FileNotFoundError as e:
                print(f"File {member.name} not found: {str(e)}")
            except PermissionError as e:
                print(f"No permission to extract {member.name}: {str(e)}")
            except tarfile.TarError as e:
                print(f"Error occurred while extracting {member.name}: {str(e)}")
            except Exception as e:
                print(f"An unexpected error occurred while extracting {member.name}: {str(e)}")

    matching_text.insert(tk.END, "Extracted .tgz file.\n\n")

    extracted_dirs = [d for d in os.listdir(extract_path) if os.path.isdir(os.path.join(extract_path, d)) and d in root_dirs]

    global selected_folder_path

    if extracted_dirs:
        selected_folder_path = os.path.join(extract_path, extracted_dirs[0])  # Choose the first matched directory
        matching_text.delete(1.0, tk.END)
        matching_text.insert(tk.END, "Extracted folder path is: " + selected_folder_path + "\n\n")
    else:
        matching_text.insert(tk.END, "No directories found inside the extracted path.")
        return

    vm_version_path = selected_folder_path + "/commands/vmware_-vl.txt"
    profile_path = selected_folder_path + "/commands/localcli_software-profile-get.txt"

    try:
        with open(vm_version_path, 'r') as vm_version_file:
            vm_version_content = vm_version_file.read()
        matching_text.insert(tk.END, "Discovered VMware Build:\n")
        matching_text.insert(tk.END, vm_version_content)
        global VMWARE_VERSION
        VMWARE_VERSION = vm_version_content

    except FileNotFoundError:
        matching_text.insert(tk.END, "VM Version file not found.")

    try:
        with open(profile_path, 'r') as profile_file:
            for line in profile_file:
                if "Name:" in line:
                    name = line.strip().split(" ", 1)[1]
                    matching_text.insert(tk.END, "\n")
                    matching_text.insert(tk.END, "Image: " + name)
                    break
    except FileNotFoundError:
        matching_text.insert(tk.END, "\n\nCustom Image not found.")


def browse_file():
    """chose a ZIP or TGZ file to extract"""
    # Open a file dialog and ask the user to select a .zip or .tgz file
    file_path = filedialog.askopenfilename(filetypes=(("Zip Files", "*.zip"), ("Tgz Files", "*.tgz"),))

    # Return if no file was selected
    if not file_path:
        return

    # Get the extension of the selected file
    _, file_extension = os.path.splitext(file_path)

    # Based on the file extension, call the appropriate function
    if file_extension == '.zip':
        extract_zip(file_path)
    elif file_extension == '.tgz':
        extract_tgz(file_path)


def browse_folder():
    """Browse to vmbundle folder"""
    folder_path = filedialog.askdirectory()
    if folder_path:
        # Do something with the selected folder path
        matching_text.delete(1.0, tk.END)
        matching_text.insert(tk.END, "Selected folder path: " + folder_path + "\n\n")

        # You can store the path in a variable for later use
        global selected_folder_path
        selected_folder_path = folder_path
        vm_version_path = selected_folder_path + "/commands/vmware_-vl.txt"
        profile_path = selected_folder_path + "/commands/localcli_software-profile-get.txt"

        try:
            with open(vm_version_path, 'r') as vm_version_file:
                vm_version_content = vm_version_file.read()
            matching_text.insert(tk.END, "Discovered VMware Build:\n")
            matching_text.insert(tk.END, vm_version_content)
            global VMWARE_VERSION
            VMWARE_VERSION = vm_version_content

        except FileNotFoundError:
            matching_text.insert(tk.END, "VM Version file not found.")

        try:
            with open(profile_path, 'r') as profile_file:
                for line in profile_file:
                    if "Name:" in line:
                        name = line.strip().split(" ", 1)[1]
                        matching_text.insert(tk.END, "\n")
                        matching_text.insert(tk.END, "Image: " + name)
                        break
        except FileNotFoundError:
            matching_text.insert(tk.END, "\n\nCustom Image not found.")


# Check for a new version at the start of the program
url = "http://100.92.104.204/vmparser.txt"  # Replace with the actual URL
current_version = BUILDVER  # Using the BUILDVER variable from your code

new_version = get_new_version(url)
if new_version and new_version != current_version:
    tk.messagebox.showinfo("Update Available", f"A newer version ({new_version}) of the application is available.")

# Create Window
root = tk.Tk()

# Set the title
root.title("VM Log Parser  " + BUILDVER)

# Create the text box for displaying
matching_text = tk.Text(root, height=50, width=220, background="light gray")
matching_text.grid(row=0, column=0, padx=10, pady=10)

# Create a vertical scroll bar
scrollbar = tk.Scrollbar(root, command=matching_text.yview)
scrollbar.grid(row=0, column=1, sticky='ns')
matching_text.config(yscrollcommand=scrollbar.set)

# Create the bottom button row
top_button_frame = tk.Frame(root)
top_button_frame.grid(row=1, column=0, padx=10, pady=10)

# Progressbar widget
progress = ttk.Progressbar(root, orient="horizontal", length=200)
progress.grid(row=1, column=0, sticky='w', padx=10, pady=10)

# --------------------------------- Create Buttons ---------------------------------

# Create the "Browse" button
browse_button = ttk.Button(top_button_frame, text="Browse", command=browse_folder, style="Custom.TButton")
browse_button.pack(side="left", padx=(1, 10), pady=10)

# Extract Zip file button
browse_button = ttk.Button(top_button_frame, text="Extract Bundle", command=browse_file, style="Custom.TButton")
browse_button.pack(side="left", padx=(1, 10), pady=10)

# Create a separator widget
separator = ttk.Separator(top_button_frame, orient="vertical")
separator.pack(side="left", padx=55, pady=10)

# Create the "Drivers" button
driver_button = ttk.Button(top_button_frame, text="Drivers", command=driver_info, style="Custom.TButton")
driver_button.pack(side="left", padx=5, pady=10)

# Create the "Network" button
network_button = ttk.Button(top_button_frame, text="Network", command=network_info, style="Custom.TButton")
network_button.pack(side="left", padx=5, pady=10)

# Create the "Storage Info" button
storage_button = ttk.Button(top_button_frame, text="Storage Info", command=storage_info, style="Custom.TButton")
storage_button.pack(side="left", padx=5, pady=10)

# Create the "VSAN Disk" button
button4 = ttk.Button(top_button_frame, text="VSAN Disks", style="Custom.TButton", command=vsan_disk_info)
button4.pack(side="left", padx=5, pady=10)

# Create the "Boot Log" button
button5 = ttk.Button(top_button_frame, text="Boot Log", style="Custom.TButton", command=boot_log_info)
button5.pack(side="left", padx=5, pady=10)

# Create the "Show Logs" button
show_logs_button = ttk.Button(top_button_frame, text="Show Logs", command=show_filtered_logs, style="Custom.TButton")
show_logs_button.pack(side="left", padx=5, pady=10)

# Create the filter entry box
filter_entry = tk.Entry(top_button_frame, width=40)
filter_entry.pack(side="left", padx=5, pady=10)

# Bind the <Return> event to the filter entry box
filter_entry.bind('<Return>', lambda event: show_filtered_logs())

# Create the "Review Folder" button
review_button = ttk.Button(top_button_frame, text="Review Folder", command=open_folder_explorer, style="Custom.TButton")
review_button.pack(side="left", padx=10, pady=10)

# Configure the button style
style = ttk.Style()
style.configure("Custom.TButton", foreground="black", background="white", font=("Arial", 10))
# --------------------------------- End Buttons ---------------------------------


# Welcome Message to show at start
matching_text.insert(tk.END, "Welcome to VMware Log parser!" + "\n\n")
matching_text.insert(tk.END, "You can start by Extracting your ZIP/TGZ file or Browse to an already "
                             "extracted bundle folder" + "\n\n")

# Start the main loop
root.mainloop()

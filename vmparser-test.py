import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from tabulate import tabulate
import os
import subprocess
import gzip
import zipfile
import tarfile

selected_folder_path = os.getcwd()
vmware_version = ""

BUILDVER = "0.5.9"

# Setup Review Folder for output text files
export_path = "Review"

# Check if the folder exists
if not os.path.exists(export_path):
    # Create the folder
    os.makedirs(export_path)
    print(f"Parsed files will be stored in '{export_path}' Folder.")
else:
    print(f"Parsed files will be stored in '{export_path}' Folder.")


def driver_info():
    module_file_path = os.path.join(selected_folder_path, "commands", "esxcfg-module_-q.txt")
    vib_file_path = os.path.join(selected_folder_path, "commands", "localcli_software-vib-list.txt")
    driver_file_path = "Review/drivers.txt"

    matching_lines = []

    # Read the contents of module file and replace "_" with "-"
    with open(module_file_path, 'r') as esx_file:
        esx_lines = [line.strip().replace("_", "-") for line in esx_file.readlines()]

    # Read the contents of vib_file_path and search for matching lines
    with open(vib_file_path, 'r') as vib_file:
        for line in vib_file:
            if any(esx_line in line for esx_line in esx_lines):
                matching_lines.append(line.strip())

    # Display the matching lines in the window
    matching_text.delete(1.0, tk.END)
    matching_text.insert(tk.END, "ESXi version:  \n" + "----------------\n" + vmware_version + "\n")
    matching_text.insert(tk.END, "Drivers in use:\n" + "----------------\n" + "\n".join(matching_lines))

    # Save the matching lines to the output file
    with open(driver_file_path, 'w') as output_file:
        output_file.write("Drivers in use: \n" + "\n".join(matching_lines))


def network_info():
    network_file_path = "Review/network.txt"
    nicinfo_file = selected_folder_path + "/commands/nicinfo.sh.txt"
    vswitch_file = selected_folder_path + "/commands/esxcfg-vswitch_-l.txt"
    vmknic_file = selected_folder_path + "/commands/esxcfg-vmknic_-l.txt"

    try:
        with open(nicinfo_file, 'r') as file:
            lines = file.readlines()
            matching_lines = []
            for line in lines:
                if 'NIC:' in line:
                    break
                matching_lines.append(line.strip())

        with open(vmknic_file, 'r') as file:
            matching_lines.append("                       ")
            matching_lines.append("VM Kernel Port Info:")
            matching_text.insert(tk.END, "VM Kernel Port Info:\n")
            matching_lines.append("_______________________")
            matching_lines.append("")
            lines = file.readlines()
            for line in lines:
                matching_lines.append(line.strip())
                matching_lines.append("--------------------------------------------------------------------------"
                                      "--------------------------------------------------------------------------"
                                      "-------------------------------------------------------------")

        with open(vswitch_file, 'r') as file:
            matching_lines.append("")
            matching_lines.append("                       ")
            matching_lines.append("vSwitch Info:")
            matching_lines.append("_______________________")
            matching_lines.append("")
            lines = file.readlines()
            for line in lines:
                matching_lines.append(line.strip())
                matching_lines.append("--------------------------------------------------------------------------"
                                      "-------------")

        # Display the matching lines in the window
        matching_text.delete(1.0, tk.END)
        matching_text.insert(tk.END, "\n".join(matching_lines))

        # Save the matching lines to the output file
        with open(network_file_path, 'w') as output_file:
            output_file.write("\n".join(matching_lines))
    except FileNotFoundError:
        matching_text.delete(1.0, tk.END)
        matching_text.insert(tk.END, "One of the command files not found.")


def storage_info():
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

# -----------------------------------------------------------------------------------------------------
#       Make sure things continue when files aren't seen
# -----------------------------------------------------------------------------------------------------
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

# -----------------------------------------------------------------------------------------------------
#   Creating Headers for the display
# -----------------------------------------------------------------------------------------------------
    # Custom lines of text to be displayed above the adapters' content
    custom_header_adapters = [
        "=== Storage Adapters ===",
        "------------------------",
        "",
    ]

    # Custom lines of text to be displayed above the storage disks' content
    custom_header_storage_disks = [
        "=== Physical Disk Path ===",
        "---------------------------",
        "",
    ]

    # Custom lines of text to be displayed between the files' content
    custom_lines = [
        "=== Mounted Volumes ===",
        "-----------------------",
        "",
    ]

    # Custom lines of text to be displayed above the nvme_info content
    custom_header_nvme_info = [
        "=== NVMe Info ===",
        "-----------------",
        "",
    ]

    # Custom lines of text to be displayed above the disk_info content
    custom_header_disk_info = [
        "=== Disk Info ===",
        "-----------------",
        "",
    ]
# -----------------------------------------------------------------------------------------------------
    # Filter the lines based on keywords for disk_info

    disk_info_filtered_lines = []
    # Specify the keywords to filter
    disk_keywords = ['Size:', 'Display Name:', 'Vendor', 'Model:', 'Devfs', 'Device Type:', 'Is SSD', 'Is SAS', ]

    # Filter the lines based on keywords
    filtered_lines = []

    for line in disk_info_lines:
        if any(line.lstrip().startswith(keyword) for keyword in disk_keywords):
            disk_info_filtered_lines.append(line)
            if 'Is SAS:' in line:
                disk_info_filtered_lines.append(
                    "-------------------------------------------------------------------------\n")

    # Create disk_info variable with filtered text
    disk_info_filtered_text = "\n".join(custom_header_disk_info) + "\n" + "\n".join(disk_info_filtered_lines)
# -----------------------------------------------------------------------------------------------------
    # Read the contents of disk_volume_path
    with open(disk_volume_path, 'r') as disk_volume_file:
        disk_volume_lines = disk_volume_file.readlines()

    # Process the lines and split them into columns
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

    # Concatenate the lines of text with the filtered lines
    filtered_text = "\n".join(custom_header_storage_disks) + "\n" + "\n".join(filtered_lines)
# -----------------------------------------------------------------------------------------------------
#           Display contents of all variables to text window
# -----------------------------------------------------------------------------------------------------
    # Concatenate the lines of text with the file contents
    display_text = "\n".join(custom_header_adapters) + "\n" + adapters_content + "\n\n" + \
                   "\n".join(custom_lines) + "\n" + table + "\n\n\n" + \
                   "\n".join(custom_header_nvme_info) + "\n" + nvme_content + "\n\n" + \
                   disk_info_filtered_text + "\n\n" + \
                   filtered_text

    # Display the matching lines in the window
    matching_text.delete(1.0, tk.END)
    matching_text.insert(tk.END, display_text)

    # Save the matching lines to the output file
    with open(storage_file_path, 'w') as storage_file:
        storage_file.write(display_text)
# -----------------------------------------------------------------------------------------------------


# Open Review Folder
def open_folder_explorer():
    # Set Review folder in CWD
    folder_path = os.path.join(os.getcwd(), "Review")
    # Use the 'explorer' command in Windows to open the folder in File Explorer
    subprocess.Popen(f'explorer "{folder_path}"')


# Show vmkernel logs
def show_filtered_logs():
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

# Show version Info
# def version_show_info():
    # matching_text.delete(1.0, tk.END)
    # matching_text.insert(tk.END, "Show version info:  \n" + vmware_version + "\n\n")


def boot_log_info():
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
                    elif ("/naa." in word or "error" in stripped_line.lower() or "Failed" in stripped_line):
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
    progressbar["value"] = value
    progressbar["maximum"] = maximum
    progressbar.update()


# Extract ZIP file
def extract_zip(file_path):
    matching_text.delete(1.0, tk.END)
    matching_text.insert(tk.END, "Selected File: " + file_path + "\n")
 #   file_path = filedialog.askopenfilename(filetypes=(("Zip Files", "*.zip"),))
    if not file_path:
        return

    extract_path = os.path.join(os.getcwd(), 'Extracted')

    if not os.path.exists(extract_path):
        os.makedirs(extract_path)

    matching_text.insert(tk.END, "Extracting .zip file...\n")

    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        members = zip_ref.namelist()
        total_members = len(members)
        for i, member in enumerate(members):
            with open(os.path.join(extract_path, member), 'wb') as f_out:
                f_out.write(zip_ref.read(member))
            update_progress(progress, i + 1, total_members)

        matching_text.insert(tk.END, "Extracted .zip, now extracting .tgz\n\n")

    for file in os.listdir(extract_path):
        if file.endswith('.tgz'):
            with tarfile.open(os.path.join(extract_path, file), errorlevel=1) as tar_ref:
                members = tar_ref.getmembers()
                for i, member in enumerate(members):
                    try:
                        member.name = member.name.replace(':', '_')  # Replace colons with underscore
                        tar_ref.extract(member, path=extract_path)
                        update_progress(progress, i+1, len(members))
                    except Exception as e:
                        print(f"Could not extract {member.name} due to {str(e)}")

    # messagebox.showinfo("Success", f"Files extracted successfully to {extract_path}")
    # matching_text.insert(tk.END, "Files extracted to" + extract_path + "\n\n")

    # List all directories under the extraction path
    extracted_dirs = [d for d in os.listdir(extract_path) if os.path.isdir(os.path.join(extract_path, d))]

    global selected_folder_path

    # Check if there are any directories in the list
    if extracted_dirs:
        # In this example, I'm assuming you want the first directory. Change this if needed.
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
        global vmware_version
        vmware_version = vm_version_content

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


# Extract TGZ file
def extract_tgz(file_path):

    # Display file path
    matching_text.delete(1.0, tk.END)
    matching_text.insert(tk.END, "Selected File: " + file_path + "\n")
#    file_path = filedialog.askopenfilename(filetypes=(("Tgz Files", "*.tgz"),))
    if not file_path:
        return

    extract_path = os.path.join(os.getcwd(), 'Extracted')

    if not os.path.exists(extract_path):
        os.makedirs(extract_path)

    matching_text.insert(tk.END, "Extracting .tgz file...\n")

    with tarfile.open(file_path, 'r') as tar_ref:
        members = tar_ref.getmembers()
        for i, member in enumerate(members):
            try:
                member.name = member.name.replace(':', '_')  # Replace colons with underscore
                tar_ref.extract(member, path=extract_path)
                update_progress(progress, i+1, len(members))
            except Exception as e:
                print(f"Could not extract {member.name} due to {str(e)}")

    matching_text.insert(tk.END, "Extracted .tgz file.\n\n")

#    messagebox.showinfo("Success", f"Files extracted successfully to {extract_path}")

    extracted_dirs = [d for d in os.listdir(extract_path) if os.path.isdir(os.path.join(extract_path, d))]

    global selected_folder_path

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
        global vmware_version
        vmware_version = vm_version_content

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


# chose a ZIP or TGZ file to extract
def browse_file():
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


# Browse to vmbundle folder
def browse_folder():
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
            global vmware_version
            vmware_version = vm_version_content

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

# End of Button contents ---------------------------------------------------#


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

# Create the label
# label_text = "Browse to Extracted Folder -->"
# label = tk.Label(top_button_frame, text=label_text, anchor="e", width=30)
# label.pack(side="left", padx=(15, 1), pady=10)

# Create the "Browse" button
browse_button = ttk.Button(top_button_frame, text="Browse", command=browse_folder, style="Custom.TButton")
browse_button.pack(side="left", padx=(1,10), pady=10)

# Extract Zip file button
browse_button = ttk.Button(top_button_frame, text="Extract Bundle", command=browse_file, style="Custom.TButton")
browse_button.pack(side="left", padx=(1,10), pady=10)

# Extract TGZ file button
# browse_button = ttk.Button(top_button_frame, text="Extract TGZ", command=browse_tgz, style="Custom.TButton")
# browse_button.pack(side="left", padx=(1,15), pady=10)

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

# Create the "Button 4" button
button4 = ttk.Button(top_button_frame, text="VSAN Disks", style="Custom.TButton", command=vsan_disk_info)
button4.pack(side="left", padx=5, pady=10)

# Create the "Button 5" button
button5 = ttk.Button(top_button_frame, text="Boot Log", style="Custom.TButton", command=boot_log_info)
button5.pack(side="left", padx=5, pady=10)

# Create the "Show Logs" button
show_logs_button = ttk.Button(top_button_frame, text="Show Logs", command=show_filtered_logs, style="Custom.TButton")
show_logs_button.pack(side="left", padx=5, pady=10)

# Create the filter entry box
filter_entry = tk.Entry(top_button_frame, width=20)
filter_entry.pack(side="left", padx=5, pady=10)

# Bind the <Return> event to the filter entry box
filter_entry.bind('<Return>', lambda event: show_filtered_logs())

# Create the "Review Folder" button
review_button = ttk.Button(top_button_frame, text="Review Folder", command=open_folder_explorer, style="Custom.TButton")
review_button.pack(side="left", padx=10, pady=10)

# Configure the button style
style = ttk.Style()
style.configure("Custom.TButton", foreground="black", background="white", font=("Arial", 10))

matching_text.insert(tk.END, "Welcome to VMparser!" "\n\n")
matching_text.insert(tk.END, "You can start by Extracting your ZIP/TGZ file or Browse to an already extracted bundle "
                             "folder" "\n\n")

# Start the main loop
root.mainloop()

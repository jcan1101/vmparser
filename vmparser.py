import tkinter as tk
from tkinter import filedialog, ttk
import os
from tabulate import tabulate
import subprocess
import gzip


selected_folder_path = os.getcwd()

BUILDVER = "0.3.9"

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
    module_file_path = selected_folder_path + "/commands/esxcfg-module_-q.txt"
    vib_file_path = selected_folder_path + "/commands/localcli_software-vib-list.txt"
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
    matching_text.insert(tk.END, "\n".join(matching_lines))

    # Save the matching lines to the output file
    with open(driver_file_path, 'w') as output_file:
        output_file.write("\n".join(matching_lines))


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
            matching_lines.append("VM Kernel Port Info:   ")
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
        print(f"One of the files not found.")


def storage_info():
    adapters_path = selected_folder_path + "/commands/localcli_storage-core-adapter-list.txt"
    disk_volume_path = selected_folder_path + "/commands/df.txt"
    storage_disks = selected_folder_path + "/commands/localcli_storage-core-path-list.txt"
    storage_file_path = "Review/storage.txt"

    # Read the contents of adapters_path
    with open(adapters_path, 'r') as adapters_file:
        adapters_content = adapters_file.read()

    # Read the contents of disk_volume_path
    with open(disk_volume_path, 'r') as disk_volume_file:
        disk_volume_lines = disk_volume_file.readlines()

    # Read the contents of storage_disks
    with open(storage_disks, 'r') as storage_disks_file:
        storage_disks_lines = storage_disks_file.readlines()

    # Custom lines of text to be displayed above the adapters' content
    custom_header_adapters = [
        "=== Storage Adapters ===",
        "------------------------",
        "",
    ]

    # Custom lines of text to be displayed above the storage disks' content
    custom_header_storage_disks = [
        "=== Physical Disks ===",
        "----------------------",
        "",
    ]

    # Custom lines of text to be displayed between the files' content
    custom_lines = [
        "=== Mounted Volumes ===",
        "-----------------------",
        "",
    ]

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


    # Format the lines from disk_volume_lines and remove the first column
    # formatted_disk_volume_lines = []
    # for line in disk_volume_lines:
    #    columns = line.strip().split()
    #    formatted_disk_volume_lines.append(" ".join(columns[1:]))

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


    # Concatenate the lines of text with the file contents
    display_text = "\n".join(custom_header_adapters) + "\n" + adapters_content + "\n\n" + \
                   "\n".join(custom_lines) + "\n" + table + "\n\n\n" + \
                   filtered_text

    # Display the matching lines in the window
    matching_text.delete(1.0, tk.END)
    matching_text.insert(tk.END, display_text)

    # Save the matching lines to the output file
    with open(storage_file_path, 'w') as storage_file:
        storage_file.write(display_text)

# Browse to vmbundle folder
def browse_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        # Do something with the selected folder path
        print("Selected folder path:", folder_path)
        # You can store the path in a variable for later use
        global selected_folder_path
        selected_folder_path = folder_path

# Open Review Folder
def open_folder_explorer():
    # Set Review folder in CWD
    folder_path = os.path.join(os.getcwd(), "Review")
    # Use the 'explorer' command in Windows to open the folder in File Explorer
    subprocess.Popen(f'explorer "{folder_path}"')

# Show vmkernel logs
import os

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



# End of Button contents ---------------------------------------------------#


# Create Window
root = tk.Tk()

# Set the title
root.title("VM Log Parser  " + BUILDVER)

# Create the text box for displaying
matching_text = tk.Text(root, height=50, width=220)
matching_text.grid(row=0, column=0, padx=10, pady=10)

# Create a vertical scroll bar
scrollbar = tk.Scrollbar(root, command=matching_text.yview)
scrollbar.grid(row=0, column=1, sticky='ns')
matching_text.config(yscrollcommand=scrollbar.set)

# Create the top button row
top_button_frame = tk.Frame(root)
top_button_frame.grid(row=1, column=0, padx=10, pady=10)

# Create the "Browse" button
browse_button = ttk.Button(top_button_frame, text="Browse", command=browse_folder, style="Custom.TButton")
browse_button.pack(side="left", padx=100, pady=10)

# Create a separator widget
separator = ttk.Separator(top_button_frame, orient="vertical")
separator.pack(side="left", padx=5, pady=10)

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
button4 = ttk.Button(top_button_frame, text="Button 4", style="Custom.TButton")
button4.pack(side="left", padx=5, pady=10)

# Create the "Button 5" button
button5 = ttk.Button(top_button_frame, text="Button 5", style="Custom.TButton")
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

# Start the main loop
root.mainloop()

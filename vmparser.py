import tkinter as tk
import os

BUILDVER = "0.2.2"

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
    module_file_path = "commands/esxcfg-module_-q.txt"
    vib_file_path = "commands/localcli_software-vib-list.txt"
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
    nicinfo_file = "commands/nicinfo.sh.txt"
    vswitch_file = "commands/esxcfg-vswitch_-l.txt"
    vmknic_file = "commands/esxcfg-vmknic_-l.txt"

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
    adapters_path = "commands/localcli_storage-core-adapter-list.txt"
    disk_volume_path = "commands/df.txt"
    storage_disks = "commands/localcli_storage-core-path-list.txt"
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
    ]

    # Custom lines of text to be displayed between the files' content
    custom_lines = [
        "=== Mounted Volumes ===",
        "-----------------------",
        "",
    ]

    # Format the lines from disk_volume_lines and remove the first column
    formatted_disk_volume_lines = []
    for line in disk_volume_lines:
        columns = line.strip().split()
        formatted_disk_volume_lines.append(" ".join(columns[1:]))

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
                   "\n".join(custom_lines) + "\n" + "\n".join(formatted_disk_volume_lines) + "\n\n\n" + \
                   filtered_text

    # Display the matching lines in the window
    matching_text.delete(1.0, tk.END)
    matching_text.insert(tk.END, display_text)

    # Save the matching lines to the output file
    with open(storage_file_path, 'w') as storage_file:
        storage_file.write(display_text)


# End of Button contents ---------------------------------------------------#

# Create the main window
root = tk.Tk()

# Set the title dynamically with BUILDVER using f-string
root.title("VM Log Parser  " + BUILDVER)

# Create the "Driver" button
driver_button = tk.Button(root, text="Drivers", command=driver_info)
driver_button.grid(row=0, column=0, padx=10, pady=10)

# Network info button
button2 = tk.Button(root, text="Network", command=network_info)
button2.grid(row=0, column=1, padx=10, pady=10)

button3 = tk.Button(root, text="Storage Info", command=storage_info)
button3.grid(row=0, column=2, padx=10, pady=10)

button4 = tk.Button(root, text="Button 4")
button4.grid(row=1, column=0, padx=10, pady=10)

button5 = tk.Button(root, text="Button 5")
button5.grid(row=1, column=1, padx=10, pady=10)

button6 = tk.Button(root, text="Button 6")
button6.grid(row=1, column=2, padx=10, pady=10)

# Create the text box for displaying
matching_text = tk.Text(root, height=50, width=220)
matching_text.grid(row=2, columnspan=6, padx=10, pady=10)

# Create a vertical scroll bar
scrollbar = tk.Scrollbar(root, command=matching_text.yview)
scrollbar.grid(row=2, column=7, sticky='ns')

# Configure the text box to use the scroll bar
matching_text.config(yscrollcommand=scrollbar.set)

# Start the main loop
root.mainloop()

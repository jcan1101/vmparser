import tkinter as tk
import os

# Setup Review Folder for output text files
folder_path = "Review"

# Check if the folder exists
if not os.path.exists(folder_path):
    # Create the folder
    os.makedirs(folder_path)
    print(f"Folder '{folder_path}' created.")
else:
    print(f"Folder '{folder_path}' already exists.")


def read_files():
    module_file_path = "commands/esxcfg-module_-q.txt"
    vib_file_path = "commands/localcli_software-vib-list.txt"
    driver_file_path = "Review/drivers.txt"

    matching_lines = []

    # Read the contents of esx_file_path
    with open(module_file_path, 'r') as esx_file:
        esx_lines = esx_file.readlines()

    # Read the contents of vib_file_path and search for matching lines
    with open(vib_file_path, 'r') as vib_file:
        for line in vib_file:
            if any(esx_line.strip() in line for esx_line in esx_lines):
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
                matching_lines.append("")  # Append an empty line for spacing

        with open(vmknic_file, 'r') as file:
            lines = file.readlines()
            for line in lines:
                matching_lines.append(line.strip())
                matching_lines.append("")  # Append an empty line for spacing

        with open(vswitch_file, 'r') as file:
            lines = file.readlines()
            for line in lines:
                matching_lines.append(line.strip())
                matching_lines.append("")  # Append an empty line for spacing

        # Display the matching lines in the window
        matching_text.delete(1.0, tk.END)
        matching_text.insert(tk.END, "\n".join(matching_lines))

        # Save the matching lines to the output file
        with open(network_file_path, 'w') as output_file:
            output_file.write("\n".join(matching_lines))
    except FileNotFoundError:
        print(f"One of the files not found.")


# Create the main window
root = tk.Tk()
root.title("VM Log Parser")

# Create the "Driver" button
driver_button = tk.Button(root, text="Drivers", command=read_files)
driver_button.grid(row=0, column=0, padx=10, pady=10)

# Network info button
button2 = tk.Button(root, text="Network", command=network_info)
button2.grid(row=0, column=1, padx=10, pady=10)

button3 = tk.Button(root, text="Button 3")
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

# Start the main loop
root.mainloop()

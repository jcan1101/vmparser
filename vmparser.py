# vmparser created by Jason Canfield
"""Modules for main os related actions"""
import os
import subprocess
import gzip
import zipfile
import tarfile
import tkinter as tk
from tkinter import filedialog, ttk, simpledialog, Toplevel, Label
from tabulate import tabulate
import requests
import sys
import webbrowser


class VMParserApp:
    def __init__(self, root):
        self.BUILDVER = "1.1.0"
        self.VMWARE_VERSION = ""
        self.export_path = "Review"
        self.matching_text = None
        self.progress = None
        self.top_button_frame = None
        self.filter_entry = None
        self.selected_folder_path = os.getcwd()
        self.root = root
        self.setup_ui()
        self.check_new_version()
        self.ensure_export_path_exists()

    def setup_ui(self):
        self.root.title(f"VM Log Parser  {self.BUILDVER}")
        self.matching_text = tk.Text(self.root, height=50, width=220, background="light gray")
        self.matching_text.grid(row=0, column=0, padx=10, pady=10)

        scrollbar = tk.Scrollbar(self.root, command=self.matching_text.yview)  # Use tk.Scrollbar
        scrollbar.grid(row=0, column=1, sticky='ns')
        self.matching_text.config(yscrollcommand=scrollbar.set)

        # Create the bottom button row
        self.top_button_frame = tk.Frame(self.root)  # Use self.root
        self.top_button_frame.grid(row=2, column=0, columnspan=2, padx=10,
                                pady=10)  # Adjusted row to 2 to accommodate progress bar

        # Progressbar widget
        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=200, mode='determinate')
        self.progress.grid(row=2, column=0, columnspan=2, sticky='w', padx=10,pady=10)

        # Bind Control+F to self.search_text function and Control+C to self.copy_text function
        self.root.bind('<Control-f>', lambda event: self.search_text())
        self.root.bind('<Control-c>', lambda event: self.copy_text())

        # Set closing behavior
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.setup_buttons()

        # Welcome Message to show at start
        self.matching_text.insert(tk.END, "Welcome to VMware Log parser!\n\n"
                                          "You can start by Extracting your ZIP/TGZ file or Browse to an already "
                                          "extracted bundle folder\n\n"
                                          "Created by: Jason Canfield\n\n")

    def setup_buttons(self):
        # Create the "Browse" button
        browse_button = ttk.Button(self.top_button_frame, text="Browse Folder", command=self.browse_folder,
                                   style="Custom.TButton")
        browse_button.pack(side="left", padx=(1, 10), pady=10)

        # Extract Zip file button
        browse_button = ttk.Button(self.top_button_frame, text="Extract Bundle", command=self.browse_file, style="Custom.TButton")
        browse_button.pack(side="left", padx=(1, 10), pady=10)

        # Create a separator widget
        separator = ttk.Separator(self.top_button_frame, orient="vertical")
        separator.pack(side="left", padx=55, pady=10)

        # Create the "Drivers" button
        driver_button = ttk.Button(self.top_button_frame, text="Drivers", command=self.driver_info, style="Custom.TButton")
        driver_button.pack(side="left", padx=5, pady=10)

        # Create the "Network" button
        network_button = ttk.Button(self.top_button_frame, text="Network", command=self.network_info, style="Custom.TButton")
        network_button.pack(side="left", padx=5, pady=10)

        # Create the "Storage Info" button
        storage_button = ttk.Button(self.top_button_frame, text="Storage Info", command=self.storage_info, style="Custom.TButton")
        storage_button.pack(side="left", padx=5, pady=10)

        # Create the "VSAN Disk" button
        button4 = ttk.Button(self.top_button_frame, text="VSAN Disks", style="Custom.TButton", command=self.vsan_disk_info)
        button4.pack(side="left", padx=5, pady=10)

        # Create the "Boot Log" button
        button5 = ttk.Button(self.top_button_frame, text="Boot Log", style="Custom.TButton", command=self.boot_log_info)
        button5.pack(side="left", padx=5, pady=10)

        # Create the "Show Logs" button
        show_logs_button = ttk.Button(self.top_button_frame, text="Show Logs", command=self.show_filtered_logs,
                                      style="Custom.TButton")
        show_logs_button.pack(side="left", padx=5, pady=10)

        # Create the filter entry box
        self.filter_entry = tk.Entry(self.top_button_frame, width=40)
        self.filter_entry.pack(side="left", padx=5, pady=10)

        # Bind the <Return> event to the filter entry box
        self.filter_entry.bind('<Return>', lambda event: self.show_filtered_logs())

        # Create the "Review Folder" button
        review_button = ttk.Button(self.top_button_frame, text="Review Folder", command=self.open_folder_explorer,
                                   style="Custom.TButton")
        review_button.pack(side="left", padx=10, pady=10)

        # Configure the button style
        style = ttk.Style()
        style.configure("Custom.TButton", foreground="black", background="white", font=("Arial", 10))

    def ensure_export_path_exists(self):
        if not os.path.exists(self.export_path):
            os.makedirs(self.export_path)
            self.matching_text.insert(tk.END, f"Parsed files will be stored in '{self.export_path}' Folder.\n")

    def browse_folder(self):
        """Browse to vmbundle folder"""
        folder_path = filedialog.askdirectory()
        if folder_path:
            # Do something with the selected folder path
            self.matching_text.delete(1.0, tk.END)
            self.matching_text.insert(tk.END, "Selected folder path: " + folder_path + "\n\n")

            # You can store the path in a variable for later use
            self.selected_folder_path = folder_path
            vm_version_path = self.selected_folder_path + "/commands/vmware_-vl.txt"
            profile_path = self.selected_folder_path + "/commands/localcli_software-profile-get.txt"

            try:
                with open(vm_version_path, 'r') as vm_version_file:
                    vm_version_content = vm_version_file.read()
                self.matching_text.insert(tk.END, "Discovered VMware Build:\n")
                self.matching_text.insert(tk.END, vm_version_content)
                self.VMWARE_VERSION = vm_version_content

            except FileNotFoundError:
                self.matching_text.insert(tk.END, "VM Version file not found.")

            try:
                with open(profile_path, 'r') as profile_file:
                    for line in profile_file:
                        if "Name:" in line:
                            name = line.strip().split(" ", 1)[1]
                            self.matching_text.insert(tk.END, "\n")
                            self.matching_text.insert(tk.END, "Image: " + name)
                            break
            except FileNotFoundError:
                self.matching_text.insert(tk.END, "\n\nCustom Image not found.")

    def browse_file(self):
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
            self.extract_zip(file_path)
        elif file_extension == '.tgz':
            self.extract_tgz(file_path)

    def check_new_version(self):
        url = "https://contribute.dub.emea.dell.com/jason_canfield/logtools/-/raw/master/VM_Parser/version.txt?inline=false"
        current_version = self.BUILDVER
        download_url = "https://contribute.dub.emea.dell.com/jason_canfield/logtools/-/raw/master/VM_Parser/vmparser.exe?inline=false"
        new_version = self.get_new_version(url)
        if new_version and new_version != current_version:
            self.show_update_dialog(current_version, new_version, download_url)

    def get_new_version(self, url):

        try:
            base_path = getattr(sys, '_MEIPASS', os.path.dirname(__file__))
            ca_bundle = os.path.join(base_path, r'contribute.dub.emea.dell.crt')
            response = requests.get(url, verify=ca_bundle)
            response.raise_for_status()  # Ensure the request was successful
            return response.text.strip()
        except Exception as e:
            print(f"An error occurred while checking for a new version: {e}")
        return None

    def show_update_dialog(self, current_version, new_version, download_url):
        dialog = Toplevel(self.root)
        dialog.title("Update Available")
        Label(dialog, text=f"   A newer version ({new_version}) of the application is available. Your current version: {current_version}   ").pack(pady=10)
        link = Label(dialog, text="Click here to download the new version.", fg="blue", cursor="hand2")
        link.pack(pady=10)
        link.bind("<Button-1>", lambda e: webbrowser.open(download_url))

        # Center the dialog on the screen
        dialog.transient(self.root)  # Set to be on top of the main window
        dialog.grab_set()  # Modal - prevents interaction with the main window until this dialog is closed
        dialog.wait_window()  # Wait here until the dialog is closed

    def open_url(url):
        """Open a URL in the web browser."""
        webbrowser.open(url)

    def on_closing(self):
        # Clear search highlights when closing the search
        self.matching_text.tag_remove("found", '1.0', tk.END)
        self.root.destroy()

    def copy_text(self):
        try:
            # Get the currently selected text
            selected_text = self.matching_text.get(tk.SEL_FIRST, tk.SEL_LAST)
            # Clear the clipboard and append the selected text
            root.clipboard_clear()
            root.clipboard_append(selected_text)
        except tk.TclError:
            # No text is selected
            pass

    def search_text(self):
        CustomSearchDialog(self.root, self.matching_text)

    def driver_info(self):
        """Display driver info"""
        module_file_path = os.path.join(self.selected_folder_path, "commands", "esxcfg-module_-q.txt")
        vib_file_path = os.path.join(self.selected_folder_path, "commands", "localcli_software-vib-list.txt")
        svtag_path = os.path.join(self.selected_folder_path, "commands", "smbiosDump.txt")
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
        self.matching_text.delete(1.0, tk.END)
        self.matching_text.insert(tk.END, "ESXi version:  \n" + "----------------\n" + self.VMWARE_VERSION + "\n")
        self.matching_text.insert(tk.END, "System Info:\n" + "----------------\n" + svtag_info_str + "\n")
        self.matching_text.insert(tk.END, "Drivers in use:\n" + "----------------\n" + "\n".join(matching_lines))
        self.matching_text.insert(tk.END,
                             "\n\nDell Packages Installed:\n" + "-------------------------\n" + "\n".join(del_lines))

        # Save the matching lines to the output file
        with open(driver_file_path, 'w') as output_file:
            output_file.write("ESXi version: \n" + self.VMWARE_VERSION + "\n")
            output_file.write("System Info: \n" + svtag_info_str + "\n")
            output_file.write("Drivers in use: \n" + "\n".join(matching_lines))
            output_file.write("\n\nDell Packages Installed: \n" + "\n".join(del_lines))

    def network_info(self):
        """Display Network files"""
        network_file_path = "Review/network.txt"
        nicinfo_file = self.selected_folder_path + "/commands/nicinfo.sh.txt"
        vswitch_file = self.selected_folder_path + "/commands/esxcfg-vswitch_-l.txt"
        vmknic_file = self.selected_folder_path + "/commands/esxcfg-vmknic_-l.txt"

        self.matching_text.tag_configure("bold", font=("Arial", 10, "bold"))
        self.matching_text.delete(1.0, tk.END)

        # Read nicinfo_file contents
        try:
            with open(nicinfo_file, 'r') as file:
                lines = file.readlines()
                for line in lines:
                    if 'NIC:' in line:
                        break
                    self.matching_text.insert(tk.END, line.strip() + "\n")
        except FileNotFoundError:
            self.matching_text.insert(tk.END, f"File not found: {nicinfo_file}\n")

        # Read vmknic_file contents
        try:
            with open(vmknic_file, 'r') as file:
                self.matching_text.insert(tk.END, "----------------------\n")
                self.matching_text.insert(tk.END, "    VM Kernel Port Info:       |\n", "bold")
                self.matching_text.insert(tk.END, "----------------------\n\n")
                lines = file.readlines()
                for line in lines:
                    self.matching_text.insert(tk.END, line.strip() + "\n")
                    self.matching_text.insert(tk.END,
                                              "----------------------------------------------------------------------"
                                              "----------------------------------------------------------------------"
                                              "-------------------------------------------------------------------\n")
        except FileNotFoundError:
            self.matching_text.insert(tk.END, f"File not found: {vmknic_file}\n")

        # Read vswitch_file contents without converting to a table
        try:
            with open(vswitch_file, 'r') as file:
                self.matching_text.insert(tk.END, "\n")
                self.matching_text.insert(tk.END, "----------------------\n")
                self.matching_text.insert(tk.END, "         vSwitch Info:              |\n", "bold")
                self.matching_text.insert(tk.END, "----------------------\n\n")
                self.matching_text.insert(tk.END, file.read() + "\n")
        except FileNotFoundError:
            self.matching_text.insert(tk.END, f"File not found: {vswitch_file}\n")

        # Save the matching lines to the output file
        with open(network_file_path, 'w') as output_file:
            output_file.write(self.matching_text.get(1.0, tk.END))

    def storage_info(self):
        """Display storage Info"""
        adapters_path = self.selected_folder_path + "/commands/localcli_storage-core-adapter-list.txt"
        disk_volume_path = self.selected_folder_path + "/commands/df.txt"
        storage_disks = self.selected_folder_path + "/commands/localcli_storage-core-path-list.txt"
        nvme_info = self.selected_folder_path + "/commands/localcli_nvme-namespace-list.txt"
        disk_info = self.selected_folder_path + "/commands/localcli_storage-core-device-list.txt"
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
            self.matching_text.insert(tk.END, "Adapters file not found.\n")

        try:
            with open(disk_volume_path, 'r') as disk_volume_file:
                disk_volume_lines = disk_volume_file.readlines()
        except FileNotFoundError:
            self.matching_text.insert(tk.END, "Disk volume file not found.\n")

        try:
            with open(storage_disks, 'r') as storage_disks_file:
                storage_disks_lines = storage_disks_file.readlines()
        except FileNotFoundError:
            self.matching_text.insert(tk.END, "Storage disks file not found.\n")

        try:
            with open(nvme_info, 'r') as nvme_file:
                nvme_content = nvme_file.read()
        except FileNotFoundError:
            self.matching_text.insert(tk.END, "NVMe info file not found.\n")

        try:
            with open(disk_info, 'r') as disk_info_file:
                disk_info_lines = disk_info_file.readlines()
        except FileNotFoundError:
            self.matching_text.insert(tk.END, "Disk info file not found.\n")

        # Configure the tag for bold formatting
        self.matching_text.tag_configure("bold", font=("Arial", 10, "bold"))

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

        self.matching_text.delete(1.0, tk.END)

        # Insert the custom headers with the bold tag
        for line in custom_header_adapters:
            self.matching_text.insert(tk.END, line + "\n", "bold")

        # Insert the adapters_content
        self.matching_text.insert(tk.END, adapters_content + "\n\n")

        # Insert the custom lines with the bold tag
        for line in custom_lines:
            self.matching_text.insert(tk.END, line + "\n", "bold")

        # Insert the table
        self.matching_text.insert(tk.END, table + "\n\n\n")

        # Insert the custom headers for NVMe info with the bold tag
        for line in custom_header_nvme_info:
            self.matching_text.insert(tk.END, line + "\n", "bold")

        # Insert the NVMe content
        self.matching_text.insert(tk.END, nvme_content + "\n\n")

        # Insert the custom headers for disk info with the bold tag
        for line in custom_header_disk_info:
            self.matching_text.insert(tk.END, line + "\n", "bold")

        # Insert the disk info filtered text
        self.matching_text.insert(tk.END, "\n".join(disk_info_filtered_lines) + "\n\n")

        # Insert the custom headers for storage disks with the bold tag
        for line in custom_header_storage_disks:
            self.matching_text.insert(tk.END, line + "\n", "bold")

        # Insert the filtered text
        self.matching_text.insert(tk.END, "\n".join(filtered_lines))

        # Concatenate the lines of text with the file contents for saving to a file
        display_text = "\n".join(custom_header_adapters) + "\n" + adapters_content + "\n\n" + \
                       "\n".join(custom_lines) + "\n" + table + "\n\n\n" + \
                       "\n".join(custom_header_nvme_info) + "\n" + nvme_content + "\n\n" + \
                       "\n".join(custom_header_disk_info) + "\n" + "\n".join(disk_info_filtered_lines) + "\n\n" + \
                       "\n".join(custom_header_storage_disks) + "\n" + "\n".join(filtered_lines)

        # Save the matching lines to the output file
        with open(storage_file_path, 'w') as storage_file:
            storage_file.write(display_text)

    def open_folder_explorer(self):
        """Open review folder using file explorer"""
        # Set Review folder in CWD
        folder_path = os.path.join(os.getcwd(), "Review")
        # Use the 'explorer' command in Windows to open the folder in File Explorer
        subprocess.Popen(f'explorer "{folder_path}"')

    def show_filtered_logs(self):
        """Show and save vmkernel logs"""
        log_files = []
        log_file_path = self.selected_folder_path + "/var/run/log/vmkernel"
        filter_text = self.filter_entry.get()

        # Find and unzip vmkernel log files from vmkernel.0.gz to vmkernel.7.gz
        for i in range(8):
            gz_file_path = log_file_path + "." + str(i) + ".gz"
            if os.path.exists(gz_file_path):
                log_files.append(gz_file_path)
                unzipped_file_path = log_file_path + "_" + str(i)
                with gzip.open(gz_file_path, 'rb') as gz_file:
                    with open(unzipped_file_path, 'wb') as unzipped_file:
                        unzipped_file.write(gz_file.read())
                # Add the unzipped file path to the log_files list to process later
                log_files.append(unzipped_file_path)

        # Add any other vmkernel log files in the directory to the list
        for file in os.listdir(self.selected_folder_path + "/var/run/log"):
            if file.startswith("vmkernel"):
                log_files.append(os.path.join(self.selected_folder_path + "/var/run/log", file))

        filtered_lines = []
        # Process each file in the log_files list
        for log_file_path in log_files:
            # Skip .gz files since we are processing unzipped copies
            if log_file_path.endswith(".gz"):
                continue

            with open(log_file_path, 'r') as log_file:
                lines = log_file.readlines()

            filtered_lines.extend([line.strip() for line in lines if filter_text in line])

        # Update the text widget with filtered lines or a not-found message
        if filtered_lines:
            self.matching_text.delete(1.0, tk.END)
            self.matching_text.insert(tk.END, "\n".join(filtered_lines))
            # Save filtered lines to a combined log file in the Review folder
            combined_log_path = os.path.join(self.export_path, "vmkernel_combined.txt")
            with open(combined_log_path, 'w') as combined_file:
                combined_file.write("\n".join(filtered_lines))
        else:
            self.matching_text.delete(1.0, tk.END)
            self.matching_text.insert(tk.END, "No matching lines found.")

    def boot_log_info(self):
        """Show vmksummary boot info"""
        file_path = self.selected_folder_path + "/var/run/log/vmksummary.log"

        try:
            with open(file_path, 'r') as file:
                matching_lines = []
                for line in file:
                    if 'boot' in line:
                        matching_lines.append(line.strip())

            # Display the matching lines in the window
            self.matching_text.delete(1.0, tk.END)
            self.matching_text.insert(tk.END, "\n".join(matching_lines))

        except FileNotFoundError:
            self.matching_text.delete(1.0, tk.END)
            self.matching_text.insert(tk.END, "File not found: " + file_path)

    def vsan_disk_info(self):
        """Display vsan disk files"""
        file_path = self.selected_folder_path + "/commands/vdq_-q--H.txt"
        output_file_path = "Review/vsan_output.txt"

        try:
            with open(file_path, 'r') as file:
                # Read the contents of the file
                lines = file.readlines()

            # Configure the tag for red formatting
            self.matching_text.tag_configure("red", foreground="red")

            # Clear the text box
            self.matching_text.delete(1.0, tk.END)

            flagged_words = set()  # Store "naa." words flagged red

            for line in lines:
                stripped_line = line.strip()
                if "Size(MB):  0" in stripped_line or "IsPDL?:  1" in stripped_line:
                    self.matching_text.insert(tk.END, stripped_line + "\n", "red")
                else:
                    words = stripped_line.split()
                    for word in words:
                        if word.startswith('naa.') and word in flagged_words:
                            self.matching_text.insert(tk.END, word + ' ', 'red')
                        elif "/naa." in word or "error" in stripped_line.lower() or "Failed" in stripped_line:
                            subwords = word.split('/')
                            for subword in subwords:
                                if subword.startswith('naa.'):
                                    flagged_words.add(subword)
                                    self.matching_text.insert(tk.END, '/' + subword + ' ', 'red')
                                else:
                                    self.matching_text.insert(tk.END, '/' + subword + ' ')
                            # delete the leading '/' from the text widget
                            self.matching_text.delete('end - 2c')
                        else:
                            self.matching_text.insert(tk.END, word + ' ')
                    self.matching_text.insert(tk.END, '\n')

            # Save the content to a separate file
            with open(output_file_path, 'w') as output_file:
                output_file.writelines(lines)

        except FileNotFoundError:
            self.matching_text.delete(1.0, tk.END)
            self.matching_text.insert(tk.END, "File not found: " + file_path)

    def update_progress(self, progressbar, value, maximum):
        """Setup progress bar widget"""
        progressbar["value"] = value
        progressbar["maximum"] = maximum
        progressbar.update()

    def extract_zip(self, file_path):
        """Extract ZIP file"""
        self.matching_text.delete(1.0, tk.END)
        self.matching_text.insert(tk.END, "Selected File: " + file_path + "\n")

        if not file_path:
            return

        extract_path = os.path.join(os.getcwd(), 'Extracted')

        if not os.path.exists(extract_path):
            os.makedirs(extract_path)

        self.matching_text.insert(tk.END, "Extracting .zip file...\n")

        tgz_files_extracted = []  # List to store the names of the .tgz files extracted from the .zip

        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            members = zip_ref.namelist()
            total_members = len(members)
            for i, member in enumerate(members):
                with open(os.path.join(extract_path, member), 'wb') as f_out:
                    f_out.write(zip_ref.read(member))
                if member.endswith('.tgz'):
                    tgz_files_extracted.append(member)  # Add the name of the .tgz file to the list
                self.update_progress(self.progress, i + 1, total_members)

            self.matching_text.insert(tk.END, "Extracted .zip, now extracting .tgz\n\n")

        for file in tgz_files_extracted:  # Only extract the .tgz files that came from the .zip
            with tarfile.open(os.path.join(extract_path, file), errorlevel=1) as tar_ref:
                members = tar_ref.getmembers()
                root_dirs = {member.name.split('/')[0] for member in members if
                             '/' in member.name}  # Get root directories from the .tgz file
                for i, member in enumerate(members):
                    try:
                        member.name = member.name.replace(':', '_')  # Replace colons with underscore
                        tar_ref.extract(member, path=extract_path)
                        self.update_progress(self.progress, i + 1, len(members))
                    except FileNotFoundError as e:
                        print(f"File {member.name} not found: {str(e)}")
                    except PermissionError as e:
                        print(f"No permission to extract {member.name}: {str(e)}")
                    except tarfile.TarError as e:
                        print(f"Error occurred while extracting {member.name}: {str(e)}")
                    except Exception as e:
                        print(f"An unexpected error occurred while extracting {member.name}: {str(e)}")

        # List all directories under the extraction path
        extracted_dirs = [d for d in os.listdir(extract_path) if
                          os.path.isdir(os.path.join(extract_path, d)) and d in root_dirs]

        # Check if there are any directories in the list
        if extracted_dirs:
            self.selected_folder_path = os.path.join(extract_path, extracted_dirs[0])
            self.matching_text.delete(1.0, tk.END)
            self.matching_text.insert(tk.END, "Extracted folder path is: " + self.selected_folder_path + "\n\n")
        else:
            self.matching_text.insert(tk.END, "No directories found inside the extracted path.")
            return

        vm_version_path = self.selected_folder_path + "/commands/vmware_-vl.txt"
        profile_path = self.selected_folder_path + "/commands/localcli_software-profile-get.txt"

        try:
            with open(vm_version_path, 'r') as vm_version_file:
                vm_version_content = vm_version_file.read()
            self.matching_text.insert(tk.END, "Discovered VMware Build:\n")
            self.matching_text.insert(tk.END, vm_version_content)
            self.VMWARE_VERSION = vm_version_content

        except FileNotFoundError:
            self.matching_text.insert(tk.END, "VM Version file not found.")

        try:
            with open(profile_path, 'r') as profile_file:
                for line in profile_file:
                    if "Name:" in line:
                        name = line.strip().split(" ", 1)[1]
                        self.matching_text.insert(tk.END, "\n")
                        self.matching_text.insert(tk.END, "Image: " + name)
                        break
        except FileNotFoundError:
            self.matching_text.insert(tk.END, "\n\nCustom Image not found.")

    def extract_tgz(self, file_path):
        """Extract TGZ file"""

        self.matching_text.delete(1.0, tk.END)
        self.matching_text.insert(tk.END, "Selected File: " + file_path + "\n")
        if not file_path:
            return

        extract_path = os.path.join(os.getcwd(), 'Extracted')

        if not os.path.exists(extract_path):
            os.makedirs(extract_path)

        self.matching_text.insert(tk.END, "Extracting .tgz file...\n")

        with tarfile.open(file_path, 'r') as tar_ref:
            members = tar_ref.getmembers()
            root_dirs = {member.name.split('/')[0] for member in members if
                         '/' in member.name}  # Get root directories from the .tgz file
            for i, member in enumerate(members):
                try:
                    member.name = member.name.replace(':', '_')  # Replace colons with underscore
                    tar_ref.extract(member, path=extract_path)
                    self.update_progress(self.progress, i + 1, len(members))
                except FileNotFoundError as e:
                    print(f"File {member.name} not found: {str(e)}")
                except PermissionError as e:
                    print(f"No permission to extract {member.name}: {str(e)}")
                except tarfile.TarError as e:
                    print(f"Error occurred while extracting {member.name}: {str(e)}")
                except Exception as e:
                    print(f"An unexpected error occurred while extracting {member.name}: {str(e)}")

        self.matching_text.insert(tk.END, "Extracted .tgz file.\n\n")

        extracted_dirs = [d for d in os.listdir(extract_path) if
                          os.path.isdir(os.path.join(extract_path, d)) and d in root_dirs]

        if extracted_dirs:
            self.selected_folder_path = os.path.join(extract_path, extracted_dirs[0])  # Choose the first matched directory
            self.matching_text.delete(1.0, tk.END)
            self.matching_text.insert(tk.END, "Extracted folder path is: " + self.selected_folder_path + "\n\n")
        else:
            self.matching_text.insert(tk.END, "No directories found inside the extracted path.")
            return

        vm_version_path = self.selected_folder_path + "/commands/vmware_-vl.txt"
        profile_path = self.selected_folder_path + "/commands/localcli_software-profile-get.txt"

        try:
            with open(vm_version_path, 'r') as vm_version_file:
                vm_version_content = vm_version_file.read()
            self.matching_text.insert(tk.END, "Discovered VMware Build:\n")
            self.matching_text.insert(tk.END, vm_version_content)
            self.VMWARE_VERSION = vm_version_content

        except FileNotFoundError:
            self.matching_text.insert(tk.END, "VM Version file not found.")

        try:
            with open(profile_path, 'r') as profile_file:
                for line in profile_file:
                    if "Name:" in line:
                        name = line.strip().split(" ", 1)[1]
                        self.matching_text.insert(tk.END, "\n")
                        self.matching_text.insert(tk.END, "Image: " + name)
                        break
        except FileNotFoundError:
            self.matching_text.insert(tk.END, "\n\nCustom Image not found.")


class CustomSearchDialog(simpledialog.Dialog):
    def __init__(self, master, text_widget):
        self.text_widget = text_widget
        self.last_index = '1.0'
        self.search_query = ""
        super().__init__(master, title="Search")

    def body(self, master):
        tk.Label(master, text="Enter search string:").grid(row=0)
        self.entry = tk.Entry(master)
        self.entry.grid(row=0, column=1)
        self.entry.bind("<Return>", self.find_next)
        return self.entry

    def find_next(self, event=None):
        if self.search_query != self.entry.get():
            # New search
            self.search_query = self.entry.get()
            self.last_index = '1.0'
            self.text_widget.tag_remove("found", '1.0', tk.END)

        if self.search_query:
            self.last_index = self.text_widget.search(self.search_query, self.last_index, nocase=1, stopindex=tk.END)
            if not self.last_index:
                self.last_index = '1.0'  # Wrap search or indicate end
                return

            last_index = f"{self.last_index}+{len(self.search_query)}c"
            self.text_widget.tag_remove("found", '1.0', tk.END)  # Clear previous highlights
            self.text_widget.tag_add("found", self.last_index, last_index)
            self.text_widget.tag_config("found", background="yellow")
            self.text_widget.see(self.last_index)
            self.last_index = last_index

    def buttonbox(self):
        box = tk.Frame(self)
        w = tk.Button(box, text="Next", width=10, command=self.find_next, default=tk.ACTIVE)
        w.pack(side=tk.LEFT, padx=5, pady=5)
        self.bind("<Return>", self.find_next)
        box.pack()


if __name__ == "__main__":
    root = tk.Tk()
    app = VMParserApp(root)
    root.mainloop()


"""
+ 1.0.4 - Added version check function
+ 1.0.5 - Added copy/find options using ctrl+c/ctrl+f
+ 1.0.6 - Added new dialogbox to download new version 
+ 1.0.7 - Redesigned to class structure for main functions
+ 1.0.8 - Changed formatting of vswitch display
+ 1.0.9 - All vmkernel logs combined and now saved into Review folder as vmkernel_combined.txt
"""
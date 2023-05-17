import tkinter as tk


def read_files():
    esx_file_path = "esxcfg-module_-q.txt"
    vib_file_path = "localcli_software-vib-list.txt"

    matching_lines = []

    # Read the contents of esx_file_path
    with open(esx_file_path, 'r') as esx_file:
        esx_lines = esx_file.readlines()

    # Read the contents of vib_file_path and search for matching lines
    with open(vib_file_path, 'r') as vib_file:
        for line in vib_file:
            if any(esx_line.strip() in line for esx_line in esx_lines):
                matching_lines.append(line.strip())

    # Display the matching lines in the window
    matching_text.delete(1.0, tk.END)
    matching_text.insert(tk.END, "\n".join(matching_lines))


# Create the main window
root = tk.Tk()
root.title("File Search")

# Create the "Info" button
info_button = tk.Button(root, text="Info", command=read_files)
info_button.pack(pady=10)

# Create the text box for displaying matching lines
matching_text = tk.Text(root, height=40, width=120)
matching_text.pack()

# Start the main loop
root.mainloop()

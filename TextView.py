import tkinter as tk
from tkinter import filedialog

def open_file():
    file_path = filedialog.askopenfilename()
    if file_path:
        with open(file_path, 'r') as file:
            content_text.delete(1.0, tk.END)
            content_text.insert(tk.END, file.read())

def filter_content():
    filter_text = filter_entry.get()
    content = content_text.get(1.0, tk.END)

    filtered_content = ""
    if filter_text:
        for line in content.split('\n'):
            if filter_text in line:
                filtered_content += line + '\n'
    else:
        filtered_content = content

    content_text.delete(1.0, tk.END)
    content_text.insert(tk.END, filtered_content)

# Create the main window
root = tk.Tk()
root.title("File Viewer")

# Create the file selection button
open_button = tk.Button(root, text="Open File", command=open_file)
open_button.pack(pady=10)

# Create the content text box
content_text = tk.Text(root, height=20, width=80)
content_text.pack()

# Create the filter entry field and button
filter_entry = tk.Entry(root, width=30)
filter_entry.pack(pady=5)

filter_button = tk.Button(root, text="Filter", command=filter_content)
filter_button.pack(pady=5)

# Start the main loop
root.mainloop()

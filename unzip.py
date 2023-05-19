import os
import tarfile
import zipfile
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk


def update_progress(progressbar, value, maximum):
    progressbar["value"] = value
    progressbar["maximum"] = maximum
    root.update()


def browse():
    file_path = filedialog.askopenfilename(filetypes=(("Zip Files", "*.zip"),))
    if not file_path:
        return

    extract_path = os.path.join(os.getcwd(), 'Extracted')

    if not os.path.exists(extract_path):
        os.makedirs(extract_path)
        messagebox.showinfo("Folder Created", f"Created folder at {extract_path}")

    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)

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

    messagebox.showinfo("Success", f"Files extracted successfully to {extract_path}")


root = tk.Tk()
root.title('File Extraction')

button_browse = tk.Button(root, text="Browse", command=browse)
button_browse.pack()

progress = ttk.Progressbar(root, orient="horizontal", length=200, mode="determinate")
progress.pack()

root.mainloop()


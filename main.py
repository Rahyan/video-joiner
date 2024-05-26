# pip install moviepy tkinter --user

import os
import re
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinterdnd2 import TkinterDnD, DND_FILES
from moviepy.editor import concatenate_videoclips, VideoFileClip

class VideoJoinerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Joiner")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        self.files = []

        self.create_widgets()
        self.setup_drag_and_drop()
        self.apply_theme("Light")

    def create_widgets(self):
        # Theme Frame
        theme_frame = ttk.Frame(self.root, padding="10")
        theme_frame.pack(fill=tk.X)
        
        self.theme_var = tk.StringVar(value="Light")
        self.theme_menu = ttk.OptionMenu(theme_frame, self.theme_var, "Light", "Dark", command=self.apply_theme)
        self.theme_menu.pack(side=tk.LEFT)

        # File Management Frame
        file_frame = ttk.LabelFrame(self.root, text="File Management", padding="10")
        file_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.add_button = ttk.Button(file_frame, text="Add Video Files", command=self.add_files)
        self.add_button.pack(side=tk.LEFT, padx=5)
        
        self.remove_button = ttk.Button(file_frame, text="Remove Selected Files", command=self.remove_files)
        self.remove_button.pack(side=tk.LEFT, padx=5)
        
        self.move_up_button = ttk.Button(file_frame, text="Move Up", command=self.move_up)
        self.move_up_button.pack(side=tk.LEFT, padx=5)
        
        self.move_down_button = ttk.Button(file_frame, text="Move Down", command=self.move_down)
        self.move_down_button.pack(side=tk.LEFT, padx=5)
        
        # Search and Filter
        search_frame = ttk.Frame(file_frame)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.search_var = tk.StringVar()
        self.search_var.trace_add('write', self.update_listbox)
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(fill=tk.X, padx=5)

        # Listbox Frame
        listbox_frame = ttk.Frame(self.root, padding="10")
        listbox_frame.pack(fill=tk.BOTH, expand=True)

        self.file_listbox = tk.Listbox(listbox_frame, selectmode=tk.MULTIPLE, width=50)
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical", command=self.file_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.file_listbox.config(yscrollcommand=scrollbar.set)
        
        # Video Operations Frame
        operation_frame = ttk.Frame(self.root, padding="10")
        operation_frame.pack(fill=tk.X)

        self.trim_button = ttk.Button(operation_frame, text="Trim Video", command=self.trim_video)
        self.trim_button.pack(side=tk.LEFT, padx=5)
        
        self.preview_button = ttk.Button(operation_frame, text="Preview Video", command=self.preview_video)
        self.preview_button.pack(side=tk.LEFT, padx=5)
        
        self.join_button = ttk.Button(operation_frame, text="Join Videos", command=self.join_videos)
        self.join_button.pack(side=tk.LEFT, padx=5)

        # Progress and Status Frame
        progress_frame = ttk.Frame(self.root, padding="10")
        progress_frame.pack(fill=tk.X)
        
        self.progress = ttk.Progressbar(progress_frame, orient="horizontal", length=300, mode="determinate")
        self.progress.pack(side=tk.LEFT, padx=5)
        
        self.status_label = ttk.Label(progress_frame, text="")
        self.status_label.pack(side=tk.LEFT, padx=5)

        # Help menu
        menubar = tk.Menu(self.root)
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Usage Instructions", command=self.show_help)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        self.root.config(menu=menubar)

    def setup_drag_and_drop(self):
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.drop_files)

    def drop_files(self, event):
        files = self.root.tk.splitlist(event.data)
        self.add_files(files)

    def apply_theme(self, theme):
        style = ttk.Style()
        if theme == "Dark":
            style.theme_use('clam')
            self.root.tk_setPalette(background='#2e2e2e', foreground='white', activeBackground='#505050', activeForeground='white')
            style.configure("TLabel", background="#2e2e2e", foreground="white")
            style.configure("TFrame", background="#2e2e2e")
            style.configure("TButton", background="#505050", foreground="white")
            style.configure("TEntry", fieldbackground="#505050", foreground="white")
            style.configure("TListbox", background="#2e2e2e", foreground="white")
        else:
            style.theme_use('default')
            self.root.tk_setPalette(background='white', foreground='black', activeBackground='lightgray', activeForeground='black')
            style.configure("TLabel", background="white", foreground="black")
            style.configure("TFrame", background="white")
            style.configure("TButton", background="lightgray", foreground="black")
            style.configure("TEntry", fieldbackground="white", foreground="black")
            style.configure("TListbox", background="white", foreground="black")

    def add_files(self, files=None):
        if not files:
            files = filedialog.askopenfilenames(filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv")])
        if files:
            for file in files:
                if file not in self.files:
                    self.files.append(file)
                    self.file_listbox.insert(tk.END, os.path.basename(file))
            self.status_label.config(text=f"{len(self.files)} files added.")

    def remove_files(self):
        selected_indices = self.file_listbox.curselection()
        for index in reversed(selected_indices):
            self.files.pop(index)
            self.file_listbox.delete(index)
        self.status_label.config(text=f"{len(self.files)} files remaining.")

    def move_up(self):
        selected_indices = self.file_listbox.curselection()
        for index in selected_indices:
            if index == 0:
                continue
            self.files[index], self.files[index-1] = self.files[index-1], self.files[index]
            self.file_listbox.delete(index)
            self.file_listbox.insert(index-1, os.path.basename(self.files[index-1]))
            self.file_listbox.select_set(index-1)
            self.file_listbox.select_clear(index)

    def move_down(self):
        selected_indices = self.file_listbox.curselection()
        for index in reversed(selected_indices):
            if index == len(self.files) - 1:
                continue
            self.files[index], self.files[index+1] = self.files[index+1], self.files[index]
            self.file_listbox.delete(index)
            self.file_listbox.insert(index+1, os.path.basename(self.files[index+1]))
            self.file_listbox.select_set(index+1)
            self.file_listbox.select_clear(index)

    def trim_video(self):
        selected_indices = self.file_listbox.curselection()
        if not selected_indices:
            messagebox.showerror("Error", "No video file selected for trimming!")
            return
        index = selected_indices[0]
        video_file = self.files[index]
        trim_window = tk.Toplevel(self.root)
        trim_window.title("Trim Video")

        tk.Label(trim_window, text="Start Time (seconds):").pack(pady=5)
        start_time = ttk.Entry(trim_window)
        start_time.pack(pady=5)

        tk.Label(trim_window, text="End Time (seconds):").pack(pady=5)
        end_time = ttk.Entry(trim_window)
        end_time.pack(pady=5)

        def apply_trim():
            try:
                start = float(start_time.get())
                end = float(end_time.get())
                clip = VideoFileClip(video_file).subclip(start, end)
                self.files[index] = clip
                self.file_listbox.delete(index)
                self.file_listbox.insert(index, f"{os.path.basename(video_file)} (Trimmed)")
                messagebox.showinfo("Success", "Video trimmed successfully!")
            except Exception as e:
                messagebox.showerror("Error", str(e))
            trim_window.destroy()

        apply_button = ttk.Button(trim_window, text="Apply", command=apply_trim)
        apply_button.pack(pady=10)

    def preview_video(self):
        selected_indices = self.file_listbox.curselection()
        if not selected_indices:
            messagebox.showerror("Error", "No video file selected for preview!")
            return
        index = selected_indices[0]
        video_file = self.files[index]
        if isinstance(video_file, str):
            clip = VideoFileClip(video_file)
        else:
            clip = video_file
        
        def preview():
            clip.preview()
        
        preview_thread = threading.Thread(target=preview)
        preview_thread.start()

    def join_videos(self):
        if not self.files:
            messagebox.showerror("Error", "No video files added!")
            return

        try:
            # Sort files based on the numerical part in the filenames
            self.files.sort(key=lambda x: int(re.findall(r'W(\d+)', os.path.basename(x))[0]))

            clips = [VideoFileClip(f) if isinstance(f, str) else f for f in self.files]
            final_clip = concatenate_videoclips(clips)

            output_path = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4 files", "*.mp4"), ("AVI files", "*.avi"), ("MKV files", "*.mkv")])
            if output_path:
                self.progress["maximum"] = 100
                final_clip.write_videofile(output_path, codec="libx264")
                messagebox.showinfo("Success", "Videos joined successfully!")
                self.files = []
                self.file_listbox.delete(0, tk.END)
                self.status_label.config(text="")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_progress(self, t, duration):
        progress = int((t / duration) * 100)
        self.progress["value"] = progress
        self.root.update_idletasks()

    def update_listbox(self, *args):
        search_term = self.search_var.get().lower()
        self.file_listbox.delete(0, tk.END)
        for file in self.files:
            if search_term in os.path.basename(file).lower():
                self.file_listbox.insert(tk.END, os.path.basename(file))

    def show_help(self):
        messagebox.showinfo("Usage Instructions", "Instructions on how to use the application.")

    def show_about(self):
        messagebox.showinfo("About", "Video Joiner App v1.0\nDeveloped by Rahyan Saouab.")

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = VideoJoinerApp(root)
    root.mainloop()

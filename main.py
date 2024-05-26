# pip install moviepy tkinter --user

import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox
from moviepy.editor import concatenate_videoclips, VideoFileClip

class VideoJoinerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Joiner")

        self.files = []

        self.add_button = tk.Button(root, text="Add Video Files", command=self.add_files)
        self.add_button.pack(pady=10)

        self.join_button = tk.Button(root, text="Join Videos", command=self.join_videos)
        self.join_button.pack(pady=10)

        self.status_label = tk.Label(root, text="")
        self.status_label.pack(pady=10)

    def add_files(self):
        files = filedialog.askopenfilenames(filetypes=[("MP4 files", "*.mp4")])
        if files:
            self.files.extend(files)
            self.status_label.config(text=f"{len(self.files)} files added.")

    def join_videos(self):
        if not self.files:
            messagebox.showerror("Error", "No video files added!")
            return

        try:
            self.files.sort(key=lambda x: int(re.findall(r'W(\d+)', os.path.basename(x))[0]))

            clips = [VideoFileClip(f) for f in self.files]
            final_clip = concatenate_videoclips(clips)
            
            output_path = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4 files", "*.mp4")])
            if output_path:
                final_clip.write_videofile(output_path, codec="libx264")
                messagebox.showinfo("Success", "Videos joined successfully!")
                self.files = []
                self.status_label.config(text="")
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoJoinerApp(root)
    root.mainloop()

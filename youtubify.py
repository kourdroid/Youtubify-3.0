"""
Youtubify 3.0
A modern YouTube downloader built with CustomTkinter, yt-dlp, and CTkMenuBar.

Features:
    - Two-panel interface:
        * Left panel for playlist downloads.
        * Right panel for individual video downloads.
    - Options for resolution (up to 4K), export formats (mp4, mp3, wav), and subtitles.
    - Destination directory selector.
    - Real-time progress (with percentage) and global logging.
    - Modern, minimalist design with red accents.
    - Custom menu bar (CTkMenuBar) with an About option.

Author: Your Name
License: MIT
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
from CTkMenuBar import CTkMenuBar  # Requires: pip install CTkMenuBar
import yt_dlp
import threading

# Global log function for appending messages to the log textbox.
def append_log(log_widget, message):
    log_widget.configure(state="normal")
    log_widget.insert("end", f"{message}\n")
    log_widget.see("end")
    log_widget.configure(state="disabled")

# -----------------------------
# Left Frame: Playlist Download
# -----------------------------
class PlaylistFrame(ctk.CTkFrame):
    def __init__(self, master, log_widget, browse_callback, *args, **kwargs):
        super().__init__(master, corner_radius=12, fg_color="#f9f9f9", *args, **kwargs)
        self.log_widget = log_widget

        # Header with red accent
        self.header = ctk.CTkLabel(self, text="Playlist Download", font=("Segoe UI", 24, "bold"), text_color="#ff4d4d")
        self.header.pack(pady=(20,10))
        
        # Playlist URL
        self.url_label = ctk.CTkLabel(self, text="Playlist URL:", font=("Segoe UI", 16))
        self.url_label.pack(pady=(10, 5))
        self.url_entry = ctk.CTkEntry(self, width=350, placeholder_text="Enter playlist URL")
        self.url_entry.pack(pady=5)
        
        # Destination Directory
        self.dest_label = ctk.CTkLabel(self, text="Destination:", font=("Segoe UI", 16))
        self.dest_label.pack(pady=(10, 5))
        self.dest_entry = ctk.CTkEntry(self, width=350, placeholder_text="Choose folder")
        self.dest_entry.pack(pady=5)
        self.browse_button = ctk.CTkButton(self, text="Browse", width=100, command=browse_callback, fg_color="#ff4d4d", hover_color="#ff6666")
        self.browse_button.pack(pady=5)
        
        # Subtitle Option
        self.subtitle_var = ctk.StringVar(value="False")
        self.subtitle_checkbox = ctk.CTkCheckBox(self, text="Download Subtitles", variable=self.subtitle_var, font=("Segoe UI", 16))
        self.subtitle_checkbox.pack(pady=5)
        
        # Download Button
        self.download_button = ctk.CTkButton(self, text="Download Playlist", fg_color="#ff4d4d", hover_color="#ff6666", command=self.start_download, width=200)
        self.download_button.pack(pady=10)
        
        # Progress Bar and Percentage Label
        self.progress_bar = ctk.CTkProgressBar(self, width=350)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=(10,5))
        self.percent_label = ctk.CTkLabel(self, text="0%", font=("Segoe UI", 14))
        self.percent_label.pack(pady=(0,10))
        
        # Status Label
        self.status_label = ctk.CTkLabel(self, text="Idle", font=("Segoe UI", 14))
        self.status_label.pack(pady=5)

    def update_status(self, message):
        self.status_label.configure(text=message)
        append_log(self.log_widget, f"[Playlist] {message}")
    
    def update_progress(self, d):
        if d.get("status") == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate")
            if total:
                progress = d.get("downloaded_bytes", 0) / total
                self.progress_bar.set(progress)
                self.percent_label.configure(text=f"{int(progress*100)}%")
        elif d.get("status") == "finished":
            self.update_status("Post-processing...")
    
    def start_download(self):
        url = self.url_entry.get().strip()
        dest_dir = self.dest_entry.get().strip()
        if not url:
            self.update_status("Error: Enter a playlist URL")
            return
        if not dest_dir:
            self.update_status("Error: Select a destination")
            return
        self.update_status("Starting playlist download...")
        
        def download_worker():
            ydl_opts = {
                "outtmpl": f"{dest_dir}/%(playlist_index)s - %(title)s.%(ext)s",
                "progress_hooks": [self.update_progress],
                "noplaylist": False,
            }
            if self.subtitle_var.get() == "True":
                ydl_opts["writesubtitles"] = True
                ydl_opts["subtitleslangs"] = ["en"]
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                self.update_status("Playlist download complete!")
            except Exception as e:
                self.update_status(f"Download error: {e}")
            self.progress_bar.set(0)
            self.percent_label.configure(text="0%")
        
        threading.Thread(target=download_worker, daemon=True).start()

# ---------------------------
# Right Frame: Video Download
# ---------------------------
class VideoFrame(ctk.CTkFrame):
    def __init__(self, master, log_widget, browse_callback, *args, **kwargs):
        super().__init__(master, corner_radius=12, fg_color="#f9f9f9", *args, **kwargs)
        self.log_widget = log_widget

        # Header with red accent
        self.header = ctk.CTkLabel(self, text="Video Download", font=("Segoe UI", 24, "bold"), text_color="#ff4d4d")
        self.header.pack(pady=(20,10))
        
        # Video URL
        self.url_label = ctk.CTkLabel(self, text="Video URL:", font=("Segoe UI", 16))
        self.url_label.pack(pady=(10,5))
        self.url_entry = ctk.CTkEntry(self, width=350, placeholder_text="Enter video URL")
        self.url_entry.pack(pady=5)
        
        # Destination Directory
        self.dest_label = ctk.CTkLabel(self, text="Destination:", font=("Segoe UI", 16))
        self.dest_label.pack(pady=(10,5))
        self.dest_entry = ctk.CTkEntry(self, width=350, placeholder_text="Choose folder")
        self.dest_entry.pack(pady=5)
        self.browse_button = ctk.CTkButton(self, text="Browse", width=100, command=browse_callback, fg_color="#ff4d4d", hover_color="#ff6666")
        self.browse_button.pack(pady=5)
        
        # Options: Resolution and Format
        self.options_frame = ctk.CTkFrame(self, corner_radius=8)
        self.options_frame.pack(pady=10)
        self.resolution_label = ctk.CTkLabel(self.options_frame, text="Resolution:", font=("Segoe UI", 16))
        self.resolution_label.grid(row=0, column=0, padx=10, pady=5)
        self.resolution_combo = ctk.CTkComboBox(self.options_frame, values=["Select resolution"], width=120)
        self.resolution_combo.grid(row=0, column=1, padx=10, pady=5)
        self.format_label = ctk.CTkLabel(self.options_frame, text="Format:", font=("Segoe UI", 16))
        self.format_label.grid(row=1, column=0, padx=10, pady=5)
        self.format_combo = ctk.CTkComboBox(self.options_frame, values=["mp4", "mp3", "wav"], width=120)
        self.format_combo.grid(row=1, column=1, padx=10, pady=5)
        
        # Subtitle Option
        self.subtitle_var = ctk.StringVar(value="False")
        self.subtitle_checkbox = ctk.CTkCheckBox(self, text="Download Subtitles", variable=self.subtitle_var, font=("Segoe UI", 16))
        self.subtitle_checkbox.pack(pady=5)
        
        # Fetch Info Button
        self.fetch_button = ctk.CTkButton(self, text="Fetch Video Info", command=self.fetch_info, width=200)
        self.fetch_button.pack(pady=10)
        
        # Download Button with red accent
        self.download_button = ctk.CTkButton(self, text="Download Video", fg_color="#ff4d4d", hover_color="#ff6666", command=self.start_download, width=200)
        self.download_button.pack(pady=10)
        
        # Progress Bar and Percentage Label
        self.progress_bar = ctk.CTkProgressBar(self, width=350)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=(10,5))
        self.percent_label = ctk.CTkLabel(self, text="0%", font=("Segoe UI", 14))
        self.percent_label.pack(pady=(0,10))
        
        # Status Label
        self.status_label = ctk.CTkLabel(self, text="Idle", font=("Segoe UI", 14))
        self.status_label.pack(pady=5)
        
        # Storage for video info
        self.video_info = None

    def update_status(self, message):
        self.status_label.configure(text=message)
        append_log(self.log_widget, f"[Video] {message}")
    
    def update_progress(self, d):
        if d.get("status") == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate")
            if total:
                progress = d.get("downloaded_bytes", 0) / total
                self.progress_bar.set(progress)
                self.percent_label.configure(text=f"{int(progress*100)}%")
        elif d.get("status") == "finished":
            self.update_status("Post-processing...")
    
    def fetch_info(self):
        url = self.url_entry.get().strip()
        if not url:
            self.update_status("Error: Enter a video URL")
            return
        self.update_status("Fetching video info...")
        
        def worker():
            ydl_opts = {"quiet": True, "skip_download": True}
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    self.video_info = info
                    resolutions = set()
                    for fmt in info.get("formats", []):
                        height = fmt.get("height")
                        if height and height <= 2160:
                            resolutions.add(height)
                    res_list = sorted(list(resolutions))
                    res_strs = [f"{res}p" for res in res_list]
                    self.resolution_combo.configure(values=res_strs)
                    if res_strs:
                        self.resolution_combo.set(res_strs[-1])
                    else:
                        self.resolution_combo.set("Default")
                    self.update_status("Video info fetched successfully.")
            except Exception as e:
                self.update_status(f"Error fetching info: {e}")
        
        threading.Thread(target=worker, daemon=True).start()
    
    def start_download(self):
        url = self.url_entry.get().strip()
        dest_dir = self.dest_entry.get().strip()
        if not url:
            self.update_status("Error: Enter a video URL")
            return
        if not dest_dir:
            self.update_status("Error: Select a destination")
            return
        
        selected_res = self.resolution_combo.get()
        selected_format = self.format_combo.get()
        res_value = None
        if selected_res.endswith("p"):
            try:
                res_value = int(selected_res[:-1])
            except:
                pass
        
        self.update_status("Starting download...")
        
        def download_worker():
            ydl_opts = {
                "outtmpl": f"{dest_dir}/%(title)s.%(ext)s",
                "progress_hooks": [self.update_progress],
                "noplaylist": True,
            }
            if selected_format in ["mp3", "wav"]:
                ydl_opts["format"] = "bestaudio/best"
                ydl_opts["postprocessors"] = [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": selected_format,
                    "preferredquality": "192",
                }]
            else:
                if res_value:
                    ydl_opts["format"] = f"bestvideo[height<={res_value}]+bestaudio/best"
                else:
                    ydl_opts["format"] = "bestvideo+bestaudio/best"
            if self.subtitle_var.get() == "True":
                ydl_opts["writesubtitles"] = True
                ydl_opts["subtitleslangs"] = ["en"]
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                self.update_status("Download complete!")
            except Exception as e:
                self.update_status(f"Download error: {e}")
            self.progress_bar.set(0)
            self.percent_label.configure(text="0%")
        
        threading.Thread(target=download_worker, daemon=True).start()

# --------------------------------
# Main Application with Two Panels
# --------------------------------
class YTDownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Youtubify 3.0")
        self.geometry("1100x850")
        self.resizable(False, False)
        
        # Create a menu bar using CTkMenuBar from the CTkMenuBar package.
        self.menu_bar = CTkMenuBar(master=self, bg_color="#ffffff", height=30, padx=5, pady=5)
        self.menu_bar.add_cascade("About", command=self.show_about)
        self.configure(menu=self.menu_bar)
        
        # Main container frame for two panels
        self.container = ctk.CTkFrame(self, corner_radius=12)
        self.container.pack(pady=20, padx=20, fill="both", expand=True)
        self.container.grid_columnconfigure(0, weight=1, uniform="group1")
        self.container.grid_columnconfigure(1, weight=1, uniform="group1")
        
        # Global log textbox at the bottom
        self.log_text = ctk.CTkTextbox(self, height=150, width=1050, state="disabled", font=("Segoe UI", 12))
        self.log_text.pack(pady=(10, 20), padx=20)
        
        # Left Panel: Playlist Download
        self.playlist_frame = PlaylistFrame(self.container, log_widget=self.log_text, browse_callback=self.browse_directory)
        self.playlist_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Right Panel: Video Download
        self.video_frame = VideoFrame(self.container, log_widget=self.log_text, browse_callback=self.browse_directory)
        self.video_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
    
    def browse_directory(self):
        folder = filedialog.askdirectory()
        if folder:
            # Update destination entries in both panels
            self.playlist_frame.dest_entry.delete(0, "end")
            self.playlist_frame.dest_entry.insert(0, folder)
            self.video_frame.dest_entry.delete(0, "end")
            self.video_frame.dest_entry.insert(0, folder)
    
    def show_about(self):
        about_message = (
            "Youtubify 3.0\n\n"
            "A modern, Notion‑inspired YouTube downloader built with CustomTkinter, yt-dlp, and CTkMenuBar.\n\n"
            "Features:\n"
            " - Playlist and video download modes\n"
            " - Resolution, format, and subtitle options\n"
            " - Destination directory selection\n"
            " - Real‑time progress with percentage and global logging\n\n"
            "Developed by Your Name\n"
            "License: MIT"
        )
        messagebox.showinfo("About Youtubify 3.0", about_message)

if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    # Base theme is blue; red accents are applied manually.
    ctk.set_default_color_theme("blue")
    app = YTDownloaderApp()
    app.mainloop()

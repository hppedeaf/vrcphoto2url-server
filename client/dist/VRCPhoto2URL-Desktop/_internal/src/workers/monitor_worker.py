from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
import os
import time

class MonitorWorker:
    def __init__(self, directory_to_watch, upload_callback):
        self.directory_to_watch = directory_to_watch
        self.upload_callback = upload_callback
        self.observer = Observer()

    def start(self):
        event_handler = PhotoMonitorHandler(self.upload_callback)
        self.observer.schedule(event_handler, self.directory_to_watch, recursive=True)
        self.observer.start()

    def stop(self):
        self.observer.stop()
        self.observer.join()

class PhotoMonitorHandler(FileSystemEventHandler):
    """Enhanced file monitor for photos with auto-upload - VRChat Optimized"""
    
    def __init__(self, callback):
        super().__init__()
        self.callback = callback
        self.photo_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.tif'}
        self.allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.tif', 
                                 '.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.m4v',
                                 '.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma',
                                 '.pdf', '.txt', '.doc', '.docx', '.zip', '.rar', '.7z'}
        self.pending_uploads = {}  # Track files pending upload to avoid duplicates
        
    def on_created(self, event):
        """Handle new file creation with VRChat optimization"""
        if not event.is_directory:
            filepath = event.src_path
            filename = os.path.basename(filepath)
            
            # Check if it's an allowed file type
            if any(filename.lower().endswith(ext) for ext in self.allowed_extensions):
                # Use smart delay for large files (especially VRChat screenshots)
                # VRChat screenshots are typically 3840x2160 and can be 5-10MB
                # Need more time for large files to be fully written
                delay = 5.0 if any(filename.lower().endswith(ext) for ext in self.photo_extensions) else 2.0
                
                # Track this file to avoid duplicate uploads
                self.pending_uploads[filepath] = time.time()
                
                threading.Timer(delay, lambda: self._process_file(filepath)).start()
    
    def on_moved(self, event):
        """Handle file move/rename events (important for VRCX which renames VRChat screenshots)"""
        if not event.is_directory:
            src_path = event.src_path
            dest_path = event.dest_path
            filename = os.path.basename(dest_path)
            
            # Check if destination is an allowed file type
            if any(filename.lower().endswith(ext) for ext in self.allowed_extensions):
                # Remove old path from pending uploads if it exists
                if src_path in self.pending_uploads:
                    del self.pending_uploads[src_path]
                
                # Use shorter delay for moved files since they should already be complete
                delay = 2.0 if any(filename.lower().endswith(ext) for ext in self.photo_extensions) else 1.0
                
                # Track the new path
                self.pending_uploads[dest_path] = time.time()
                
                threading.Timer(delay, lambda: self._process_file(dest_path)).start()
    
    def _process_file(self, filepath):
        """Process file after delay with existence check"""
        try:
            # Remove from pending uploads
            if filepath in self.pending_uploads:
                del self.pending_uploads[filepath]
            
            # Verify file still exists before processing
            if os.path.exists(filepath):
                self.callback(filepath)
            else:
                print(f"⚠️ File monitor: File no longer exists: {os.path.basename(filepath)}")
        except Exception as e:
            print(f"❌ File monitor error: {e}")
import os
import time
from PySide6.QtCore import QThread, Signal

class UploadWorker(QThread):
    """Enhanced upload worker with VRChat optimization and auto features"""
    upload_complete = Signal(str, str, str, int)  # filename, service, url, size
    upload_failed = Signal(str, str)  # filename, error
    upload_progress = Signal(str, int)  # status, percentage
    
    def __init__(self, server_manager):
        super().__init__()
        self.server_manager = server_manager
        self.upload_queue = []
        self.running = False
        
    def add_upload(self, filepath: str):
        """Add file to upload queue"""
        if filepath not in [item['filepath'] for item in self.upload_queue]:
            self.upload_queue.append({
                'filepath': filepath,
                'timestamp': time.time(),
                'filename': os.path.basename(filepath)
            })
    
    def run(self):
        """Process upload queue"""
        self.running = True
        
        while self.running and self.upload_queue:
            try:
                upload_item = self.upload_queue.pop(0)
                filepath = upload_item['filepath']
                filename = upload_item['filename']
                
                self.upload_progress.emit(f"Preparing {filename}", 10)
                
                # Wait for file to be ready
                if not self._wait_for_file_ready(filepath, filename):
                    continue
                
                self.upload_progress.emit(f"Uploading {filename}", 50)
                
                # Upload file
                file_size = os.path.getsize(filepath)
                url, service = self.server_manager.upload_file(filepath)
                
                self.upload_progress.emit(f"Completed {filename}", 100)
                self.upload_complete.emit(filename, service, url, file_size)
                
                time.sleep(0.5)
                
            except Exception as e:
                self.upload_failed.emit(filename, str(e))
        
        self.running = False
    
    def _wait_for_file_ready(self, filepath: str, filename: str) -> bool:
        """Wait for file to be ready with VRChat screenshot optimization"""
        # Enhanced retry logic for large VRChat screenshots (5-10MB files)
        file_size = 0
        try:
            file_size = os.path.getsize(filepath)
        except:
            pass
        
        # Use more retries for large files (VRChat screenshots)
        max_retries = 15 if file_size > 5 * 1024 * 1024 else 10
        
        # File stability checking - ensure file size is stable
        stable_size_checks = 0
        last_size = 0
        
        for retry in range(max_retries):
            try:
                if not os.path.exists(filepath):
                    self.upload_failed.emit(filename, "File not found")
                    return False
                
                # Check current file size
                current_size = os.path.getsize(filepath)
                
                # Test file access
                with open(filepath, 'rb') as test_file:
                    test_file.read(1)
                
                # Check if file size is stable (same size for 3 consecutive checks)
                if current_size == last_size:
                    stable_size_checks += 1
                    if stable_size_checks >= 3:
                        print(f"✅ File ready: {filename} ({current_size} bytes, stable after {retry + 1} attempts)")
                        return True
                else:
                    stable_size_checks = 0
                    last_size = current_size
                
                # Dynamic wait time based on file size and retry count
                if current_size > 5 * 1024 * 1024:  # Large files (>5MB)
                    wait_time = min(3 + retry * 0.5, 8.0)  # 3-8 seconds
                else:
                    wait_time = min(1 + retry * 0.2, 3.0)  # 1-3 seconds
                
                self.upload_progress.emit(f"Waiting for {filename} (attempt {retry + 1})", 20 + retry * 2)
                time.sleep(wait_time)
                
            except PermissionError:
                if retry < max_retries - 1:
                    time.sleep(1 + retry * 0.5)
                    continue
                else:
                    self.upload_failed.emit(filename, "File is locked")
                    return False
            except Exception as e:
                if retry < max_retries - 1:
                    time.sleep(1)
                    continue
                else:
                    self.upload_failed.emit(filename, f"File error: {str(e)}")
                    return False
        
        self.upload_failed.emit(filename, f"File not ready after {max_retries} attempts")
        return False
    
    def stop(self):
        """Stop worker"""
        self.running = False
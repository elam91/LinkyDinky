import threading
import sys
import os
import subprocess

class BotRunner:
    def __init__(self, on_log_callback, on_status_change=None):
        self.process = None
        self.thread = None
        self.running = False
        self.on_log = on_log_callback
        self.on_status_change = on_status_change
        
    def start(self, script="request_minimum", keyword=None):
        if self.running:
            self.on_log("Bot is already running!")
            return
        
        self.running = True
        if self.on_status_change:
            self.on_status_change("running")
        
        self.thread = threading.Thread(target=self._run_bot, args=(script, keyword), daemon=True)
        self.thread.start()
    
    def stop(self):
        if not self.running:
            self.on_log("Bot is not running!")
            return
        
        self.running = False
        if self.on_status_change:
            self.on_status_change("stopped")
        
        self.on_log("Stopping bot...")
        
        if self.process:
            self.process.terminate()
            self.process = None
    
    def _run_bot(self, script, keyword):
        try:
            self.on_log(f"Starting {script}.py...")
            
            script_path = f"{script}.py"
            
            cmd = [sys.executable, "-u", script_path]
            
            if keyword:
                cmd.extend(["--keyword"] + keyword.split())
                self.on_log(f"Using keyword: {keyword}")
            
            self.on_log(f"Running: {' '.join(cmd)}")
            
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            )
            
            for line in iter(self.process.stdout.readline, ''):
                if not self.running:
                    break
                if line.strip():
                    self.on_log(line.strip())
            
            self.process.wait()
            
            if self.process.returncode == 0:
                self.on_log("Bot completed successfully!")
            else:
                self.on_log(f"Bot exited with code: {self.process.returncode}")
            
        except Exception as e:
            self.on_log(f"Error running bot: {str(e)}")
            import traceback
            self.on_log(traceback.format_exc())
        finally:
            self.process = None
            self.running = False
            if self.on_status_change:
                self.on_status_change("idle")

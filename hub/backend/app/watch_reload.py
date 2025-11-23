#!/usr/bin/env python3
"""
File watcher that triggers Flask reload by touching app.py when route files change.
This ensures Flask's reloader detects changes even when files are imported via blueprints.
"""
import os
import sys
import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ReloadTrigger(FileSystemEventHandler):
    def __init__(self, trigger_files):
        self.trigger_files = trigger_files if isinstance(trigger_files, list) else [trigger_files]
        self.last_trigger = 0
        self.debounce_seconds = 0.5  # Prevent multiple triggers for rapid changes
    
    def on_modified(self, event):
        if event.is_directory:
            return
        
        # Only watch Python files
        if not event.src_path.endswith('.py'):
            return
        
        # Ignore __pycache__ and other system files
        if '__pycache__' in event.src_path or event.src_path.endswith('.pyc'):
            return
        
        # Debounce: don't trigger too frequently
        current_time = time.time()
        if current_time - self.last_trigger < self.debounce_seconds:
            return
        
        self.last_trigger = current_time
        
        # Touch the changed file itself AND trigger files to force Flask reload
        # Flask's --extra-files watches the route files directly, so touching the file
        # itself should trigger a reload. Also touch __init__.py to ensure blueprints reload.
        try:
            changed_path = Path(event.src_path)
            
            # Clear pycache for the changed module
            if changed_path.exists():
                pycache_dir = changed_path.parent / '__pycache__'
                if pycache_dir.exists():
                    import shutil
                    try:
                        shutil.rmtree(pycache_dir)
                        print(f"🧹 Cleared __pycache__ for {changed_path.parent}")
                    except:
                        pass
                
                # Touch the changed file itself (Flask watches it via --extra-files)
                os.utime(str(changed_path), None)
            
            # Also touch __init__.py to ensure blueprints are re-imported
            for trigger_file in self.trigger_files:
                if os.path.exists(trigger_file):
                    os.utime(trigger_file, None)
            
            print(f"🔄 Detected change in {event.src_path}, triggering reload...")
        except Exception as e:
            print(f"Error triggering reload: {e}")

def watch_routes():
    """Watch the routes directory and trigger reloads on changes"""
    app_dir = Path(__file__).parent
    routes_dir = app_dir / 'routes'
    trigger_files = [
        str(app_dir / 'app.py'),
        str(app_dir / '__init__.py')
    ]
    
    if not routes_dir.exists():
        print(f"Routes directory not found: {routes_dir}")
        return
    
    print(f"👀 Watching {routes_dir} for changes...")
    print(f"   Trigger files: {', '.join(trigger_files)}")
    
    event_handler = ReloadTrigger(trigger_files)
    observer = Observer()
    observer.schedule(event_handler, str(routes_dir), recursive=True)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    
    observer.join()

if __name__ == '__main__':
    watch_routes()


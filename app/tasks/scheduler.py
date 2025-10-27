# Background service for continuous SLA monitoring
import threading
import time
from datetime import datetime
from app.services.notification_service import NotificationService

class SLAMonitor:
    """Runs every 5 minutes to check for SLA violations"""
    
    def __init__(self, interval=300):  # Default: 5 minutes
        self.interval = interval  # Check interval in seconds
        self.running = False
        self.thread = None
    
    def start(self):
        """Start the SLA monitoring thread"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.thread.start()
            print(f"SLA Monitor started - checking every {self.interval} seconds")
    
    def stop(self):
        """Stop the SLA monitoring thread"""
        self.running = False
        if self.thread:
            self.thread.join()
        print("SLA Monitor stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                print(f"[{datetime.now()}] Checking SLA violations...")
                NotificationService.check_and_notify_sla_violations()
            except Exception as e:
                print(f"Error in SLA monitoring: {e}")
            
            time.sleep(self.interval)

# Global instance
sla_monitor = SLAMonitor()
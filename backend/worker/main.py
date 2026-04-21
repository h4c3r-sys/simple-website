import time
import os

print("Python Worker Service starting...")
print("Connecting to ScyllaDB at:", os.environ.get("SCYLLA_HOST", "localhost"))

def process_background_tasks():
    while True:
        # Here it would poll a queue or database for async tasks
        # like indexing messages for search, sending notifications, etc.
        print("Worker heartbeat...")
        time.sleep(60)

if __name__ == "__main__":
    process_background_tasks()

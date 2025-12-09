import sys
import time

def streaming_text(text, delay=0.1):
    """Simulate streaming output by updating the same line."""
    for i in range(1, len(text) + 1):
        # Overwrite the same line
        sys.stdout.write('\r' + text[:i])
        sys.stdout.flush()
        time.sleep(delay)
    print()  # Move to the next line after completion
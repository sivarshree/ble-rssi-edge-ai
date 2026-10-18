import serial
import csv
import time

# --- CONFIGURATION ---
# Change to your actual COM port (e.g., 'COM3' or '/dev/ttyUSB0')
SERIAL_PORT = 'COM3'  
BAUD_RATE = 115200
SAMPLES_PER_DISTANCE = 200

print("--- RSSI Data Collector Initialized ---")
print(f"Connecting to ESP32 on {SERIAL_PORT}...")

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE)
    time.sleep(2) # Give the ESP32 a moment to stabilize
except Exception as e:
    print(f"Error: Could not connect to {SERIAL_PORT}. Check the port and try again.")
    exit()

# Open CSV in append mode to safely add data
with open('rssi_dataset.csv', mode='a', newline='') as file:
    writer = csv.writer(file)
    
    # Write the column headers if the file is completely new
    if file.tell() == 0:
        writer.writerow(['Distance', 'RSSI'])

    while True:
        # Prompt for the next marker
        distance = input("\nEnter current distance in meters (or type 'q' to quit): ")
        
        if distance.lower() == 'q':
            print("\nData collection complete. Your dataset is safely saved.")
            break
            
        print(f"\nGet ready! Collecting {SAMPLES_PER_DISTANCE} samples for {distance} meters.")
        
        # 3-Second Countdown to stabilize your hand and the beacon
        for i in range(3, 0, -1):
            print(f"Starting in {i}...")
            time.sleep(1)
            
        # THE FIX: Flush the serial buffer of any old "walking" data
        ser.reset_input_buffer() 
        print("Recording now! Hold the beacon steady...")
        
        count = 0
        while count < SAMPLES_PER_DISTANCE:
            if ser.in_waiting > 0:
                try:
                    # Read, decode, and clean the incoming line
                    line = ser.readline().decode('utf-8').strip()
                    rssi = int(line) # Ensure it's a clean integer
                    
                    # Log to CSV
                    writer.writerow([distance, rssi])
                    count += 1
                    
                    # Progress update
                    if count % 50 == 0:
                        print(f"Captured {count}/{SAMPLES_PER_DISTANCE} samples...")
                        
                except ValueError:
                    # Silently ignore any corrupted RF static or text
                    pass 

        print(f"✅ Success! Data for {distance} meters safely logged.")
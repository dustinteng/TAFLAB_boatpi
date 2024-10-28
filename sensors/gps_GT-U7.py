import serial
import time

# Define the serial port and the baud rate
serial_port = '/dev/ttyS0'  # Replace with the correct port if different
baud_rate = 9600
gps = None  # Initialize gps as None for error handling

try:
    # Initialize the serial connection
    gps = serial.Serial(serial_port, baud_rate, timeout=1)
    print("GPS module connected on /dev/ttyS0")

    while True:
        try:
            if gps.in_waiting > 0:  # Check if there's data to read
                data = gps.readline().decode('utf-8', errors='ignore').strip()  # Read a line and decode

                if data.startswith('$GPGGA'):
                    parts = data.split(',')
                    fix_quality = parts[6]

                    # Only print if fix quality is greater than 0 (indicating a valid GPS fix)
                    if fix_quality != '0':
                        time_stamp = parts[1]
                        latitude = parts[2]
                        latitude_direction = parts[3]
                        longitude = parts[4]
                        longitude_direction = parts[5]
                        num_satellites = parts[7]

                        # Display parsed data
                        print(f"Time: {time_stamp}, Latitude: {latitude} {latitude_direction}, "
                              f"Longitude: {longitude} {longitude_direction}, Fix Quality: {fix_quality}, "
                              f"Satellites: {num_satellites}")
                    else:
                        print("No GPS fix yet.")

        except serial.SerialException as e:
            print(f"Serial exception: {e}")
            break  # Break the loop if serial error occurs

        time.sleep(0.5)  # Pause briefly to read incoming data

except serial.SerialException as e:
    print(f"Error opening serial port: {e}")
finally:
    if gps:  # Only close if gps was successfully opened
        gps.close()

import snap7
import time
import keyboard  # Import the keyboard library
from _thread import start_new_thread

def read_barcode_data(plc, db_number, start_byte, size):
    try:
        # Read data from the specified DB starting from the given byte position
        barcode_data = plc.db_read(db_number, start_byte, size)
        barcode_string = barcode_data.decode('ascii', errors='ignore').strip('\x00')
        
        # Find the index of ',' and extract substring starting from that index
        index = barcode_string.find(',')
        if index != -1:
            barcode_string = barcode_string[index + 1:]

        return barcode_string
    except Exception as e:
        print(f"Error: {e}")
        return None

def get_weight_data(plc, db_number, start_byte, size):
    try:
        weight_data = plc.db_read(db_number, start_byte, size)
        weight_string = weight_data.decode('ascii', errors='ignore').strip('\x00')
        index = weight_string.find('+')
        if index != -1:
            weight_string = weight_string[index + 1:]
        return weight_string
    except Exception as e:
        print(f"Error: {e}")
        return None

def get_trigger(plc, db_number, start_byte):
    try:
        data = plc.db_read(db_number, start_byte, 1)  # Read one byte from the specified byte offset
        byte_value = data[0]  # Extract the byte value from the data
        mask = 1 << 0  # Create a mask to extract the specific bit
        return bool(byte_value & mask)  # Check if the specified bit is set
    except Exception as e:
        print(f"Error: {e}")
        return None
def Write_location(plc, location):
    try:
        # Ensure that the location value is within the range of a single byte

        plc.db_write(12, 2, location.to_bytes(2, byteorder='big'))
        plc.db_write(12, 0, b'\x01')
    except Exception as e:
        print(f"Error: {e}")

        
plc_ip = '192.168.6.155'  # Replace with your PLC's IP address
barcode_db_number = 1  # Replace with the DB number where your barcode data is stored
barcode_start_byte = 8  # Replace with the start byte position of your barcode data
barcode_size = 18  # Replace with the size of the barcode data in bytes
weight_db_number = 9
weight_start_byte = 8
weight_size = 30
plc = snap7.client.Client()
plc.connect(plc_ip, 0, 1)  # Connect to the PLC
previous_barcode_data = None

global location
while True:

    
    if keyboard.is_pressed('esc'):  # Check if ESC key is pressed
        print('Disconnecting from PLC')
        break  # Exit the loop if ESC is pressed
    

    
    if get_trigger(plc, barcode_db_number, 0):

        while get_trigger(plc, barcode_db_number,282):
            pass
        barcode_data = int(read_barcode_data(plc, barcode_db_number, barcode_start_byte, barcode_size))
        weight_data = float(get_weight_data(plc, weight_db_number, weight_start_byte, weight_size))
        print("Updated Barcode Data:", barcode_data)
        print("Updated Weight:", weight_data)
        if barcode_data == 100120011268:
            location = 2
        elif barcode_data == 120256789218:
            location = 1
        Write_location(plc,location)       
        while get_trigger(plc, barcode_db_number, 0):   
            pass
        

plc.disconnect()  # Disconnect from the PLC

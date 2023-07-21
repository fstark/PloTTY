def extract_ascii_string(filename):
    with open(filename, 'rb') as file:
        # Set the starting offset to 0x29
        file.seek(0x29)

        # Read bytes until the next occurrence of 0x0d
        ascii_bytes = bytearray()
        byte = file.read(1)
        while byte and byte != b'\x0d':
            ascii_bytes.append(byte[0])
            byte = file.read(1)

        # Convert the extracted bytes into an ASCII string
        ascii_string = ascii_bytes.decode('ascii')

    return ascii_string

print(extract_ascii_string("out.bin"))

import os
import subprocess
import sys
output_dir = "output"


def write_v3_format(data, filename):

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    filepath = os.path.join(output_dir, filename)
    
    # hex word adressed umwandlung
    with open(filepath, "w") as outfile:
        outfile.write("v3.0 hex words addressed\n")
        for i in range(0, len(data), 16):
            chunk = data[i:i+16] # In chunks gruppieren
            address = i
            hex_str = " ".join("{:02X}".format(b) for b in chunk)
            outfile.write("{:04X}: {}\n".format(address, hex_str))
    
    print(f"Datei gespeichert unter {filepath}")

def process_hex_file(input_filename, instr_output_filename, ram_output_filename):
    """Verarbeitet eine v2.0-Hex-Datei von customasm, teilt sie in Befehls- und RAM-Daten (Nach vorher gesetztem Offset) und speichert sie in zwei v3.0-Dateien für logisim"""

    try:
        # customasm.exe main.asm -f logisim8 -o output/main.txt
        # Hier ist customasm entweder installiert oder im gleichen Ordner wie das Skript gebraucht.
        # https://github.com/hlorenzi/customasm
        # cargo install customasm
        if os.name == 'nt':  # Windows
            subprocess.run(["./customasm.exe", input_filename, "-f", "logisim8", "-o", output_dir+"/main.txt"], check=True)
        else:  # Linux/macOS
            subprocess.run(["customasm", input_filename, "-f", "logisim8", "-o", output_dir+"/main.txt"], check=True)
        with open(output_dir+"/main.txt", "r") as f:
            lines = f.readlines()

        hex_data = "".join(lines[1:]).replace(" ", "").strip()
        bytes_data = bytes.fromhex(hex_data)

        instr_data = bytes_data[:65536]
        ram_data = bytes_data[65536:65536*2]  #RAM data (0x1000 to 0x1FFFF) laut offset aus customasm #bankdef

                    
        # letze 00 entfernen, damit die Datei lesbarer bleibt. #res wird hier nicht beinflusst, da logisim sowieso den rest als 00 füllt.
        instr_data = instr_data.rstrip(b'\x00')
        ram_data = ram_data.rstrip(b'\x00')

        write_v3_format(instr_data, instr_output_filename)
        write_v3_format(ram_data, ram_output_filename)



    except FileNotFoundError:
        print(f"Customasm nicht gefunden")
    except subprocess.CalledProcessError as e:
        print(f"customasm fehler: {e}")
    except Exception as e:
        print(f"{e}")


# eigene asm datei kann angegeben werden, indem sie einfach nach dem skriptnamen angegeben wird ./asm.py main.asm ansonsten standardmäßig main.asm
if len(sys.argv) > 1:
    input_filename = sys.argv[1]
else:
    input_filename = "main.asm"

process_hex_file(input_filename, "instructions.rom", "ram.rom")

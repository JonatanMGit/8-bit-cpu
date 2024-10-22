from enum import Enum
import os
output_dir = "output"

class DSTsel(Enum):
    SEL1 = 0b00
    SEL2 = 0b01
    DST_CONST = 0b10
    DST_NONE = 0b11

class SRCsel(Enum):
    SEL1 = 0b00
    SEL2 = 0b01
    SRC_CONST = 0b10
    SRC_NONE = 0b11

class SRCconst(Enum): # A B C D ERG IMML IMMH SP SP_DEC IPL IPH INST DATA(RAM) D_IN(CPU_In)
    A = 0b0000
    B = 0b0001
    C = 0b0010
    D = 0b0011
    ERG = 0b0100
    IMML = 0b0101
    IMMH = 0b0110
    SP = 0b0111
    SP_DEC = 0b1000
    IPL = 0b1001
    IPH = 0b1010
    INST = 0b1011
    DATA = 0b1100
    D_IN = 0b1101

class DSTconst(Enum): # A B C D IMML IMMH OUT IN DATA CLK_ADRD CLK_SP X X X X NULL
    A = 0b0000
    B = 0b0001
    C = 0b0010
    D = 0b0011
    IMML = 0b0100
    IMMH = 0b0101
    OUT = 0b0110
    IN = 0b0111
    DATA = 0b1000
    clkADRD = 0b1001
    CLK_SP = 0b1010
    NULL = 0b1111

class ALUALUopn(Enum):
    ADD = 0b0000
    SUB = 0b0001
    ADC = 0b0010
    SBB = 0b0011
    NAND = 0b0100
    SHIFT = 0b0101

class mabSteuerung(Enum):
    IP_PLUS_1 = 0b000
    NULL = 0b001
    CCCC = 0b010
    CC = 0b011
    START = 0b100

def assemble_micro_instruction(
    SRCconst=0, DstConst=0, DSTsel=0, SrcSel=0, 
    clkOPC=0, writeData=0, clkIP=0, stapelZugriff=0, setIP=0, decIP=0, 
    setSP=0, decSP=0, clkFlags=0, ALUopn=0, mab_steuerung=0
):
    # Bitweise alle Parameter einfügen
    # |= Bitwise OR
    instruction = 0
    instruction |= (SRCconst & 0b1111) << 0     # Bits 0-3
    instruction |= (DstConst & 0b1111) << 4     # Bits 4-7
    instruction |= (DSTsel & 0b11) << 8         # Bits 8-9
    instruction |= (SrcSel & 0b11) << 10        # Bits 10-11
    instruction |= (clkOPC & 0b1) << 12         # Bit 12
    instruction |= (writeData & 0b1) << 13      # Bit 13
    instruction |= (clkIP & 0b1) << 14          # Bit 14
    instruction |= (stapelZugriff & 0b1) << 15  # Bit 15
    instruction |= (setIP & 0b1) << 16          # Bit 16
    instruction |= (decIP & 0b1) << 17          # Bit 17
    instruction |= (setSP & 0b1) << 18          # Bit 18
    instruction |= (decSP & 0b1) << 19          # Bit 19
    instruction |= (clkFlags & 0b1) << 20       # Bit 20
    instruction |= (ALUopn & 0b1111) << 21      # Bits 21-24
    instruction |= (mab_steuerung & 0b111) << 25 # Bits 25-27

    return instruction

# fetch
def fetch():
    return assemble_micro_instruction(DSTsel=DSTsel.DST_NONE.value, SrcSel=SRCsel.SRC_NONE.value, clkOPC=1, clkIP=1, mab_steuerung=mabSteuerung.START.value)

# mov REG1, REG2
def mov():
    return assemble_micro_instruction(SrcSel=SRCsel.SEL1.value, DSTsel=DSTsel.SEL2.value, clkOPC=1, clkIP=1, mab_steuerung=mabSteuerung.START.value)

# add REG1, REG2
def add():
    return assemble_micro_instruction(DSTsel=DSTsel.SEL1.value, clkFlags=1, SrcSel=SRCsel.SRC_CONST.value,SRCconst=SRCconst.ERG.value, ALUopn=ALUALUopn.ADD.value, clkOPC=1, clkIP=1, mab_steuerung=mabSteuerung.START.value)

# sub REG1, REG2
def sub():
    return assemble_micro_instruction(DSTsel=DSTsel.SEL1.value, clkFlags=1, SrcSel=SRCsel.SRC_CONST.value, SRCconst=SRCconst.ERG.value, ALUopn=ALUALUopn.SUB.value, clkOPC=1, clkIP=1, mab_steuerung=mabSteuerung.START.value)

# nand REG1, REG2
def nand():
    return assemble_micro_instruction(DSTsel=DSTsel.SEL1.value, clkFlags=1, SrcSel=SRCsel.SRC_CONST.value, SRCconst=SRCconst.ERG.value, ALUopn=ALUALUopn.NAND.value, clkOPC=1, clkIP=1, mab_steuerung=mabSteuerung.START.value)

# shift REG1 um REG2 stellen
def shift():
    return assemble_micro_instruction(DSTsel=DSTsel.SEL1.value, clkFlags=1, SrcSel=SRCsel.SRC_CONST.value, SRCconst=SRCconst.ERG.value, ALUopn=ALUALUopn.SHIFT.value, mab_steuerung=mabSteuerung.NULL.value)

# cmp reg1, reg2
def cmp():
    return assemble_micro_instruction(DSTsel=DSTsel.DST_NONE.value, clkFlags=1, SrcSel=SRCsel.SRC_NONE.value, ALUopn=ALUALUopn.SUB.value, clkOPC=1, clkIP=1, mab_steuerung=mabSteuerung.START.value)

# store reg1, reg2
def load():
    # ADRD=PP(0)+sel2
    instruction1 = assemble_micro_instruction(DSTsel=DSTsel.DST_CONST.value, DstConst=DSTconst.clkADRD.value, SrcSel=SRCsel.SEL2.value)
    # DATA->sel1
    instruction2 = assemble_micro_instruction(DSTsel=DSTsel.SEL1.value, SrcSel=SRCsel.SRC_CONST.value, SRCconst=SRCconst.DATA.value, mab_steuerung=mabSteuerung.NULL.value)

    return [instruction1, instruction2]

# load reg1, reg2
def store():
    # ADRD=PP(0)+sel1
    instruction1 = assemble_micro_instruction(DSTsel=DSTsel.DST_CONST.value, DstConst=DSTconst.clkADRD.value, SrcSel=SRCsel.SEL1.value)
    # sel2->DATA
    instruction2 = assemble_micro_instruction(DSTsel=DSTsel.DST_CONST.value, DstConst=DSTconst.DATA.value, writeData=1, SrcSel=SRCsel.SEL2.value, mab_steuerung=mabSteuerung.NULL.value)

    return [instruction1, instruction2]

# const cc reg, imm
def const():
    # Immediate -> IMML mit IP+1 und bedingung
    instruction1 = assemble_micro_instruction(DSTsel=DSTsel.DST_CONST.value, DstConst=DSTconst.IMML.value, SrcSel=SRCsel.SRC_CONST.value, SRCconst=SRCconst.INST.value, clkIP=1, mab_steuerung=mabSteuerung.CC.value)
    # IMML -> sel2
    instruction2 = assemble_micro_instruction(DSTsel=DSTsel.SEL2.value, SrcSel=SRCsel.SRC_CONST.value, SRCconst=SRCconst.IMML.value, mab_steuerung=mabSteuerung.NULL.value)

    return [instruction1, instruction2]

def jump(): # jmp cccc imml immh
    # Instruction -> IMMH IP+1
    instruction1 = assemble_micro_instruction(DSTsel=DSTsel.DST_CONST.value, DstConst=DSTconst.IMMH.value, SrcSel=SRCsel.SRC_CONST.value, SRCconst=SRCconst.INST.value, clkIP=1)
    # INstruction -> IMML IP+1
    instruction2 = assemble_micro_instruction(DSTsel=DSTsel.DST_CONST.value, DstConst=DSTconst.IMML.value, SrcSel=SRCsel.SRC_CONST.value, SRCconst=SRCconst.INST.value, clkIP=1, mab_steuerung=mabSteuerung.CCCC.value)
    # IMML, IMMH -> IP
    instruction3 = assemble_micro_instruction(DSTsel=DSTsel.DST_NONE.value, setIP=1, clkIP=1, SrcSel=SRCsel.SRC_NONE.value, mab_steuerung=mabSteuerung.NULL.value)

    return [instruction1, instruction2, instruction3]


# sel2 -> OUT port nach sel1
def out():
    return assemble_micro_instruction(SrcSel=SRCsel.SEL2.value, DSTsel=DSTsel.DST_CONST.value, DstConst=DSTconst.OUT.value, clkOPC=1, clkIP=1, mab_steuerung=mabSteuerung.START.value)

# IN port (sel1) nach sel2
def inp():
    # clock input mit selector 1 (im cpu verbunden)
    instruction1 = assemble_micro_instruction(DstConst=DSTconst.IN.value, DSTsel=DSTsel.DST_CONST.value, SrcSel=SRCsel.SRC_NONE.value)

    instruction2 = assemble_micro_instruction(DSTsel=DSTsel.SEL2.value, SrcSel=SRCsel.SRC_CONST.value, SRCconst=SRCconst.D_IN.value, mab_steuerung=mabSteuerung.NULL.value)

    return [instruction1, instruction2]

# Liste der Makrobefehle (Makroinstruktionen)
macro_instructions = [
    fetch,
    mov,
    add,
    sub,
    nand,
    shift,
    cmp,
    store,
    load,
    const,
    jump,
    out,
    inp

]

# Mikroinstruktionen und Offsets berechnen
def generate_micro_instructions_and_offsets(macro_instructions):
    offsets = []
    micro_instructions = []
    offset = 0

    for macro in macro_instructions:
        offsets.append(offset)               # Aktuellen Offset speichern
        instruction_set = macro() 


        if isinstance(instruction_set, list): # Liste von Instructions
            micro_instructions.extend(instruction_set)
            offset += len(instruction_set)
        else: # nur eine Instruction
            micro_instructions.append(instruction_set)
            offset += 1

    # max 64 start adressen (offsets)
    if offset > 64:
        raise ValueError("Zu viele Makroinstruktionen. Es sind maximal 64 Startadressen möglich.")
    
    # max 256 micro instructions
    if len(micro_instructions) > 256:
        raise ValueError("Zu viele Mikroinstruktionen. Es sind maximal 256 Mikroinstruktionen möglich.")

    return micro_instructions, offsets


def save_micro_program(filename, micro_instructions):

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    filepath = os.path.join(output_dir, filename)
    
    # Mikroinstructionen speicher
    with open(filepath, 'w') as f:
        f.write("v3.0 hex words addressed\n")
        for i, instruction in enumerate(micro_instructions):
            hex_output = format(instruction, '08x').upper()  # In Hex umwandeln, 32 Bit
            f.write(f"{i:02x}: {hex_output}\n")
    
    print(f"Mikroprogramm gespeichert in {filepath}")


def save_offsets(filename, offsets):

    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w') as f:
        f.write("v3.0 hex words addressed\n")
        for i, offset in enumerate(offsets):
            hex_offset = format(offset, '02x').upper()  # In Hex umwandeln, 8 Bit
            f.write(f"{i:02x}: {hex_offset}\n")
    
    print(f"Offsets gespeichert in {filepath}")

# Mikroinstruktionen und Offsets erzeugen
micro_instructions, offsets = generate_micro_instructions_and_offsets(macro_instructions)

# Dateien speichern
save_micro_program('micro_program.rom', micro_instructions)
save_offsets('offset.rom', offsets)

print("Mikroprogramm und Offsets erfolgreich gespeichert.")

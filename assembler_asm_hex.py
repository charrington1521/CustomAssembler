from typing import List, Dict
import os, re
import argparse
from math import ceil

def asm_files_in_dir(dir: str) -> List[str]:
    ''' Extracts .asm files from a directory. For link ordering, requires a
    file named "main.asm" to exist in the directory. Remaining files are
    linked alphabetically. If called on a dir with no .asm files, the 
    program will check for a /asm directory inside.
    @param dir: directory to extract .asm files from.
    @return a list of all the .asm files in dir.
    '''
    toReturn = [file for file in os.listdir(dir) if file[-3:] == "asm"]

    if toReturn == []:
        if dir[-4:] == "/asm":
            raise(Exception(f"No .asm files found in {dir}"))
        else:
            return asm_files_in_dir(dir+"/asm")
    elif not "main.asm" in toReturn:
        raise(Exception(f"No main.asm was found in dir {dir}"))
    else:
        toReturn.remove('main.asm')
        toReturn.insert(0, 'main.asm')
    
        return toReturn

cwd = os.getcwd()

parser=argparse.ArgumentParser(
description='''Links and assembles an "output.hex" file for loading into Logisim. Takes in a number of .asm files or directories as input.''')
parser.add_argument('-m', default='upgraded', help="Mode. 'upgraded' by default. Other option is 'basic' for the basic CPU.")
parser.add_argument('-o', type=str, default=cwd, help="Output location: a path to put output.hex at. Current working directory by default.")
parser.add_argument('-p', nargs='*', default=[], help='An ordered list of paths to link. If none passed the current working directory is used. Paths to directories require one "main.asm" to order the linking.')
args=parser.parse_args()

global PREFIX, INSTRUCTION_SIZE, IMM_SIZE, MODE_SIZE, INSTRUCTION_SET, REGISTERS
if args.m == 'upgraded':
    from constants_upgraded import PREFIX, INSTRUCTION_SIZE, IMM_SIZE, MODE_SIZE, INSTRUCTION_SET, REGISTERS
elif args.m == 'basic':
    from constants_basic import PREFIX, INSTRUCTION_SIZE, IMM_SIZE, MODE_SIZE, INSTRUCTION_SET, REGISTERS
else:
    raise(Exception("Expected a valid assembler mode."))

if args.p == []:
    files_to_link = asm_files_in_dir(cwd)
else:
    files_to_link = []

    for path in args.p:
        if not os.path.exists(path):
            if not os.path.exists(cwd+"/"+path):
                raise(Exception(f"Path {cwd+'/'+path} was not found"))
            else:
                path = cwd+"/"+path
                
        if os.path.isdir(path):
            for file in asm_files_in_dir(path):
                files_to_link.append(file)
        elif os.path.isfile(path):
            assert(path[-3:] == 'asm')
            files_to_link.append(path)
        else:
            raise(Exception(f"Argument {path} is not a directory or .asm file"))

def is_i_type(command: str) -> bool:
    '''
    @param command: a command such as 'addi'
    @return: True if command is I-type. False otherwise.
    '''
    return INSTRUCTION_SET[command][0] != '0b' + '0' * MODE_SIZE

def literal_to_bits(literal: str, pad: int = IMM_SIZE) -> str:
    '''
    @param literal: the number to convert
    @param pad: the total number of bits to occupy. Defauls to Imm size.
    @return: a binary conversion of literal occupying pad bits with 0b removed.
    '''
    if literal[0] == "-":
        num = int(literal[1:])
        num = 2 ** IMM_SIZE - num
    else:
        num = int(literal)

    return bin(num).replace('0b', '').rjust(pad, '0')

def instruction_to_hex(instruction: List[str]) -> str:
    '''
    @param instruction: an assembly instruction parsed in the form [command, args. . .]
    @return: a six-digit hexidecimal conversion of the given instruction. With 0x removed.
    '''
    command = instruction[0].lower()
    if not command in INSTRUCTION_SET:
        raise(Exception(f"Command {command} is not an instruction"))
    
    mode = INSTRUCTION_SET[command][0]
    op  = INSTRUCTION_SET[command][1]

    #could be worthwhile to have a destination = $0 error. . . 
    if not is_i_type(command): #All R-type commands
        dest = REGISTERS[instruction[1]]
        src1 = REGISTERS[instruction[2]]
        src2 = REGISTERS[instruction[3]]

        instruction_bin = "".join([mode, op, dest, src1, src2])

    elif command == 'sw' or command == 'lw':
        offset, register = instruction[2].split('(')
        register = register[:-1]

        reg = REGISTERS[instruction[1]]
        mem = REGISTERS[register]
        imm = literal_to_bits(offset)

        instruction_bin = "".join([mode, op, reg, mem, imm])

    elif command == 'beq' or command == 'bne':
        src1 = REGISTERS[instruction[1]]
        src2 = REGISTERS[instruction[2]]
        imm = literal_to_bits(instruction[3])
    
        instruction_bin = "".join([mode, op, src1, src2, imm])

    elif command == 'j':
        imm = literal_to_bits(instruction[1], pad=INSTRUCTION_SIZE-MODE_SIZE)
    
        instruction_bin = "".join([mode, op, imm])

    else:  #All regular I-type commands
        dest = REGISTERS[instruction[1]]
        src  = REGISTERS[instruction[2]]
        imm  = literal_to_bits(instruction[3])
        
        instruction_bin = "".join([mode, op, dest, src, imm])        
    
    instruction_bin = instruction_bin.replace('0b', '').ljust(INSTRUCTION_SIZE, '0')
    return hex(int(instruction_bin, 2)).replace('0x', '').rjust(ceil(INSTRUCTION_SIZE/4), '0')

def clean(file: str) -> List[List[str]]: 
    ''' Removes whitespace and comments from a .asm file. Convert the file
    into parsed assembly instructions of the form [command, args. . .]
    @param file: file to remove spaces and convert
    @return: a list containing each instruction
    '''
    f_str = ""
    with open(file, "r", encoding='utf8') as f:
        
        for line in f:
            f_str += line.strip() + "\n"

    f_str = re.sub("#.+?\\n", "\n", f_str)

    return [line.split() for line in f_str.split('\n') if len(line) > 0]

def extract_labels(clean_file: List[List[str]]) -> Dict[str, int]:
    '''REMOVES and stores location of label lines in a parsed assembly instruction
    formatted file.
    @param clean_file: a list of parsed assembly instructions.
    @return: a dictionary with labels as keys and their line numbers as values.
    '''
    labels = dict({})

    line_number = 0
    for line in clean_file:
        label = re.findall('[a-zA-Z0-9_ \t]+:', line[0])
        if len(label) > 0:
            assert(len(label) == 1)
            label = label[0]

            if label in labels:
                raise Exception("Label occurs multiple times")
            else:
                label = label[:-1]
                labels[label] = line_number
        else:
            line_number += 1

    for label in labels:
        clean_file.remove([label+':'])

    return labels

if __name__ == '__main__':
    clean_files = [clean(file) for file in files_to_link]
    labels = dict({})
    line_number = 0
    for file in clean_files:
        new_labels = extract_labels(file)

        for label in new_labels:
            if label in labels:
                #multi defn error. . .
                pass
            else:
                labels[label] = new_labels[label] + line_number

        line_number += len(file)

    clean_assembled = []

    line_number = 0
    for file in clean_files:
        for instruction in file:
            if instruction[-1] in labels:
                if instruction[0] == 'j':
                    instruction[-1] = str(labels[instruction[-1]])
                elif instruction[0] == 'beq' or instruction[0] == 'bne':
                    instruction[-1] = str(labels[instruction[-1]] - line_number)
            clean_assembled.append(instruction)
            line_number += 1

    assembled_hex = []
    for instruction in clean_assembled:
        assembled_hex.append(instruction_to_hex(instruction))

    output  = PREFIX
    #Append a $0 clearer?
    output += " ".join(assembled_hex)

    #custom output locations?
    with open(args.o+"/output.hex", "+tw", encoding='utf8') as f:
        f.write(output)





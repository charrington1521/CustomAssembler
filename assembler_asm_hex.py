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
        num = 2 ** pad - num
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
        imm = literal_to_bits((instruction[3]))
    
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
                labels[label] = line_number - 1
        else:
            line_number += 1

    for label in labels:
        clean_file.remove([label+':'])

    return labels

class CleanFile():

    def __init__(self, file_path: str):
        self.clean_file = self.clean(file_path)
        self.name = file_path.split("/")[-1][:-4]
        x = extract_labels(self.clean_file)
        self.labels : Dict[str, int] = x

    def clean(self, file: str) -> List[List[str]]: 
        ''' Removes whitespace and comments from a .asm file. Convert the file
        into parsed assembly instructions of the form [command, args. . .]
        @param file: file to remove spaces and convert
        @return: a list containing each instruction
        '''
        f_str = ""
        with open(file, "r", encoding='utf8') as f:
            
            for line in f:
                f_str += line.strip() + "\n"

        f_str = re.sub("(#.+?\n)", "\n", f_str)
        f_str = re.sub("#", "", f_str)

        return [line.split() for line in f_str.split('\n') if len(line) > 0]

    def is_referred_to(self, label):
        """Returns whether or not a given label occurs in a cleaned file
        @param label: label to check for
        @param clean_file: a cleaned format file
        @param labels: the labels of the given file. Run extract labels to retrieve.
        """
        referrents = [instruction[-1] for instruction in self.clean_file if instruction[-1] in self.labels]

        return label in referrents
    
    def replace_label(self, old_label, new_label):
        """Replaces the old_label with the new_label
        @param old_label: the label to replace
        @param new_label: the label to put in instead
        """
        old = self.labels.pop(label)
        self.labels[self.name + label] = old

    def __len__(self):
        return len(self.clean_file)

if __name__ == '__main__':
    if args.p == []:
        files_to_link = asm_files_in_dir(cwd)
    else:
        files_to_link = []

        for path in args.p:
            if not os.path.exists(path):
                if os.path.exists(cwd+"/"+path):
                    path = cwd+"/"+path
                elif os.path.exists(cwd+"/asm/"+path):
                    path = cwd+"/asm/"+path
                else:
                    if not os.path.exists(cwd+"/"+path):
                        raise(Exception(f"Path {cwd+'/'+path} was not found"))
                    else:
                        raise(Exception(f"Path {cwd+'/asm/'+path} was not found"))
                    
            if os.path.isdir(path):
                for file in asm_files_in_dir(path):
                    files_to_link.append(file)
            elif os.path.isfile(path):
                assert(path[-3:] == 'asm')
                files_to_link.append(path)
            else:
                raise(Exception(f"Argument {path} is not a directory or .asm file"))


    clean_files = [CleanFile(file) for file in files_to_link]
    labels = dict({})
    line_number = 0
    for file in clean_files:
        to_replace = dict({})
        #this does not ensure that all labels in a file are defined and doesnt throw an error
        #if there is an issue because of this
        for label in file.labels:
            is_defined = label in labels
            if file.is_referred_to(label):
                #A local label
                to_replace[label] = file.name + "_" + label
                if label in labels:
                    raise("Bad naming convention of a label in another file")
            elif is_defined:
                raise("Global label defined in multiple files")

            labels[label] = file.labels[label] + line_number

        for label in file.labels:
            labels[label] = file.labels[label] + line_number

        line_number += len(file)

    for label in to_replace:
        old = labels.pop(label)
        labels[to_replace[label]] = old

    clean_assembled = []

    line_number = 0
    for file in clean_files:
        for instruction in file.clean_file:
            label = instruction[-1]
            if label in to_replace.keys():
                label = to_replace[label]

            if label in labels:

                if instruction[0] == 'j':
                    instruction[-1] = str(labels[label] + 1)
                elif instruction[0] == 'beq' or instruction[0] == 'bne':
                    instruction[-1] = str(labels[label] - line_number)

            clean_assembled.append(instruction)
            line_number += 1

    print(to_replace)
    print(labels)
    print(clean_assembled)
    assembled_hex = []
    for instruction in clean_assembled:
        assembled_hex.append(instruction_to_hex(instruction))

    output  = PREFIX
    #Append a $0 clearer?
    output += " ".join(assembled_hex)

    #custom output locations?
    with open(args.o+"/output.hex", "+tw", encoding='utf8') as f:
        f.write(output)





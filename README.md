# Custom Assembler

This repo contains a assembler_asm_hex.py file which can be used 
to convert assembly code to .hex files for use on our custom Logisim CPU. These .hex files can be loaded into the included logisim .circ files at the 
instruction memory of the "Full CPU" to run the code. 

## Setup

Python (version requirement to be decided)
Logisim 2.7.1

---
<a name = "ToC"></a>

## Table of Contents

**[Skip ToC](#usage-and-support)**

**[Usage](#usage-and-support)**

- [Assembling .asm Files](#assembling-a-asm-file)
- [Linking Multiple .asm Files](#linking-multiple-asm-files)
- [Running .hex Files in Logisim](#running-a-hex-file)

**[Implementation](#implementation)**

**[Validation](#validation)**

---

<a name = "Usage"></a>

## Usage and Support

<a name = "Assembling Single"></a>

### Assembling a .asm file

- Create a MIPs style Assembly Language .asm file wherever you would like

- run the following command: ```python assembler_asm_hex.py -p [path to .asm file]``` This command will detect immediately relative file paths (but won't check within sub directories).

- By default this will create an "output.hex" file at the current working directory the command was run from. To specify a separate location, use the ```-o``` flag 

[Return to ToC](#table-of-contents)

### Linking multiple .asm files

- Create multiple MIPs Assembly .asm files wherever you would like

- run the following command: ```python assembler_asm_hex.py -p [path to .asm] [path to .asm] . . . [path to last .asm]``` where the paths are given in linking order, first to last. Labels in .asm files are cross-referenced. For instance defining a label "begin" in multiple linked files will cause an error.  
@Future work will allow for marking global and local labels. 

- One can also place all the .asm files into a "asm" folder and give the path to this instead. In this case, the assembler expects there to be a "main.asm" file to link first. Everything else links alphabetically. 
@Future work will allow a file for specifiying link order. 

[Return to ToC](#table-of-contents)

### Running a .hex File

- In Logisim open the desired .circ file (typically "upgraded")

- Navigate to the "Full CPU" subcircuit. Locate the leftmost memory element. This is the instruction memory. 

- Right click the instruction memory and select "Load Image...". Find and select the output.hex file you would like to run. 

@Future work: .hex files for .data sections of asm files to load into RAM

- Ensure Logisim is in simulation mode (hand icon top left by default) and simulation is enabled (check the simulation menu on the toolbar).

- Toggle the "clk" pin high and low repeatedly until the instruction memory is highlighting an empty line

- The program has been sucessfully run! Double clicking and diving into the register files will allow one to see register results. All memory based results can be viewed in the memory element (RAM) at the far right of the "Full CPU" subcircuit. 

[Return to ToC](#table-of-contents)

## Implementation

In our design we selected a 16-bit CPU, with 16 registers each able to hold words that are two bytes in size. 

The RAM addresses are 16 bits and each word of ram is also two-bytes. 

The 16-bit ALU included uses a standard ripple carry adder.  

In order to represent three registers and all of our included operations, a 21 bit instruction word was chosen. 

We implemented branching and jumping by labels along with multi-file linking in order to assist in the construction of more complicated program structures. 

Labels can be local or global, assumed by whether or not they are referenced within a file. Local labels are handled by appending the containing file’s name at assemble time. This means that naming a label in “main.asm” “other_file_loop.asm” in a linkage with the file “other_file” containing the local label “loop” can cause errors in program execution. 

There are no pseudonyms for branching instructions such as “blt” or ability to parse .data headers in assembly files. 

Furthermore there is no support for a stack pointer and function based jump calls. 

The register $0 is often assumed to have the value 0 within, however, nothing guarantees this behavior in this CPU. 

[Return to ToC](#table-of-contents)

## Validation

See the document at [this link](https://github.com/charrington1521/CustomAssembler/blob/master/HarringtonCollinFinalReport.pdf)

[Return to ToC](#table-of-contents)
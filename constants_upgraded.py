PREFIX = "v2.0 raw\n"

IMM_SIZE = 7

MODE_SIZE = 3

INSTRUCTION_SIZE = 21

REGISTERS = {
    '$0':  '0b0000',

    '$s0': '0b1000',
    '$s1': '0b1001',
    '$s2': '0b1010',
    '$s3': '0b1011',
    '$s4': '0b1010',
    '$s5': '0b1101',
    '$s6': '0b1110',
    '$s7': '0b1111',

    '$t0': '0b0001',
    '$t1': '0b0010',
    '$t2': '0b0011',
    '$t3': '0b0100',
    '$t4': '0b0101',
    '$t5': '0b0110',
    '$t6': '0b0111'
}

INSTRUCTION_SET = {
    'add':      ['0b000', '0b000'],
    'addi':     ['0b111', '0b000'],
    'and':      ['0b000', '0b001'],
    'andi':     ['0b111', '0b001'],
    'or':       ['0b000', '0b010'],
    'ori':      ['0b111', '0b010'],
    'sub':      ['0b000', '0b011'],
    'subi':     ['0b111', '0b011'],

    'lw':       ['0b001', '0b000'], #op code is add
    'sw':       ['0b010', '0b000'], #op code is add

    'beq':      ['0b101', '0b011'], #op code is sub
    'bne':      ['0b110', '0b011'], #op code is sub

    'slt':      ['0b000', '0b110'], 

    'j':        ['0b100', '']       #no op code

}
addi $1 $0 4
addi $2 $0 0
addi $3 $0 0
global:
loop:
beq $1 $2 exit_loop
addi $2 $2 1
addi $3 $3 1
j loop
exit_loop:
bne $2 $3 exit
j skip_def
exit:

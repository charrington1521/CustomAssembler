addi $1 $0 4
addi $2 $0 2
addi $3 $0 0
skip_def:
beq $1 $3 exit
j global
exit:
lw $t1 0($t0)
lw $t2 1($t0)
lw $t3 2($t0)
addi $t0 $t0 3
lw $t4 0($t0)
lw $t5 1($t0)
lw $t6 2($t0)
sw $t1 2($t0)
sw $t2 1($t0)
sw $t3 0($t0)
addi $t0 $t0 -3
sw $t4 2($t0)
sw $t5 1($t0)
sw $t6 0($t0)
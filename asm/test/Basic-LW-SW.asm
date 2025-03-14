#Author: John Rieffel
#Edits by Chris Fernandes
#NOTE: if your instruction word does not support immediates in the range [-6,7], 
# you will need to REWRITE this code in order to work with your processor 
#
# results: values 1..7 should be in memory locations 1..7
# 	       values 7..1 should be in registers 1..7 (7 should be $1, 6 should be in $2, etc.)
#
addi $1 $0 1
addi $2 $0 2
add  $3 $2 $1
add  $4 $2 $2
addi $5 $0 5
add  $6 $2 $4
addi $7 $0 7
sw   $1 1($0)
sw   $2 2($0)
sw   $3 3($0)
sw   $4 3($1)
sw   $5 2($3)
sw   $6 0($6)
sw   $7 7($0)
lw   $1 0($7) 
lw   $2 -1($7) 
lw   $3 -2($7) 
lw   $4 -3($7) 
lw   $5 -4($7) 
lw   $6 -5($7) 
lw   $7 -6($7)

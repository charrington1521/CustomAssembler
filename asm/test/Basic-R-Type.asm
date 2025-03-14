#Author: John Rieffel
#Description: this program should put the values 1..7 into registers 1..7
#Note: this assumes your processor can handle 3-bit signed immediates.  If it cannot, you will need to modify this code.
addi $1 $0 1
addi $2 $0 2
add  $3 $2 $1
add  $4 $2 $2
add $5 $4 $1
add  $6 $2 $4
add $7 $3 $4

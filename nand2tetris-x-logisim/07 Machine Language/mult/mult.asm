// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)

// Put your code here.


@R0
D=M
@ZERO
D;JEQ

@R1
D=M
@ZERO
D;JEQ

@START
0;JMP

(ZERO)
@R2
M=0
@END
0;JMP

(START)
@R2
M=0

(MULTI)
@R0
D=M
@R2
M=M+D
@R1
M=M-1
D=M
@MULTI
D;JNE

(END)
@END
0;JMP

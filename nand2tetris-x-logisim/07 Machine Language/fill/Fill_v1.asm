// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed.
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.
@x
M=-1


(CHECKLOOP)
@KBD
D=M

@SET
D;JNE


@CLEAN
0;JMP


// clear color
(CLEAN)

// reach screen min
@x
D=M
D=D+1

@CHECKLOOP
D;JEQ


@x
D=M
@SCREEN
A=D+A
M=0
@x
M=M-1

@CHECKLOOP
0;JMP


// set color
(SET)

// reach screen max
@x
D=M
@8191
D=D-A

@CHECKLOOP
D;JEQ

// set color
@x
M=M+1
D=M
@SCREEN
A=D+A
M=-1

@CHECKLOOP
0;JMP

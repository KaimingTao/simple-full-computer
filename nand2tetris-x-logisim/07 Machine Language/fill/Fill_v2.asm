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
M=0
@y
M=0


(CHECKLOOP)
@KBD
D=M

@SET
D;JNE

// reach screen max
@x
D=M
@8192
D=D-A
@CHECKLOOP
D;JEQ

@y
D=M
@8192
D=D-A
@CHECKLOOP
D;JEQ

@CLEAN
0;JMP


// clear color
(CLEAN)
@y
M=0

@x
D=M
@SCREEN
A=D+A
M=0
@x
M=M+1

@CHECKLOOP
0;JMP


// set color
(SET)
@x
M=0

@y
D=M
@SCREEN
A=D+A
M=-1
@y
M=M+1

@CHECKLOOP
0;JMP

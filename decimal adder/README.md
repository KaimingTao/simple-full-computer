# Decimal adder

Computer arithmetic operations are fundamentally symbolic. Even basic binary addition relies on underlying symbolic processes involving components like FULL-ADDERS, HALF-ADDERS, XOR, and AND operations.

In computers, decimal numbers are typically converted to binary before being added. Since symbols are essentially strings, an question arises: Can we develop a decimal adder that operates exclusively on decimal symbols without converting them to binary? Such an approach would allow a virtual machine to perform arithmetic purely through string operations.

This project aims to explore that possibility. Currently, it only supports adding natural numbers.

## Two versions of decimal adder

Both versions of the decimal adder follow a similar structure. They first implement a half adder, then build a full adder from it, and finally extend the process to handle addition across any number of digits. As a result, this approach can be applied to any digital carry system, not just decimal addition.

### Rotation list

The rotation list approach envisions a rotor with 10 decimal symbols arranged in order. Rotating the rotor by one position represents either increasing or decreasing a digit by 1.

- Rotating from 0 to 9 signifies a borrow operation.
- Rotating from 9 to 0 signifies a carry operation.

Using this mechanism, a half adder can be constructed.



### Search table

This approach uses a ROM that stores the results of all possible two-digit additions, along with information about whether a carry occurs. With this lookup table, a half adder can be implemented.

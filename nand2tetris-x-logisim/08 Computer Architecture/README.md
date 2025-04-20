Date: 2025-04-20

The [Hack_computer.circ](./Hack_computer.circ) file contains fully functional hack computer and its submodules built from logisim evolution only.

Using Logisim-evolution (v.3.8.0) to create a Hack computer emulator is possible, you don't need to create some special module.

Here is some key issues I've solved:

## Video driver

The hack computer contains a clock divider, the CPU is using slower clock, the video driver is using 16x faster clock (original one). So in a CPU cycle, the 16 bits of one VRAM value can be fully write to the `RGB video` module. The `RGB video` module only supports one pixel per cycle write.


## Keyboard driver

The `Hack` machine language separates memory addressing and accessing in two cycles `@SCREEN\n D=M\n`, so the keyboard module will fetch from keyboard **twice**, but it should be **once**. To prevent this issue, a DQ flip-flop is used, only when two consecutive cycles are addressing the keyboard memory, the value will be read from keyboard, and only in the second cycle.

## Reset is important

Reset is important for starting the computer, otherwise the RAM and VRAM outputs will have `EEEE` values.

## `RAM` module is better than `ROM` module

ROM module don't have **clock** input, so it's hard to control it's feedout speed.

## Convert text machine language to binary machine language file

- please use [to_bin_file.py](../to_bin_file.py)
    - `python to_bin_file.py <filename>`

## `RGB video` module bug

The video module is a bit buggy, 1) the document is not listing it, 2) when set to scale less than 2, the pixel updating order is not the same as how it's programmed by x and y coordinates.

## `ROM` module issue

Set `Asynchronous read` to `Yes`, set `Read write control` to `Whole word read/write only`. Otherwise when addressing the memory by A-instruction, the value for the next C-instruction is from previous memory, not current one.

## Use tunnel more and use probe

## Epilogue

Logisim/Logisim-evolution is among the few publicly available general digital logic/computer simulator. It's powerful but still has some issues on module implementation and documentation. See through it's potential it can be some **professional level vintage computer simulator**. Hope I can use future versions of it to upgrade this hack computer simulator in a more simple way.

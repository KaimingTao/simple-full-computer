# Python3.13

import tkinter as tk

def draw_bitmap(bitmap, pixel_size=4):
    rows = len(bitmap)
    cols = 16  # each 16-bit integer represents 16 pixels

    width = cols * pixel_size
    height = rows * pixel_size

    root = tk.Tk()
    root.title("Bitmap Viewer")
    canvas = tk.Canvas(root, width=width, height=height, bg="white")
    canvas.pack()

    for y, value in enumerate(bitmap):
        for x in range(16):
            bit = (value >> (15 - x)) & 1  # MSB on left
            color = "black" if bit else "white"
            x1 = x * pixel_size
            y1 = y * pixel_size
            x2 = x1 + pixel_size
            y2 = y1 + pixel_size
            canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=color)

    root.mainloop()

# Example usage:
# A checkerboard pattern for testing (alternating 0b1010101010101010 and 0b0101010101010101)
test_bitmap = [(0b1010101010101010 if i % 2 == 0 else 0b0101010101010101) for i in range(512)]
draw_bitmap(test_bitmap)

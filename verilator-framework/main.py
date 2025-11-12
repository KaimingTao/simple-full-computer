import ctypes



def and_gate(a: int, b: int) -> int:
    lib = ctypes.CDLL("./libandgate.dylib")  # or .so on Linux

    lib.and_gate_init()
    lib.and_gate_eval.argtypes = [ctypes.c_int, ctypes.c_int]
    lib.and_gate_eval.restype = ctypes.c_int
    # lib.and_gate_finish()
    return lib.and_gate_eval(a, b)


def compute_and(entry1, entry2, result_label):
    a = entry1.get()
    b = entry2.get()
    result = and_gate(int(a), int(b))
    result_label.config(text=f"Result: {result}")


def main():
    import tkinter as tk
    from tkinter import ttk

    window = tk.Tk()
    window.title("AND Gate")
    
    tk.Label(window, text="Input A (0 or 1):").grid(row=0, column=0)
    entry1 = tk.Entry(window, width=5)
    entry1.grid(row=0, column=1)

    tk.Label(window, text="Input B (0 or 1):").grid(row=1, column=0)
    entry2 = tk.Entry(window, width=5)
    entry2.grid(row=1, column=1)

    tk.Button(window, text="Compute AND", command=
              lambda: compute_and(entry1, entry2, result_label)).grid(row=2, columnspan=2)

    result_label = tk.Label(window, text="Result: ")
    result_label.grid(row=3, columnspan=2)

    window.mainloop()


if __name__ == '__main__':
    main()

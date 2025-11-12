#include "Vand_gate.h"
#include "verilated.h"

extern "C" {
    VerilatedContext* contextp = new VerilatedContext;
    Vand_gate* top = nullptr;

    void and_gate_init() {
        top = new Vand_gate{contextp};
    }

    // a and b must be 0 or 1
    int and_gate_eval(int a, int b) {
        top->a = a;
        top->b = b;
        top->eval();
        return top->y;
    }

    void and_gate_finish() {
        delete top;
        top = nullptr;
        delete contextp;
    }

    int main() {
        return 0;
    }
}

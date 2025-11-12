// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Symbol table internal header
//
// Internal details; most calling programs do not need this header,
// unless using verilator public meta comments.

#ifndef VERILATED_VAND_GATE__SYMS_H_
#define VERILATED_VAND_GATE__SYMS_H_  // guard

#include "verilated.h"

// INCLUDE MODEL CLASS

#include "Vand_gate.h"

// INCLUDE MODULE CLASSES
#include "Vand_gate___024root.h"

// SYMS CLASS (contains all model state)
class alignas(VL_CACHE_LINE_BYTES)Vand_gate__Syms final : public VerilatedSyms {
  public:
    // INTERNAL STATE
    Vand_gate* const __Vm_modelp;
    VlDeleter __Vm_deleter;
    bool __Vm_didInit = false;

    // MODULE INSTANCE STATE
    Vand_gate___024root            TOP;

    // CONSTRUCTORS
    Vand_gate__Syms(VerilatedContext* contextp, const char* namep, Vand_gate* modelp);
    ~Vand_gate__Syms();

    // METHODS
    const char* name() { return TOP.name(); }
};

#endif  // guard

// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See Vand_gate.h for the primary calling header

#include "Vand_gate__pch.h"
#include "Vand_gate__Syms.h"
#include "Vand_gate___024root.h"

void Vand_gate___024root___ctor_var_reset(Vand_gate___024root* vlSelf);

Vand_gate___024root::Vand_gate___024root(Vand_gate__Syms* symsp, const char* v__name)
    : VerilatedModule{v__name}
    , vlSymsp{symsp}
 {
    // Reset structure values
    Vand_gate___024root___ctor_var_reset(this);
}

void Vand_gate___024root::__Vconfigure(bool first) {
    (void)first;  // Prevent unused variable warning
}

Vand_gate___024root::~Vand_gate___024root() {
}

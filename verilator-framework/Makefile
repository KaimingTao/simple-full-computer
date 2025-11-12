# all:
# 	verilator -Wall --cc --lib-create and_gate and_gate.v --top-module and_gate
# 	make -C obj_dir -f Vand_gate.mk

all:
	verilator --cc and_gate.v --exe and_gate_wrapper.cpp --Mdir obj_dir --compiler clang
	make -C obj_dir -f Vand_gate.mk
	clang++ -I/opt/homebrew/Cellar/verilator/5.036/share/verilator/include -I/opt/homebrew/Cellar/verilator/5.036/share/verilator/include/vltstd -fPIC -Os -undefined dynamic_lookup -shared -flat_namespace obj_dir/Vand_gate__ALL.o obj_dir/and_gate_wrapper.o obj_dir/verilated.o obj_dir/verilated_threads.o -Iobj_dir -o libandgate.dylib
	python3.13 main.py

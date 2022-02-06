# riscv-core
a riscv core on a fpga

## Prerequisites
first a simulation in python
- riscv-gnu-toolchain
- `riscv-testes`
- python

then synthesis in the fpga
- fpga?

## Installation

### riscv-testes
```sh
git clone https://github.com/riscv/riscv-tests
cd riscv-tests
git submodule update --init --recursive
autoconf
./configure
make
make install
cd ..
```

### Python
```sh
numpy
pyelftools==0.27
```

## FPGA
### Verilog
### DE-115

## Notes
riscv uses 32-bit instructions. 
pc = 32
phyaddr = 0x80000000

zero, x0, const 0
ra, x1, return addr
sp, x2, stack point
gp, x3, global pointer
tp, x4, thread pointer
t0-2, x5-7, tmp register
s0/fp, x8, saved register/frame pointer
s1, x9, saved register
a0-a1, x10-11, function arguments/return values
a2-7, x12-17, functon arguments
s2-11, x18-27, saed register
t3-6, x28-31, temporary register

there are four main instructions formats: r-type, i-type, s/b-type, and u/j-type.
- r-type (register): such as "add s0, s1, s2" operate on three registers
- i-type (immediate): such as "addi s3, s4, 42"
- s/b-type (store/branch): such as "sw a0, 4(sp)" operates on two registers and 12- or 13-bit signed immediate.
- u/j-type (upper immediate/jump): such as "beq a0, a1, L1" 

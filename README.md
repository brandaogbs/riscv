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

there are four main instructions formats: r-type, i-type, s/b-type, and u/j-type.
- r-type (register): such as "add s0, s1, s2" operate on three registers
- i-type (immediate): such as "addi s3, s4, 42"
- s/b-type (store/branch): such as "sw a0, 4(sp)" operates on two registers and 12- or 13-bit signed immediate.
- u/j-type (upper immediate/jump): such as "beq a0, a1, L1" 

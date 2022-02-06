#!/usr/bin/python3

import struct
import glob
from elftools.elf.elffile import ELFFile

# elf:https://upload.wikimedia.org/wikipedia/commons/e/e4/ELF_Executable_and_Linkable_Format_diagram_by_Ange_Albertini.png

#80000174 <test_2>:
#80000174:       00000093                li      ra,0
#80000178:       00000113                li      sp,0
#8000017c:       00208733                add     a4,ra,sp
#80000180:       00000393                li      t2,0
#80000184:       00200193                li      gp,2
#80000188:       4c771663                bne     a4,t2,80000654 <fail>

regfile = [0]*33
PC = 32

memory = b'\x00'*0x100000 

def reset():
  global memory 
  global regfile
  
  # mem. hard reset 
  regfile = [0]*33
  memory = b'\x00'*0x10000

def memload(paddr, data):
  global memory

  # physical offset
  addr -= 0x8000000
  assert addr >= 0 and addr < len(memory)

def regdump():
  dump = []
  
  for i in range(33):
    if i==0 or i%8 == 0:
      dump += "\n"
    dump += " %3s:%08x" % ("x%d"%i, regfile[i])
  print(''.join(dump))

if __name__ == "__main__":
  for x in glob.glob("riscv-tests/isa/rv32ui-*"):
    if x.endswith(".dump"):
      continue
    with open(x, 'rb') as f:
      print("[test]", x)
      e = ELFFile(f)
      for s in e.iter_segments():
        reset()
        print("paddr: %d"%s.header.p_paddr)
        regdump() 

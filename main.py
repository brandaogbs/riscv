#!/usr/bin/python3

import struct
import glob
from enum import Enum
from elftools.elf.elffile import ELFFile

# elf:https://upload.wikimedia.org/wikipedia/commons/e/e4/ELF_Executable_and_Linkable_Format_diagram_by_Ange_Albertini.png
# https://riscv.org/wp-content/uploads/2019/12/riscv-spec-20191213.pdf

#80000000 <_start>:
#80000000:			 0480006f								 j			 80000048 <reset_vector>

#80000004 <trap_vector>:
#80000004:			 34202f73								 csrr		 t5,mcause
#80000008:			 00800f93								 li			 t6,8
#8000000c:			 03ff0863								 beq		 t5,t6,8000003c <write_tohost>
#80000010:			 00900f93								 li			 t6,9
#80000014:			 03ff0463								 beq		 t5,t6,8000003c <write_tohost>
#80000018:			 00b00f93								 li			 t6,11
#8000001c:			 03ff0063								 beq		 t5,t6,8000003c <write_tohost>
#80000020:			 00000f13								 li			 t5,0
#80000024:			 000f0463								 beqz		 t5,8000002c <trap_vector+0x28>
#80000028:			 000f0067								 jr			 t5
#8000002c:			 34202f73								 csrr		 t5,mcause
#80000030:			 000f5463								 bgez		 t5,80000038 <handle_exception>
#80000034:			 0040006f								 j			 80000038 <handle_exception>

#80000038 <handle_exception>:
#80000038:			 5391e193								 ori		 gp,gp,1337

#8000003c <write_tohost>:
#8000003c:			 00001f17								 auipc	 t5,0x1
#80000040:			 fc3f2223								 sw			 gp,-60(t5) # 80001000 <tohost>
#80000044:			 ff9ff06f								 j			 8000003c <write_tohost>

#80000048 <reset_vector>:
#80000048:			 00000093								 li			 ra,0
#8000004c:			 00000113								 li			 sp,0
#80000050:			 00000193								 li			 gp,0
# ..
#80000170:			 30200073								 mret

#80000174 <test_2>:
#80000174:			 00000093								 li			 ra,0
#80000178:			 00000113								 li			 sp,0
#8000017c:			 00208733								 add		 a4,ra,sp
#80000180:			 00000393								 li			 t2,0
#80000184:			 00200193								 li			 gp,2
#80000188:			 4c771663								 bne		 a4,t2,80000654 <fail>

regfile = [0]*33
PC = 32

memory = b'\x00'*0x10000 

class Opcode(Enum):
	# http://pages.hmc.edu/harris/ddca/ddcarv/DDCArv_AppB_Harris.pdf
	# https://riscv.org/wp-content/uploads/2019/12/riscv-spec-20191213.pdf
	LOAD	 = 0b0000011
	STORE  = 0b0100011
	
	AUIPC  = 0b0010111
	LUI		 = 0b0110111 
	
	JAL		 = 0b1101111
	JALR	 = 0b1100111
	BRANCH = 0b1100011

	IMM		 = 0b0010011
	OP		 = 0b0110011

	MISC	 = 0b0001111
	SYSTEM = 0b1110011

class Funct3(Enum):
	# http://pages.hmc.edu/harris/ddca/ddcarv/DDCArv_AppB_Harris.pdf
	# https://riscv.org/wp-content/uploads/2019/12/riscv-spec-20191213.pdf
	ADD  = SUB = ADDI = 0b000
	SLLI = 0b001
	SLT  = SLTI = 0b010
	SLTU = SLTIU = 0b011

	XOR = XORI = 0b100
	SRL = SRLI = SRA = SRAI = 0b101
	OR	= ORI = 0b110
	AND = ANDI = 0b111

	BEQ  = 0b000
	BNE  = 0b001
	BLT  = 0b100
	BGE  = 0b101
	BLTU = 0b110
	BGEU = 0b111

	LB	= SB = 0b000
	LH	= SH = 0b001
	LW	= SW = 0b010
	LBU = 0b100
	LHU = 0b101

def reset():
	global memory 
	global regfile
	
	# mem. hard reset 
	regfile = [0]*33
	memory = b'\x00'*0x10000

def memload(paddr, data):
	global memory

	# physical offset
	paddr -= 0x80000000
	#print(paddr)
	assert paddr >= 0 and paddr < len(memory)
	
	# mem: pre + data + pos
	memory = memory[:paddr] + data + memory[paddr+len(data):]

def rv32i(paddr):
	paddr -= 0x80000000
	assert paddr >= 0 and paddr < len(memory)
	
	# get the 32-bit instruction (ui, little-endian)
	return struct.unpack("<I", memory[paddr:paddr+4])[0]

def sign_ext(h, l):
	if h & (1 << (l-1)):
		h -= (1 << l)
	return h

def decode(ins, sb, eb):
	return (ins >> eb) & ((1 << (sb-eb+1))-1)

def pipeline():
	### fetch instruction 
	ins = rv32i(regfile[PC])

	### instruction decode
	# decode opcode 
	opcode = Opcode(decode(ins, 6, 0))
	
	#decode immediates for differents formats
	imm_i = sign_ext(decode(ins,31,20), 12)
	imm_s = sign_ext(decode(ins,31,25)<<5 | decode(ins,11,7), 12)
	imm_b = sign_ext(decode(ins,32,31)<<12 | decode(ins,30,25)<<5 | decode(ins,11,8)<<1 | decode(ins,8,7)<<11,13) 
	imm_u = sign_ext(decode(ins,31,12)<<12,32)
	imm_j = sign_ext(decode(ins,31,30)<<20 | decode(ins,30,21)<<1 | decode(ins,21,20)<<11 | decode(ins,19,12)<<12,21)

	#decode destination reg
	rd = decode(ins,11,7)

	#decode source regs
	rs1 = decode(ins,19,15)
	rs2 = decode(ins,24,20)

	rpc = regfile[PC]

	#decode functs
	funct3 = Funct3(decode(ins,14,12))
	funct7 = decode(ins,31,25)

	print("%x %8x %r"% (regfile[PC], ins, opcode))
	if opcode == Opcode.JAL:
		regfile[PC] += imm_j 
	elif opcode == Opcode.IMM:
		print(funct3)
		if funct3 == Funct3.ADDI:
			regfile[rd] = regfile[rs1] + imm_i
			regfile[PC] += 4	
	return True

def regdump():
	dump = []
	for i in range(33):
		if i!=0 and i%8 == 0:
			dump += "\n"
		dump += " %3s:%08x" % ("x%d"%i, regfile[i])
	print(''.join(dump))

if __name__ == "__main__":
	for x in glob.glob("riscv-tests/isa/rv32ui-v-*"):
		if x.endswith(".dump"):
			continue
		with open(x, 'rb') as f:
			reset()
			print("[test]", x)
			e = ELFFile(f)
			for s in e.iter_segments():
				memload(s.header.p_paddr, s.data())
			
			regfile[PC] = 0x80000000 
			while pipeline():
				pass
			regdump()
		break


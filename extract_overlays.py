import struct, capstone, json, collections
b = open('iss2000_pal.z64','rb').read()
def ram(o): return o-0xC00+0x80000000
def rom(r): return r-0x80000000+0xC00
MAIN_END=0x70000   # codegedeelte van het hoofdblok
md = capstone.Cs(capstone.CS_ARCH_MIPS, capstone.CS_MODE_MIPS64|capstone.CS_MODE_BIG_ENDIAN)
md.detail=False
T=0x80003E24
w0=0x0C000000|((T&0x0FFFFFFF)>>2)
M=0xFFFFFFFF
def s16(x): return x-0x10000 if x&0x8000 else x
sites=[o for o in range(0x1000,MAIN_END,4) if struct.unpack_from('>I',b,o)[0]==w0]
loads=[]
for s in sites:
    # loop terug tot begin van basisblok (max 40 instr); stop bij jr/branch/jal vóór s
    st=s-60*4
    vals={}
    ins=list(md.disasm(b[st:s+8], ram(st)))
    for i in ins:
        m=i.mnemonic; ops=[o.strip() for o in i.op_str.split(',')]
        try:
            if m=='lui': vals[ops[0]]=(int(ops[1],16)<<16)&M
            elif m=='ori' and ops[1] in vals: vals[ops[0]]=vals[ops[1]]|int(ops[2],16)
            elif m in('addiu','addi'):
                imm=int(ops[2],16) if not ops[2].startswith('-') else -int(ops[2][1:],16)
                if ops[1]=='$zero': vals[ops[0]]=imm&M
                elif ops[1] in vals: vals[ops[0]]=(vals[ops[1]]+imm)&M
                else: vals.pop(ops[0],None)
            elif m=='subu' and ops[1] in vals and ops[2] in vals: vals[ops[0]]=(vals[ops[1]]-vals[ops[2]])&M
            elif m=='move' and ops[1] in vals: vals[ops[0]]=vals[ops[1]]
            elif m in('jr','j'): vals={}   # basisblok-einde
            elif m=='jal' and i.address!=ram(s): vals={k:v for k,v in vals.items() if k.startswith('$s')}
            elif m in('sw','sb','sh','lw','lb','lbu','lhu','nop','beq','bne','beqz','bnez','beql','bnel','bnezl'):
                if m.startswith('l') and ops[0] in vals: vals.pop(ops[0])
            else:
                vals.pop(ops[0],None)
        except Exception:
            pass
    a0,a1,a2=vals.get('$a0'),vals.get('$a1'),vals.get('$a2')
    loads.append(dict(site=ram(s), rom=a0, ram=a1, size=a2))
json.dump(loads, open('rom_read_sites.json','w'), indent=1)
ok=[l for l in loads if None not in (l['rom'],l['ram'],l['size'])]
print(f"{len(loads)} aanroepen, {len(ok)} volledig herleid, {len(loads)-len(ok)} dynamisch/onzeker")

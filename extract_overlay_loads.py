import struct, capstone, json
b = open('iss2000_pal.z64','rb').read()
md = capstone.Cs(capstone.CS_ARCH_MIPS, capstone.CS_MODE_MIPS64|capstone.CS_MODE_BIG_ENDIAN)
M=0xFFFFFFFF
T=0x80003E24; w0=0x0C000000|((T&0x0FFFFFFF)>>2)
def resolve(blob_rom, blob_ram, site_off):
    st=max(blob_rom, site_off-60*4)
    vals={}
    base=blob_ram+(st-blob_rom)
    for i in md.disasm(b[st:site_off+8], base):
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
            elif m in('jr','j'): vals={}
            elif m=='jal' and i.address!=base+(site_off-st): vals={k:v for k,v in vals.items() if k.startswith('$s')}
            elif m in('sw','sb','sh','nop','beq','bne','beqz','bnez','beql','bnel','bnezl'): pass
            elif m.startswith('l') and m!='lui': vals.pop(ops[0],None)
            else: vals.pop(ops[0],None)
        except Exception: pass
    return vals.get('$a0'),vals.get('$a1'),vals.get('$a2')
if __name__=='__main__':
    blobs=json.load(open('/mnt/user-data/outputs/iss2000-analysis/overlays.json'))
    known={(int(x['rom_start'],16),int(x['ram'],16),int(x['size'],16)) for x in blobs}
    out=[]
    for x in blobs:
        r=int(x['rom_start'],16); a=int(x['ram'],16); s=int(x['size'],16)
        for off in range(r,r+s,4):
            if struct.unpack_from('>I',b,off)[0]==w0:
                rr,aa,ss=resolve(r,a,off)
                out.append(dict(overlay=hex(r),site=hex(a+off-r),rom=rr,ram=aa,size=ss))
    ok=[o for o in out if None not in (o['rom'],o['ram'],o['size'])]
    print(len(out),"aanroepen in overlays;",len(ok),"herleid")
    for o in out:
        print(o['overlay'],o['site'],
              [f"{o[k]:X}" if o[k] is not None else None for k in('rom','ram','size')])
    json.dump(out,open('overlay_internal_loads.json','w'),indent=1)

"""Nagebouwde decompressor voor ISS 2000 (methode 0 van 0x800082A8). Afgeleid uit de MIPS-code."""
import struct, zlib
def decompress(rom: bytes, start: int):
    hdr = struct.unpack_from('>I', rom, start)[0]
    if hdr & 0x80000000:               # bit31: 4-byte kop (0x80000000|lengte) + standaard zlib-stream
        total = hdr & 0x7FFFFFFF
        d = zlib.decompressobj(); out = d.decompress(rom[start+4:start+total])
        if not d.eof: raise ValueError("zlib-stream onvolledig")
        return out, total - len(d.unused_data), total
    if hdr & 0xF0000000: raise ValueError(f"methode {hdr>>28} niet geimplementeerd")
    total = hdr                       # gecomprimeerde lengte incl. kop
    pos = start + 4; end = start + total
    out = bytearray()
    while pos < end:
        c = rom[pos]; pos += 1
        if c & 0x80 == 0:
            length = (c >> 2) + 2
            dist = ((c & 3) << 8) | rom[pos]; pos += 1
            if dist == 0 or dist > len(out): raise ValueError(f"ongeldige afstand {dist} bij uitvoer {len(out):X}")
            for _ in range(length): out.append(out[-dist])
        elif c < 0xA0:
            n = c & 0x1F
            out += rom[pos:pos+n]; pos += n
        elif c < 0xE0:
            n = (c & 0x1F) + 2
            out += bytes([rom[pos]]) * n; pos += 1
        elif c < 0xFF:
            out += bytes((c & 0x1F) + 2)
        else:
            n = rom[pos] + 2; pos += 1
            out += bytes(n)
    return bytes(out), pos - start, total


def read_asset(rom: bytes, start: int, end: int, flagged: bool) -> bytes:
    """Leest een asset zoals het spel: vlag gezet (bit31 van het beginadres in de tabel) -> gecomprimeerd
    (zlib als bit31 van de kop gezet is, anders de eigen LZ), vlag niet gezet -> ruwe bytes."""
    if not flagged:
        return rom[start:end]
    return decompress(rom, start)[0]

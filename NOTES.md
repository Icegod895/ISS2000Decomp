# ISS 2000 (PAL, N64): analyse-notities

Status: eerste verkenning (stap 1 en 2). Alles hieronder is afgeleid uit de ROM zelf; niets is bevestigd door uitvoeren in een emulator.

## ROM
- Bestand: V64 (byte-swapped), 16 MB. Omgezet naar z64 (big-endian).
- SHA1 (z64): `e7078e5f1e899382b1cc145df43ee8cfaa924297`
- Naam `I.S.S.2000`, gamecode `NISX`, regio X (PAL), versie 0
- CIC 6102, clock 0x0000000F, entrypoint `0x80000400`
- CRC1 `336364A0`, CRC2 `06C8D5BF`

## Opstart
- Hoofdblok: ROM `0x1000` naar RAM `0x80000400`, 1:1 (RAM = ROM - 0xC00 + 0x80000000).
- Entry wist BSS vanaf `0x8009DD20` (lengte 0x10F7D0 bytes), zet stack `0x800CC370`, springt naar main `0x80000814`.
- Hoofdblok (code + data) loopt tot ongeveer ROM `0x9E920`. Code zelf ongeveer tot ROM `0x70000`.

## Grafische microcode (relevant voor RT64)
- `RSP Gfx ucode F3DEX fifo 2.06` op ROM `0x9AC28`
- `RSP Gfx ucode F3DLX.Rej fifo 2.06` op ROM `0x9B048`
- Beide standaard Nintendo (1998). F3DLX.Rej moet nog gecontroleerd worden tegen RT64.

## Libultra-functies (herkend)
| RAM | Functie |
|---|---|
| `0x80058670` | `__osEPiRawStartDma` (patroon, niet bevestigd) |
| `0x80058860` | `osEPiStartDma` |
| `0x80058900` | `osPiStartDma` |
| `0x80003D54` | game-wrapper rond osEPiStartDma (PI-handle, wacht op bericht) |
| `0x80003E24` | `rom_read(rom_adres, ram_dest, grootte)` (naam is van ons) |

## Overlays / segmenten
De game laadt segmenten met `rom_read(begin, bestemming, eind - begin)`; de waarden zijn constanten in de code.
- Hoofdblok: 49 aanroepen, 41 herleid.
- Overlay `0x2DEE70` (RAM `0x801AD820`, de wedstrijd-engine) bevat zelf een grote laadroutine rond `0x801B6608` tot `0x801B79D0`: 39 aanroepen, 37 herleid.
- Totaal **72 unieke segmenten** (zie `segments.json`).
- Meerdere segmenten delen dezelfde RAM-slot (o.a. `0x801EB960`, `0x801AD820`, `0x8027D380`, `0x8029EEA0`), dus ze worden gewisseld naargelang de gamestatus. De overlay-grenzen moeten daarom als aparte linker-segmenten met overlappende RAM-adressen worden opgezet.

| ROM start | ROM end | Grootte | RAM-adres | Gevonden in |
|---|---|---|---|---|
| 0x25AAF0 | 0x287AB0 | 0x2CFC0 | 0x801AD820 | main |
| 0x287AB0 | 0x298280 | 0x107D0 | 0x801DB100 | main |
| 0x298280 | 0x29D870 | 0x55F0 | 0x801EB960 | main |
| 0x29D870 | 0x2A32A0 | 0x5A30 | 0x801EB960 | main |
| 0x2B0E60 | 0x2BC720 | 0xB8C0 | 0x801EB960 | main |
| 0x2BC720 | 0x2BCB90 | 0x470 | 0x801EB960 | main |
| 0x2C4920 | 0x2C7000 | 0x26E0 | 0x801EB960 | main |
| 0x2C99E0 | 0x2D3980 | 0x9FA0 | 0x801AD820 | main |
| 0x2D3980 | 0x2D65E0 | 0x2C60 | 0x801AD820 | main |
| 0x2D65E0 | 0x2D7530 | 0xF50 | 0x803EB000 | main |
| 0x2D7530 | 0x2DEE70 | 0x7940 | 0x803EB000 | main |
| 0x2DEE70 | 0x314A80 | 0x35C10 | 0x801AD820 | main |
| 0x314A80 | 0x315400 | 0x980 | 0x801ED700 | main |
| 0x315400 | 0x316D00 | 0x1900 | 0x801ED700 | main |
| 0x316D00 | 0x318660 | 0x1960 | 0x801ED700 | main |
| 0x318660 | 0x3248C0 | 0xC260 | 0x801EF060 | overlay 0x2dee70 |
| 0x3248E0 | 0x326630 | 0x1D50 | 0x801FEA80 | overlay 0x2dee70 |
| 0x326630 | 0x32A300 | 0x3CD0 | 0x801EF060 | main |
| 0x32AE00 | 0x376010 | 0x4B210 | 0x803AC000 | overlay 0x2dee70 |
| 0x376010 | 0x386080 | 0x10070 | 0x802A4380 | main |
| 0x386080 | 0x3A7B10 | 0x21A90 | 0x802B57E0 | main |
| 0x3A7B10 | 0x3AC9A0 | 0x4E90 | 0x8027D380 | main |
| 0x3AC9A0 | 0x3B47E0 | 0x7E40 | 0x80297040 | overlay 0x2dee70 |
| 0x3B47E0 | 0x3C69D0 | 0x121F0 | 0x8029EEA0 | overlay 0x2dee70 |
| 0x3C69D0 | 0x3D0680 | 0x9CB0 | 0x802B1110 | overlay 0x2dee70 |
| 0x3D0680 | 0x3DCC70 | 0xC5F0 | 0x802BAE10 | overlay 0x2dee70 |
| 0x3DCC70 | 0x3E3040 | 0x63D0 | 0x802C7830 | overlay 0x2dee70 |
| 0x3E3040 | 0x3E83D0 | 0x5390 | 0x8027D380 | overlay 0x2dee70 |
| 0x3E83D0 | 0x3F34F0 | 0xB120 | 0x8029EEA0 | overlay 0x2dee70 |
| 0x3F34F0 | 0x3FC9F0 | 0x9500 | 0x802AA060 | overlay 0x2dee70 |
| 0x3FC9F0 | 0x401910 | 0x4F20 | 0x802B35B0 | overlay 0x2dee70 |
| 0x401910 | 0x40C7A0 | 0xAE90 | 0x802B8500 | overlay 0x2dee70 |
| 0x40C7A0 | 0x41B4F0 | 0xED50 | 0x802C3490 | overlay 0x2dee70 |
| 0x41B4F0 | 0x427BF0 | 0xC700 | 0x802B8500 | overlay 0x2dee70 |
| 0x427BF0 | 0x436A00 | 0xEE10 | 0x8029EEA0 | overlay 0x2dee70 |
| 0x436A00 | 0x445DF0 | 0xF3F0 | 0x802AE200 | overlay 0x2dee70 |
| 0x445DF0 | 0x4534E0 | 0xD6F0 | 0x802BDAF0 | overlay 0x2dee70 |
| 0x4534E0 | 0x460DA0 | 0xD8C0 | 0x8029EEA0 | overlay 0x2dee70 |
| 0x460DA0 | 0x4689A0 | 0x7C00 | 0x802ACDB0 | overlay 0x2dee70 |
| 0x4689A0 | 0x46FC80 | 0x72E0 | 0x802B4B10 | overlay 0x2dee70 |
| 0x46FC80 | 0x481680 | 0x11A00 | 0x8029EEA0 | overlay 0x2dee70 |
| 0x481680 | 0x484E10 | 0x3790 | 0x802B1070 | overlay 0x2dee70 |
| 0x484E10 | 0x490F40 | 0xC130 | 0x802B8EB0 | overlay 0x2dee70 |
| 0x490F40 | 0x499D90 | 0x8E50 | 0x802B1110 | overlay 0x2dee70 |
| 0x499D90 | 0x49D610 | 0x3880 | 0x802BAE10 | overlay 0x2dee70 |
| 0x49D610 | 0x4A26A0 | 0x5090 | 0x802CDCB0 | overlay 0x2dee70 |
| 0x4A26A0 | 0x4A41C0 | 0x1B20 | 0x8027D380 | overlay 0x2dee70 |
| 0x4A41C0 | 0x4A6820 | 0x2660 | 0x8022DF30 | main |
| 0x4A6820 | 0x4DFA40 | 0x39220 | 0x80230590 | main |
| 0x4DFA40 | 0x4E51D0 | 0x5790 | 0x8026D730 | main |
| 0x4E51D0 | 0x4EDA30 | 0x8860 | 0x80272EF0 | main |
| 0x4EDA30 | 0x4F19E0 | 0x3FB0 | 0x8026D730 | main |
| 0x4F19E0 | 0x4F6A20 | 0x5040 | 0x802718F0 | main |
| 0x4F6A20 | 0x4FC4E0 | 0x5AC0 | 0x80276930 | main |
| 0x4FC4E0 | 0x501520 | 0x5040 | 0x80222480 | main |
| 0x501530 | 0x5021D0 | 0xCA0 | 0x80201280 | main |
| 0x5085D0 | 0x508BF0 | 0x620 | 0x80270140 | main |
| 0x508C30 | 0x508ED0 | 0x2A0 | 0x802D5E00 | overlay 0x2dee70 |
| 0x508ED0 | 0x50A1D0 | 0x1300 | 0x802D5E00 | overlay 0x2dee70 |
| 0x50A1D0 | 0x50B4D0 | 0x1300 | 0x802D5E00 | overlay 0x2dee70 |
| 0x50B4D0 | 0x50C3E0 | 0xF10 | 0x803FAF60 | overlay 0x2dee70 |
| 0x50C3E0 | 0x5103D0 | 0x3FF0 | 0x803FAF60 | overlay 0x2dee70 |
| 0x5103D0 | 0x514580 | 0x41B0 | 0x803FAF60 | overlay 0x2dee70 |
| 0x514580 | 0x514950 | 0x3D0 | 0x802DD400 | overlay 0x2dee70 |
| 0x514950 | 0x515160 | 0x810 | 0x802DD400 | overlay 0x2dee70 |
| 0x515160 | 0x515890 | 0x730 | 0x802DD400 | overlay 0x2dee70 |
| 0x515890 | 0x516CE0 | 0x1450 | 0x807AA000 | main |
| 0x516CE0 | 0x523120 | 0xC440 | 0x801EF060 | main |
| 0x523120 | 0x5645E0 | 0x414C0 | 0x80212700 | main |
| 0x564670 | 0x572EB0 | 0xE840 | 0x80257310 | main |
| 0x572EB0 | 0x57F870 | 0xC9C0 | 0x803C4F80 | main |
| 0x57F870 | 0x581DD0 | 0x2560 | 0x803D1A30 | main |

## Debug-controle op `0x80003A18` (geen kopieerbeveiliging)
- Leest `0xBFF00000` en vergelijkt met `"KMC\0"` (Kyoto Microcomputer-ontwikkelhardware).
- Anders vergelijkt het ROM[0..0x100] met 0x100 bytes op ROM-offset `0x1000000` (achter het einde, gespiegeld op een echte cartridge).
- Bij een verschil worden de pointers `0x8006CFB4` en `0x8006CFB0` omgezet van lege stubs (`0x8005D8D0`, `0x8005D8E4`) naar echte debug-printfuncties (`0x80003B10`, `0x80003B4C`, die `_Printf` aanroepen). Op echte hardware blijven het stubs.
- Er wordt ook `"IS64"` naar `0xB1FF0000` geschreven (IS-Viewer 64 debug-interface).
- Gevolg voor de port: niets omzeilen. Zorg dat een ROM-read voorbij het einde de gespiegelde data teruggeeft, of laat de stubs gewoon staan.

## Compiler en code-indeling hoofdblok
Gemeten aan hoe simpele registerkopieën (`move`) zijn gecodeerd:
| Regio | `daddu`-kopieën | `addu`-kopieën | `or`-kopieën |
|---|---|---|---|
| Gamecode `0x80000400` - `0x80058000` | 3239 | 0 | 0 |
| Libultra `0x80058400` - `0x80068800` | 0 | 839 | 0 |
| Overlays samen | 21768 | 171 | 153 |

- Gamecode gebruikt uitsluitend `daddu`. Dat past bij **GCC** met 64-bit registers (waarschijnlijk een KMC GCC 2.7.x-variant) en niet bij IDO.
- Libultra is met andere vlaggen gebouwd (`addu`), zoals gebruikelijk bij Nintendo's eigen bibliotheek.
- Grenzen zijn op 0x400 nauwkeurig; de exacte functiegrens moet nog worden vastgesteld.
- Geen `$gp`-gebruik in de gamecode.
- Nog **niet bevestigd**: de exacte GCC-versie en vlaggen. Dat vereist een testcompilatie van een bekende functie.
- Libultra-versie nog niet vastgesteld.

## Asset-index #1 (ROM `0x9E920` - `0x25A600`)
Gevonden via de laadfunctie `0x80028AA4(item_struct, index)`, die `rom_read(rom, ram, size)` aanroept met waarden uit tabellen:
| Functie | Doet | Tabel (RAM) |
|---|---|---|
| `0x800284A0(i)` | ROM-offset = `0x9E920 + u32[i]` | `0x800780B0` |
| `0x800284C0(i)` | grootte (u16) | `0x800788F0` |
| `0x80028488(i)` | veld16 | `0x80077C90` |
| `0x800284D8(i)` | type (u8) | `0x80078D10` |
| `0x800284EC(i)` | veld32 | `0x80078F20` |

- 528 items, allemaal binnen de ROM, offsets oplopend.
- De ruimte tot het volgende item is bij 494 van 527 items **exact 56 x grootte**.
- Items beginnen met een oplopende u16-lijst (`0, 1, 2, ...`); veld16 is bij de eerste items `0x6E` (110).
- Hypothese: elk item is een clip van N frames; grootte = 2N (index-lijst), per frame 110 bytes, totaal 112N = 56 x grootte. Mogelijk spelersanimaties. **Aanname, nog niet bevestigd.**
- Het loopt tot `0x25A600`, kort voor het eerste overlay-segment op `0x25AAF0`.
- Volledige tabel: `asset_index_1.json`.

## Audio-banken (ROM vanaf `0x581DD0`)  [CORRECTIE: dit is geen compressie]
Eerdere versie van deze notities noemde dit een eigen gecomprimeerd formaat. Dat was fout: het zijn standaard Nintendo-audiobestanden.

- De functie rond `0x8004C000` is de **audio-initialisatie**. De configuratie bevat `0xAC44` = 44100 Hz. Een lus leest vier blokken uit de ROM met `eind[i] - begin[i]` als lengte (`0x8004B5A0` is de leesfunctie).
- Lijsten met ROM-adressen in het hoofdblok (begin/eind-paren, `eind[i] = begin[i+1]`):

| Lijst | ROM | RAM | Items |
|---|---|---|---|
| A (begin) | `0x88360` | `0x80087760` | >=55 |
| B (eind) | `0x8843C` | `0x8008783C` | 110 |
| C (begin) | `0x88640` | `0x80087A40` | 28 |
| D (eind) | `0x886B0` | `0x80087AB0` | 28 |

- Items in A/B beginnen met `42 31` = revisie `'B1'` van een **ALBankFile** (.ctl). Gecontroleerd op het eerste item (ROM `0x5893F0`, `0x7540` bytes): `bankCount=1`, bank op +`0x7260`, **178 instrumenten**, **sampleRate 44100**, alle pointers binnen het bestand; instrument 0: volume 127, pan 64, bendRange 200, 1 sound; wavetable type 0 (**ADPCM**), basis `0x0`, lengte `0x2950`.
- De "lengtevelden" uit de kop waren dus bankoffsets binnen het bestand; daarom klopten ze niet met `eind - begin`.
- Alleen het eerste bestand is volledig gecontroleerd; de overige items in A/B/C/D zijn nog niet geparsed.
- Hypothese (niet gecontroleerd): de dichte data in de rest van dit gebied (entropie ~7,3-7,7) is ADPCM-sampledata (.tbl) en sequenties, geen zlib.
- C/D (28 items, begin `00 00 xx xx 9F 00 ...`) is waarschijnlijk sequence-data; nog niet onderzocht.
- De 45 echte zlib-streams (kop `78 xx`, o.a. rond `0xC62C1C` en `0xE78B6C`) zijn een apart verhaal; de inflate-code zit in het segment op `0x8027D380`.

## Onverklaarde ROM-gebieden (nog geen vaste laadconstanten gevonden)
Totaal ongeveer 12,3 MiB. Waarschijnlijk assets die via een tabel/index worden geladen.
- ~~`0x9E920` - `0x25AAF0`~~: verklaard, zie Asset-index #1.
- `0x2A32A0` - `0x2B0E60`, `0x2BCB90` - `0x2C4920`, `0x2C7000` - `0x2C99E0`, `0x5021D0` - `0x5085D0`
- `0x581DD0` - `0x1000000` (10,5 MiB, entropie ~7,3-7,7): bevat audio-banken (zie boven); de rest nog onbekend

Correctie op een eerdere gok: `0x515890` (RAM `0x807AA000`) is geen tabel maar een klein codesegment.

## Open punten
- Dynamische `rom_read`-aanroepen: `0x80008900`, `0x8002864C`, `0x80028AF8`, `0x8004B5A8`, `0x800539E0`, `0x80055F28`, `0x80055F70` (hoofdblok) en `0x802A489C`, `0x8027D448` (overlays). Dit zijn waarschijnlijk generieke asset-loaders; de aanroepers vinden levert de asset-tabel op.
- Nog niets in een emulator geverifieerd.

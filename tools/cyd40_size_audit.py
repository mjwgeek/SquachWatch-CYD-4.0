"""Inspect linked CYD40 ELF sizes; report only, never relax image validation."""
from collections import Counter, defaultdict
from hashlib import sha256
from pathlib import Path
import shutil
import subprocess

from elftools.elf.elffile import ELFFile

LIMIT = 0x1e0000
out = Path("size-audit")
out.mkdir(exist_ok=True)
for profile in ("cyd40", "cyd40-fast"):
    root = Path(".pio/build") / profile
    binary = root / "firmware.bin"
    size = binary.stat().st_size
    print(f"\n=== {profile}: image {size:,}, slot {LIMIT:,}, free {LIMIT-size:,} ===")
    with (root / "firmware.elf").open("rb") as src:
        elf = ELFFile(src)
        print("Allocated sections (NOBITS is RAM only):")
        for sec in elf.iter_sections():
            if sec["sh_flags"] & 2 and sec["sh_size"]:
                print(f'{sec["sh_size"]:>9,}  {sec.name:30} {sec["sh_type"]}')
        table = elf.get_section_by_name(".symtab")
        if table is None:
            print("No symbol table available")
            continue
        unique = {}
        for sym in table.iter_symbols():
            index = sym["st_shndx"]
            n = sym["st_size"]
            kind = sym["st_info"]["type"]
            if not isinstance(index, int) or not n or kind not in ("STT_FUNC", "STT_OBJECT"):
                continue
            sec = elf.get_section(index)
            if not (sec["sh_flags"] & 2) or sec["sh_type"] == "SHT_NOBITS":
                continue
            key = (index, sym["st_value"], n)
            unique.setdefault(key, (sym.name, kind, sec.name))
        cxxfilt = next(iter(Path.home().glob(".platformio/packages/toolchain-xtensa-esp32/bin/xtensa-esp32-elf-c++filt")), None)
        names = list(dict.fromkeys(v[0] for v in unique.values()))
        decoded = {}
        if cxxfilt and names:
            try:
                dem = subprocess.run([str(cxxfilt)], input="\n".join(names)+"\n",
                                     text=True, capture_output=True, check=True).stdout.splitlines()
                if len(dem) == len(names):
                    decoded = dict(zip(names, dem))
            except (OSError, subprocess.SubprocessError):
                pass
        totals = Counter()
        groups = defaultdict(list)
        for (index, addr, n), (name, kind, section) in unique.items():
            totals[(kind, section)] += n
            if kind == "STT_OBJECT" and n >= 64:
                sec = elf.get_section(index)
                if sec["sh_flags"] & 1:
                    continue
                offset = addr-sec["sh_addr"]
                if 0 <= offset and offset+n <= sec["sh_size"]:
                    data = sec.data()[offset:offset+n]
                    groups[(n, sha256(data).hexdigest())].append(decoded.get(name,name))
        print("Largest linked functions/objects (top 80, bytes; aliases deduplicated):")
        rows = sorted(unique.items(), key=lambda entry: entry[0][2], reverse=True)
        for (_, _, n), (name, kind, section) in rows[:80]:
            print(f"{n:>9,} {kind:10} {section:22} {decoded.get(name,name)}")
        print("Identical read-only objects at different addresses (potential savings, not proof of safe aliasing):")
        for (n, digest), group in sorted(groups.items(), key=lambda item: item[0][0]*(len(item[1])-1), reverse=True)[:50]:
            if len(group)>1:
                print(f"{n*(len(group)-1):>8,} bytes: {n} x {len(group)}: {' | '.join(group)}")
        with (out / f"{profile}-symbols.tsv").open("w") as dst:
            dst.write("bytes\tkind\tsection\tsymbol\n")
            for (_, _, n), (name, kind, section) in rows:
                dst.write(f"{n}\t{kind}\t{section}\t{decoded.get(name,name)}\n")
    for mapfile in root.glob("*.map"):
        shutil.copy2(mapfile, out / f"{profile}-{mapfile.name}")

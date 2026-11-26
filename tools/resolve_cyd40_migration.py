#!/usr/bin/env python3
"""One-time, pinned v1.40 -> current upstream migration. Never publishes."""
import subprocess as sp
import re
from pathlib import Path

def git(*args):
    return sp.check_output(["git", *args], text=True)

def old(path):
    return git("show", "dc5cb2bbefbdf7dfba6758ceb4a0a501ae84b94d:" + path)

# These are the actual conflicts from Actions run 45763915734.
# Refuse new/unreviewed conflict shapes instead of applying blanket -X ours/theirs.
counts = {"README.md":4,"docs/FAQ.md":1,"include/ui_settings.h":3,
          "platformio.ini":3,"sim/main_sim.cpp":1,"sim/make_show_demo.py":1,
          "src/clock.cpp":2,"src/main.cpp":63,"src/ota_wifi.cpp":2,
          "src/pet.cpp":4,"src/status_light.cpp":1,"src/ui_clear.cpp":2,
          "src/ui_settings.cpp":27,"tools/flash_known.py":1}
paths = set(git("diff","--name-only","--diff-filter=U").splitlines())
assert paths == set(counts), (paths-set(counts),set(counts)-paths)
pat = re.compile(r"^<<<<<<< [^\n]*\n(.*?)^=======\n(.*?)^>>>>>>> [^\n]*\n", re.M|re.S)
for path,n in counts.items():
    p=Path(path)
    s=p.read_text()
    matches=list(pat.finditer(s))
    assert len(matches)==n,(path,len(matches),n)
    # Keep fork documentation and the proven HTTPS OTA stack on this first
    # port. The upstream UI/clock/pet APIs must move together.
    if path in ("README.md","src/ota_wifi.cpp"):
        p.write_text(old(path))
        continue
    index=0
    def resolve(m):
        global index
        index+=1
        a,b=m.groups()
        if path=="src/main.cpp":
            if index==9:
                # CYD40's existing 30ms/two-sample press/release gate,
                # other boards retain the complete new upstream behavior.
                assert "s_downSamples" in a and "sampleTouchRaw" in b
                assert a.endswith("#else\n    if (!readTouchRaw(a, b)) return tp;\n")
                return a.rsplit("#else\n",1)[0]+"#else\n"+b+"#endif\n"
            if index==10:
                assert "s_lastPoint" in a and "s_held" in b
                return a+b.replace("#if defined(TOUCH_ON_DISPLAY_BUS)", "#elif defined(TOUCH_ON_DISPLAY_BUS)",1)
            if index==23:
                assert "pinMode" not in b and "!defined(WS_C5_35)" in b
                return b.rstrip("\n")+" && !defined(CYD40)\n"
        if path=="src/ui_settings.cpp":
            if index==8:
                assert "defined(CYD40)" in a and "defined(WS_C5_35)" in b
                return b.rstrip("\n")+" || defined(CYD40)\n"
            if index==9:
                assert "SettingsRow::UPDATE_CHECK" in a and "SettingsRow::UPDATE_CHECK" in b
                return b.replace("SettingsRow::DIAGNOSTICS, SettingsRow::UPDATE_FIRMWARE, SettingsRow::UPDATE_CHECK,",
                    "SettingsRow::DIAGNOSTICS, SettingsRow::UPDATE_FIRMWARE,\n#if !defined(CYD40)\n    SettingsRow::UPDATE_CHECK,\n#endif")
        return b
    p.write_text(pat.sub(resolve,s))
    assert index==n,(path,index)
# Preserve fork-owned board, updater, calibration helpers and physical flash
# layout byte-for-byte. No signing secret is exposed to the candidate build.
protected=["include/cyd40_user_setup.h","include/board_audio.h","src/board_audio.cpp",
           "include/ota_pubkey.h","src/ota_wifi.cpp","include/ota_wifi.h",
           "src/ota_core.cpp","include/ota_core.h","tools/sign_firmware.py",
           "src/touch_cal.cpp","partitions_ota.csv","webflasher/index.html",
           "CYD40_WIFI_OTA.md","HOSYOND_CYD40.md"]
for path in protected:
    Path(path).write_text(old(path))
# Preserve the exact two environment definitions, not older upstream defaults.
p=Path("platformio.ini")
s=p.read_text()
def envblock(t,name):
    m=re.search(r"(?m)^\[env:"+re.escape(name)+r"\]\n.*?(?=^\[|\Z)",t,re.S)
    assert m,name
    # Include all active flags; trailing comment banners are not settings.
    return m
for name in ("cyd40","cyd40-fast"):
    a=envblock(old("platformio.ini"),name)
    b=envblock(s,name)
    s=s[:b.start()]+a.group()+s[b.end():]
p.write_text(s)
# Remove duplicate picker declaration only if the upstream declaration exists.
p=Path("src/main.cpp")
s=p.read_text()
if s.count("static bool s_scanPickerOpen = false;")>1:
    s=s.replace("static bool s_scanPickerOpen = false;\n","",1)
# Check the exact raw-read branch, because CYD35R is now the upstream flag.
# Preserve the separate calibration namespace and raw threshold for CYD40.
start=s.index("static bool readTouchRaw(int16_t& a, int16_t& b) {")
end=s.index("\n}",start)
raw=s[start:end]
if "#if defined(CYD40)" not in raw:
    anchor="    if (usingCapTouch) return rawReadCap(a, b);\n"
    assert anchor in raw
    raw=raw.replace(anchor,anchor+"#if defined(CYD40)\n    return rawReadResistive(a, b);\n#elif defined(TOUCH_ON_DISPLAY_BUS) || defined(CYD35R)\n    return rawReadFiltered(a, b);\n#else\n    return rawReadResistive(a, b);\n#endif\n",1)
    # If the old non-CYD40 dispatch is also present, stop rather than duplicate.
    raise RuntimeError("Review raw touch dispatch before proceeding")
# CYD40 must not use the generic stricter coordinate-agreement filter.
assert "return rawReadResistive(a, b);" in raw
p.write_text(s)
for path in counts:
    assert not re.search(r"^(<<<<<<< |=======\n|>>>>>>> )",Path(path).read_text(),re.M),path
for path in protected:
    assert Path(path).read_text()==old(path),path
# Preserve the original CYD40 features as explicit regression contracts.
required={
 "src/main.cpp":["cyd40touch","getTouchRawZ() < 350","s_downSamples < 2","sampleAt - s_firstDown < 30","sampleAt - s_firstUp >= 30","BoardAudio::begin()","BoardAudio::testBeep()","BoardAudio::toneStop()","boardBatteryChargingEstimated","OtaWifi::taskActive()","CYD40: no Wi-Fi"],
 "src/ui_clear.cpp":["boardBatteryChargingEstimated","CYD40 quick sound toggle"],
 "src/ui_settings.cpp":["SettingsRow::SOUND_ALERTS","SettingsRow::SOUND_VOLUME","#if !defined(CYD40)"],
 "src/settings.cpp":["defined(CYD40)","soundAlerts","soundVolume"],
 "src/ota_wifi.cpp":["https://mjwgeek.github.io/SquachWatch-CYD-4.0/"],
 "include/ota_pubkey.h":["#define OTA_PUBKEY_IS_TEST 0"],
 "platformio.ini":["[env:cyd40]","[env:cyd40-fast]","-DCYD40=1","-DSERIAL_BAUD=115200","-DSPI_FREQUENCY=80000000"],
}
for path,strings in required.items():
    t=Path(path).read_text()
    for x in strings:
        assert x in t,(path,x)
print("Resolved pinned conflict set; CYD40 source checks passed.")

# LCDWiki ES3C40P 4.0-inch ESP32-S3 IPS (development build)

This separate build target is for the **LCDWiki ES3C40P**, *not* the original
Hosyond E32R40T ESP32-32E 4.0-inch with resistive touch. Do not interchange
firmware files.

Source: https://www.lcdwiki.com/4.0inch_ESP32-S3_Display

## Hardware

- MCU ESP32-S3 N16R8 (16 MB flash, 8 MB OPI PSRAM)
- IPS 320x480 ST7796S, SPI pins CS10 DC46 CLK12 MOSI11 MISO13, BL45
- FT6336U capacitive I2C touch SDA16 SCL15 RESET18 (INT17)
- SDMMC 4-bit: CLK38 CMD40 D0/1/2/3 = 39/41/48/47
- WS2812 RGB status LED: GPIO42
- Battery ADC: GPIO9
- Audio: ES8311 codec with I2S interface, amplifier enable GPIO1 active low.
  **Audio is not yet wired up in this first port.**
- Native ESP32-S3 USB for firmware flashing.

## Build

`pio run -e lcdwiki-es3c40p`

This environment reuses the existing Freenove S3 peripheral paths because
their wiring matches, but selects a distinct ST7796S driver and 320x480
display setup. 40 MHz SPI is the conservative initial value.

**Experimental:** compilation only establishes that a binary can be built.
Display image/rotation, touch mapping, SD, battery reading and audio must be
checked on physical LCDWiki hardware before declaring support complete.
Do not add to the public web flasher until a tester confirms it boots.

The existing Hosyond `cyd40` and `cyd40-fast` targets are unchanged.

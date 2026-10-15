// LCDWiki ES3C40P: 4.0-inch IPS ST7796S 320x480 on ESP32-S3 N16R8.
// Manufacturer pinout: https://www.lcdwiki.com/4.0inch_ESP32-S3_Display
// Capacitive touch FT6336U is on I2C SDA=16 SCL=15 RST=18 (INT=17).
// Native USB, 16MB flash, 8MB OPI PSRAM. SD_MMC uses 38/40/39/41/48/47.
// GPIO45 is the backlight. GPIO46 is TFT DC on this board.
// The hardware shares the Freenove ESP32-S3 2.8-inch peripheral pinout,
// but NOT the panel controller or dimensions. See [env:lcdwiki-es3c40p].
#pragma once
#define USER_SETUP_INFO "SquachWatch / LCDWiki ES3C40P 4.0 IPS / ST7796S"
#define ST7796_DRIVER
#define TFT_WIDTH  320
#define TFT_HEIGHT 480

#define USE_HSPI_PORT
#define TFT_MISO 13
#define TFT_MOSI 11
#define TFT_SCLK 12
#define TFT_CS   10
#define TFT_DC   46
#define TFT_RST  -1
#define TFT_BL   45
#define TFT_BACKLIGHT_ON HIGH

#define LOAD_GLCD
#define LOAD_FONT2
#define LOAD_FONT4
#define SMOOTH_FONT

// Conservative bring-up speed; overclock only after real-device testing.
#ifndef SPI_FREQUENCY
#define SPI_FREQUENCY 40000000
#endif
#define SPI_READ_FREQUENCY 20000000
// Display rotation, inversion and RGB ordering are handled in main.cpp.
#define TFT_RGB_ORDER TFT_BGR

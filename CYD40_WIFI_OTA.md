# Wi-Fi OTA updates for the Hosyond CYD40 fork

This fork updates over Wi-Fi from **https://mjwgeek.github.io/SquachWatch-CYD-4.0/**, not squachwatch.com.
Supported images: `cyd40` and `cyd40-fast`, signed separately. The OTA screen keeps upstream's signature and rollback verification. The GitHub Pages publishing workflow gives each successful release a three-component `2.0.<run_number>` version.

## Required one-time signing setup

A unique ECDSA P-256 key pair has been generated for this fork. The **public key only** lives in `include/ota_pubkey.h`. Keep the private key secure and never commit it.
Go to repository **Settings → Secrets and variables → Actions → New repository secret**, set the name **OTA_SIGNING_KEY**, and paste the *entire contents* of the private PEM file including BEGIN/END lines. Then rerun **Publish Hosyond Chrome Flasher**, or push a new commit to master.

If the secret is missing, the Chrome USB flasher still deploys, but OTA files are not published. If a signature fails, the firmware refuses the update.

**Important:** The new firmware embeds this fork's public key. An existing CYD40 that still has the previous public key must receive this update **once via USB** before it will trust this fork's future Wi-Fi releases.

## Files published by Pages
- `manifest-cyd40.json`, `cyd40-firmware.bin`, `cyd40-firmware.sig`
- `manifest-cyd40-fast.json`, `cyd40-fast-firmware.bin`, `cyd40-fast-firmware.sig`

Do not change the environment names in the signing workflow without updating firmware identity handling. OTA updates only replace the app partition; they do not replace the bootloader or partition table. Never use OTA to migrate partition layouts. Wi-Fi TLS support consumes more memory than the old plain-HTTP updater and requires hardware testing.

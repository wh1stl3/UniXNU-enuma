# Firmware log capture (ramoops)

How the `uefi-enuma` firmware log reaches the host on enuma, and how to read it back.

## Channel design

- The firmware writes its DEBUG output into the stock kernel's **ramoops console zone** via
  `Platforms/Xiaomi/enumaPkg/Library/RamoopsLogLib` (`RamoopsLogLib.c`), mapped by the
  `MemoryMapLib.c` `RAMOOPS` row.
- **Address / size**: `0xB0000000`, 4 MiB total. The stock Android kernel reserves
  `ramoops_memreserve=4M` here (measured via `/sys/module/ramoops/parameters`): console 2 MiB +
  pmsg 2 MiB, no ECC. The console zone carries a `DBGC` header written by the log library.
- **Warm reset survives**: SEC configures the PON reset type to *warm* + *bootloader* reason
  before DXE, so an `ASSERT` or a watchdog reset hot-restarts the device into fastboot with RAM
  preserved. A **hard reset loses the log** (the console zone is DRAM).

## Read-back flow

Replace `<enuma>` with the device's fastboot serial (never commit the real serial).

```sh
# 1. Device is sitting in fastboot after the firmware warm-reset.
fastboot -s <enuma> continue        # resume into Android WITHOUT resetting (keeps RAM)

# 2. Once Android is up, copy the console log out (needs root):
adb -s <enuma> shell su -c 'cp /sys/fs/pstore/console-ramoops-0 /data/local/tmp/ramoops'
adb -s <enuma> pull /data/local/tmp/ramoops console-ramoops-0.txt
adb -s <enuma> shell su -c 'rm /data/local/tmp/ramoops'
```

## Interpreting the log

- **Reached the menu**: look for `[Bds]Booting UniXNU` and the menu renderer output. If the screen
  also showed the menu and the keys work, the run reached bring-up stage 2.
- **Stage 3 (payload) reached**: look for `UNIXNURAMDISK: device tree at …` and
  `UNIXNURAMDISK: initrd block device … Success` followed by `[Bds]Booting UniXNU` and the FAT
  payload mount. The menu default item then counts down 3 s, calls DarwinBoot, and a placeholder
  kernel shows `Load Error` (expected until a real kernel is built).
- **ASSERT / crash**: look for `ASSERT [<module>] <file>(<line>)` followed by the warm-restart
  marker (the SEC PON line at the top of the next capture shows `warm`).
- **Hang**: the last line is the driver whose entry hung (for example the vendor `DisplayDxe`).
  A hang ends in a watchdog warm reset, so the log survives and the last line is the hang point.
- **Early abort**: if the log is short and stops at an `AllocatePoolPages` failure or a missing
  Arch protocol, the DXE heap was exhausted (see the DXE Heap 2 fix in `MemoryMapLib.c`).

## Known limitations

- No UART; DEBUG output only reaches the framebuffer (on screen) and the ramoops console zone.
- The log survives **warm** resets only; a hard reset or power-off clears it.
- Reading the log requires root on Android (`su -c`) and a device that still boots Android.
- The base-repo `AdvancedLogDxe.c` exit key accepts only CR/LF/ESC, so the power key
  (`SCAN_SUSPEND`) cannot exit the Tools > Advanced Logger page (base repo is read-only).

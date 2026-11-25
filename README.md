# PortProton on Portal (ARM64)

**Independent experimental compatibility project — not an official PortProton or Portal release.**

[Русская версия](README-RU.md)

This project documents a working way to use the classic PortProton GUI in the rootless Debian desktop provided by [Portal](https://github.com/Retrorerr/Portal) on Android. It combines an ARM64 build of PortProton's modified YAD, Portal's Box64 build, and a small adaptation of the PortProton launch scripts. Steam is not required.

## Tested environment

Initial proof of concept: 25 November 2026, OnePlus Pad 3, Snapdragon 8 Elite (Oryon / Adreno 830v1), Portal Debian 13 / KDE Plasma 6, ARM64. PortProton 1.7.5, scripts 2481 (STABLE), PROTON_LG_10-28 (Wine 10.0 Staging), modified YAD 14.0, Portal Box64 0.3.4 (build dated 22 November 2026). The original dependency hashes and YAD commit have not yet been recorded.

| Test | Result |
| --- | --- |
| Native PortProton YAD GUI | Passed |
| Winecfg and DEFAULT prefix management | Passed |
| Launch Windows EXE through PortProton | Passed, reported by tester |
| 32-bit Windows Ren'Py game (Witch Soup), direct Wine/Box64 | Passed; audio and saves also tested |
| DXVK / VKD3D, hardware acceleration | Not independently verified |
| Clean install, automatic updates, other devices, demanding games | Not verified |

This is an early proof of concept, not a general-purpose ARM64 distribution or a production-ready installer. The Direct3D path produced missing VKD3D DLL errors in the direct Wine test; the game still rendered. Its actual renderer was not established.

## How it works

- PortProton's special YAD fork is compiled natively for ARM64 (ordinary system YAD is not an equivalent replacement). Box64 could start a basic x86-64 YAD dialog but not its form/notebook GUI reliably.
- Box64 runs Proton LG's x86-64 `wine64` and `wineserver`. Wine's WoW64 mode was able to launch the tested 32-bit Windows game; no Box86 was required for that test.
- A small ARM64 branch bypasses the x86 pressure-vessel runtime and its portable libraries. The wrappers clear the inherited library search path and call the original Wine binaries without replacing them.
- Mono and Gecko are disabled in the Wine wrapper for this proof of concept. Applications requiring them are not covered.

## Try it

Read the [manual setup and rollback guide](docs/setup.md) first. It records the successful manual procedure; the supplied patch utility is a new packaging of the tested changes and has not been run on a clean Portal installation. It is intended for the classic PortProton scripts, not PortProtonQt.

The upstream software is downloaded directly from its authors, not redistributed here. Do not install an amd64 Debian package directly on the ARM64 system; the guide extracts its launcher instead.

Please report integration-specific issues here with a minimal, redacted log, versions and device information. Avoid sending the full environment dump: it may contain local paths, credentials or session tokens. Upstream bugs should be reported to the appropriate upstream only after reproducing them outside this adaptation where possible.

## Credits and thanks

This experiment is made possible by the work of the following authors and communities:

- [Mikhail Tergoev (Castro-Fidel) and the Linux Gaming / PortProton team](https://github.com/Castro-Fidel/PortWINE) — PortProton and its launch scripts; also [DEB packaging](https://github.com/Castro-Fidel/PortProton_dpkg), [YAD fork](https://github.com/Castro-Fidel/yad_portproton) and [Wine LG builds](https://github.com/Castro-Fidel/wine_builds).
- [Retrorerr and Portal contributors](https://github.com/Retrorerr/Portal), and the Local Desktop upstream community — the Android-hosted desktop and Portal-specific integration, including the Box64 build.
- [ptitSeb and Box64 contributors](https://github.com/ptitSeb/box64) — x86-64 translation on ARM64.
- [YAD](https://github.com/v1cont/yad) developers and contributors — the dialog toolkit.
- [Wine](https://www.winehq.org/), [Wine Staging](https://github.com/wine-staging/wine-staging), [Valve Proton](https://github.com/ValveSoftware/Proton) and [GE-Proton](https://github.com/GloriousEggroll/proton-ge-custom) developers — Windows compatibility and downstream improvements.
- [DXVK](https://github.com/doitsujin/dxvk), [VKD3D-Proton](https://github.com/HansKristian-Work/vkd3d-proton), Mesa and other upstream contributors whose work is used by PortProton and Portal.

Thank you for making these projects open and for the years of work behind them. This repository claims only the independent adaptation and documentation, not authorship of any upstream project. The names are used descriptively; no affiliation or endorsement is implied.

## License

The original compatibility scripts and documentation in this repository are provided under the [MIT License](LICENSE). The upstream projects retain their own licenses and copyright notices. See [third-party notices](THIRD_PARTY.md). No upstream binaries, game files or complete upstream source trees are included.

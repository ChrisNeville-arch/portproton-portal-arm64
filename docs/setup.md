# Manual setup (experimental)

These steps reconstruct the successful manual experiment. The historical upstream branches and asset URLs are recorded below, but are mutable; inspect sources before running and record the exact commit and SHA-256 for your own installation. The complete procedure has not been tested on a second clean device. Commands assume Bash, the standard Portal desktop user and a home directory containing no conflicting installation. Stop if an expected file is missing or an unexpected error occurs. Back up existing prefixes and saves before changing them.

## 1. Extract the official PortProton launcher

In Portal's Debian environment:

```bash
sudo apt install curl git python3 yad file build-essential autoconf automake intltool gettext pkg-config libgtk-3-dev vulkan-tools pciutils
mkdir -p ~/portproton-test ~/.local/bin
cd ~/portproton-test
curl -fL https://github.com/Castro-Fidel/PortProton_dpkg/releases/download/portproton_amd64/portproton_amd64.deb -o portproton_amd64.deb
sha256sum portproton_amd64.deb
dpkg-deb -x portproton_amd64.deb extracted
bash ~/portproton-test/extracted/usr/bin/portproton
```

The last command downloads upstream scripts and runtime files (the initial test downloaded about 1.6 GB). On ARM64, some bundled x86-64 GUI helpers will fail with `Exec format error`; this happened in the original experiment. The launcher nevertheless populated `~/PortProton/data/scripts` and `~/PortProton/data/themes/gui`. Verify these directories exist before continuing. Do not install the amd64 package into the system package database. If the initial launcher no longer behaves as described, stop rather than guessing.

## 2. Install the Portal-specific Box64

Original upstream location used in the test:

```bash
curl -fL https://raw.githubusercontent.com/Retrorerr/Portal/main/assets/guest-arm64/portal-box64 -o ~/.local/bin/box64
chmod +x ~/.local/bin/box64
file ~/.local/bin/box64
sha256sum ~/.local/bin/box64
~/.local/bin/box64 --version
```

This URL points to a mutable branch. The tested version was 0.3.4, build dated 22 November 2026. Do not replace an existing working Box64 without backing it up. Portal's [build script](https://github.com/Retrorerr/Portal/blob/main/scripts/build-box64.sh) documents its custom build. No Box64 binary is included in this repository.

## 3. Build PortProton's modified YAD natively

```bash
cd ~/portproton-test
git clone -b PortProton --depth 1 https://github.com/Castro-Fidel/yad_portproton.git
cd yad_portproton
git rev-parse HEAD
autoreconf -ivf && intltoolize
./configure --enable-standalone --disable-html --disable-spell --disable-sourceview
make -j4
file src/yad
src/yad --version
GDK_BACKEND=x11 src/yad --form --field='Test:TXT' 'Hello'
```

The resulting ELF must be ARM64; the tested version was YAD 14.0. The form should return the entered value after clicking OK. Preserve the original executable before replacing it:

```bash
cd ~/PortProton/data/themes/gui
# On a fresh installation only; do not overwrite an existing backup.
if [[ ! -e yad_gui_pp.x86_64 ]]; then
    cp -a yad_gui_pp yad_gui_pp.x86_64
fi
install -m 755 ~/portproton-test/yad_portproton/src/yad yad_gui_pp
GDK_BACKEND=x11 bash ~/PortProton/data/scripts/start.sh
```

The GUI should open. Select PROTON_LG_10-28 (the tested build). In the original experiment, opening Prefix Manager downloaded it. Prefix management will fail before the patch because Wine and pressure-vessel are x86 binaries. Verify that `~/PortProton/data/dist/PROTON_LG_10-28/bin/wine64` and `wineserver` exist. Do not assume the resulting prefix has been initialized successfully.

## 4. Optional independent Wine smoke test

Use a separate prefix, never the existing PortProton DEFAULT for this test:

```bash
export PATH="$HOME/.local/bin:$PATH"
cd ~/PortProton/data/dist/PROTON_LG_10-28/bin
~/.local/bin/box64 ./wine64 --version
WINEPREFIX="$HOME/.wine-box64-test" WINEARCH=win64 \
  WINEDLLOVERRIDES='mscoree,mshtml=' ~/.local/bin/box64 ./wine64 wineboot --init
WINEPREFIX="$HOME/.wine-box64-test" \
  WINEDLLOVERRIDES='mscoree,mshtml=' ~/.local/bin/box64 ./wine64 winecfg
```

The original wineboot attempt did not disable Mono/Gecko and encountered an illegal instruction during Mono installation. The command above includes the workaround used for subsequent successful tests, but this exact clean-prefix sequence has not been verified separately. Winecfg should display a window. Wine service, seccomp and Portal preload warnings were observed; they did not block the tested game. Do not treat a working Winecfg as proof that all applications work.

## 5. Apply the ARM64 integration

From the root of this compatibility repository, with PortProton and Wine applications closed:

```bash
install -m 755 wrappers/pp-wine wrappers/pp-wineserver ~/.local/bin/
python3 apply_patch.py
GDK_BACKEND=x11 bash ~/PortProton/data/scripts/start.sh
```

The patch utility adds the two tested ARM64 branches to `functions_helper`, saves a backup and checks Bash syntax. It uses exact anchors and refuses unexpected or partially patched layouts. It has only been tested against a minimal synthetic script, not a clean Portal installation. It does not patch upstream binaries or download software. Recheck the patch after any PortProton update; updates may also overwrite the native YAD.

Open Prefix Manager, then launch a known test EXE through PortProton. Audio, saving and Direct3D acceleration should be tested independently. The wrapper disables Mono/Gecko and clears `LD_LIBRARY_PATH`; those are deliberate limitations of this experiment. ESYNC was disabled automatically due to the open-file limit. MangoHud, vkBasalt, gamescope, auxiliary x86 helpers, prefix backup/restore and other Wine builds are not covered by this test.

## Rollback

Stop PortProton and Wine first. If the upstream scripts have not been updated since the patch, restore `~/PortProton/data/scripts/functions_helper.portal-arm64.original` to `functions_helper` and `~/PortProton/data/themes/gui/yad_gui_pp.x86_64` to `yad_gui_pp`. Remove only the two compatibility wrappers installed by this guide if they are no longer in use. Do not delete your prefixes, downloaded games or saves. If PortProton has updated since the backup, use the corresponding unmodified upstream version instead of restoring a stale file. This rollback restores the original x86-64 behavior; it does not make stock PortProton ARM64-compatible.

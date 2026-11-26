# ORCHID Private Symbol Keyboard

This module adds an Android Input Method Service backed by the parserless ORCHID symbol registry.

## Build and current status
- The ORCHID Android debug APK was successfully built by GitHub Actions for commit `00f8a727640f986908b33b4bd6f982b73cfb5b00`.
- The workflow ran unit tests, assembled the debug APK, verified the APK file, and uploaded the artifact.
- A successful CI build does not establish physical-device installation or runtime behavior. Those checks remain device-side.

## Features
- Offline symbol keyboard with the 12 Chronoglyph-01 symbols.
- Local private symbols stored in app-private SharedPreferences.
- Typed expression composition by canonical symbol IDs; no tokenizer or parser.
- Explicit JSON symbol-pack import/export through `OrchidKeyboardApi`.
- Android Sharesheet sharing is user initiated.
- The IME inserts a glyph only after the user taps its key.
- Manager shortcuts open Android's input-method settings and keyboard picker.
- Imported packs are bounded to 256 KB and 500 records; imported IDs cannot overwrite canonical Chronoglyph IDs.

## Enable on Android
1. Install the ERIA/ORCHID APK.
2. Open the app and enter **ORCHID • Private Symbols & Keyboard**.
3. Tap **Enable ORCHID keyboard in Android settings** and enable **ORCHID Symbol Keyboard**.
4. Return to the manager and tap **Select ORCHID as current keyboard**.
5. Select ORCHID in the Android keyboard picker.
6. Open any text field and tap a symbol to insert it.

On Samsung One UI, the system settings route may be labelled **Settings → General management → Keyboard list and default**. Android may show different wording by version.

## Private and shareable
Private symbols stay in the app's private local registry by default. Export creates an `ORCHID_SYMBOL_PACK_V1` JSON package; sharing is explicit and user initiated. Import validates the package format and merges records into the local private registry. A shared package is a copy, not live synchronization. The format currently has no cryptographic signature or end-to-end encryption, so do not treat it as confidential or authenticated.

## API
- `symbols()`
- `compose(symbolIds)`
- `addPrivateSymbol(name, glyph, meaning)`
- `importPrivatePack(json)`
- `createShareIntent()`

## Scope and outstanding validation
- This is an Android IME and launcher flow, not an Android operating-system image, desktop keyboard, or web keyboard.
- The current keyboard is a scrollable symbol grid; no predictive text or contextual keystroke collection.
- Private symbols are app-local; the IME reads the same local registry.
- Persistent local storage is implemented. EPHEMERAL, CACHE, OFFLINE overlay, and DISTRIBUTED signed-sync profiles remain separate planned runtime modes.
- Locale-specific RTL, shaping, combining-mark, and accessibility tests remain outstanding.
- Physical installation, insertion, IME restart persistence, private-symbol creation, and export/import round-trip must be verified on-device.

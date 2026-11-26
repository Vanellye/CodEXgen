# ORCHID Private Symbol Keyboard

This module adds an Android Input Method Service backed by the parserless ORCHID symbol registry.

## Features
- Offline symbol keyboard with the 12 Chronoglyph-01 symbols.
- Local private symbols stored in app-private SharedPreferences.
- Typed expression composition by canonical symbol IDs; no tokenizer or parser.
- Explicit JSON symbol-pack import/export through `OrchidKeyboardApi`.
- Share intent uses the Android Sharesheet only when the host app explicitly launches it.
- The IME inserts a glyph only after the user taps its key.

## Enable on Android
1. Install the ERIA debug/release APK.
2. Open Android Settings → System → Keyboard → On-screen keyboard (wording varies by device).
3. Enable **ORCHID Symbol Keyboard**.
4. Select it from the keyboard switcher while entering text.

Android may label these settings differently by manufacturer/version.

## Private and shareable
Private symbols stay in the app's private local registry by default. Export creates an `ORCHID_SYMBOL_PACK_V1` JSON package; sharing is explicit and user initiated. Import validates the package format and merges records into the local private registry. A shared package is a copy, not live synchronization. The format currently has no cryptographic signature or end-to-end encryption, so do not treat it as confidential or authenticated.

## API
- `symbols()`
- `compose(symbolIds)`
- `addPrivateSymbol(name, glyph, meaning)`
- `importPrivatePack(json)`
- `createShareIntent()`

## Current limitations
- This is an Android IME implementation, not a desktop or web keyboard.
- The current keyboard is a simple scrollable symbol grid; no predictive text or contextual keystroke collection.
- Private symbols are app-local; the IME reads the same local registry.
- The repository change has not yet been built into an APK or tested on a physical device.

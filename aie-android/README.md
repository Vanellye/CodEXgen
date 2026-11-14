# Æị Android APK (separate native package)

This is a separate Android Studio/Gradle project. It does not depend on the Termux standalone web server.

## Build
From the repository root, with Java 17 and Android SDK installed:
```bash
./gradlew -p aie-android assembleDebug
```
APK output:
`aie-android/app/build/outputs/apk/debug/app-debug.apk`

Install with:
```bash
adb install -r aie-android/app/build/outputs/apk/debug/app-debug.apk
```
On a phone without ADB, transfer the APK to the device and install it after allowing installation from that source.

## Connect to ERIA
On first launch the app uses `http://127.0.0.1:8778`. Change the API origin in the top field and tap Connect if your existing ERIA server uses another local address/port. The Android app calls the API through a native bridge, so the bundled page does not require permissive browser CORS settings.

The app allows only these API routes:
- `GET /api/platform/status`
- `POST /api/scan`
- `POST /api/decode`

The native bridge does not expose arbitrary URL fetching or filesystem/database access. No SQLite file is opened by the APK.

## Security and current limits
- Cleartext HTTP is enabled to support a local Termux HTTP server. Use only a trusted local network; prefer HTTPS if the server is later configured for it.
- The API origin is stored in app-private preferences.
- The app does not launch, install, or manage the Termux ERIA server.
- Pantheon is intentionally not connected until its native bridge is tested and a real ERIA adapter exists.
- A successful Gradle build proves APK compilation only; it does not prove the live API, database identity, scan behavior, or Pantheon readiness.

# ERIA Android client

Android Studio client for the existing ERIA HTML conversation server.

- Application ID: `com.vanellye.eria`
- Minimum SDK: 24
- Target SDK: 35
- Compile SDK: 35
- Kotlin / Java target: 17

## Server connection

The app opens `http://111.1.1.1:1111/`.

The Android WebView enables JavaScript and DOM storage, disables local file access, and restricts top-level navigation to HTTP on host `111.1.1.1`, port `1111`. No separate chat API is assumed; the HTML application retains its existing conversation protocol.

The manifest permits cleartext traffic because the supplied URL uses HTTP. For use beyond a trusted network, deploy HTTPS and disable cleartext traffic.

## Build

Open the repository in Android Studio, sync Gradle, and run the `app` configuration on an Android 7.0+ device.

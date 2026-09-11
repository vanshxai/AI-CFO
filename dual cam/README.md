# Dual Cam

A small Android app that records front and rear camera video **at the same time**.

## What it does

- Live dual preview: rear camera fullscreen, front camera in a small picture-in-picture card (top-right).
- One button starts/stops recording — saves two separate MP4 files (one per camera) to `Movies/DualCam/` via MediaStore.
- Swap button — swap which camera is the big view vs. the small overlay.
- Torch (flashlight) toggle for the rear camera.
- Runtime camera/microphone permission handling.
- Graceful "not supported" screen if the device's hardware can't stream both cameras concurrently.

Not included (by design, to keep this small): merging the two videos into a single side-by-side file, filters/effects, photo capture, landscape support. These would all be reasonable follow-ups.

## How it works

Built with [CameraX](https://developer.android.com/media/camera/camerax) and its `ConcurrentCamera` API (`ProcessCameraProvider.availableConcurrentCameraInfos` + `bindToLifecycle(List<SingleCameraConfig>)`), which is the officially supported way to run two cameras at once. Support is hardware-dependent — most phones from the last few years (Pixel, Samsung, etc.) support it; some budget/older devices don't, which is why the app checks and shows a fallback screen instead of crashing.

- `MainActivity.kt` — all the logic: permission flow, binding both cameras, starting/stopping the two simultaneous recordings, swapping previews, torch control.
- `activity_main.xml` — the UI: two `PreviewView`s, record FAB, swap/torch buttons, permission and "unsupported" overlays.

## Requirements

- Android Studio (Koala/2024.1 or newer recommended).
- A physical Android device with a front + rear camera that supports concurrent camera streaming (Android 11+ devices are the most likely to support it — the app will tell you at launch if yours doesn't). Emulators do not support concurrent camera.
- minSdk 29 (Android 10), compileSdk/targetSdk 34.

## Build & run

```
cd "dual cam"
./gradlew assembleDebug
```

Or just open the `dual cam` folder in Android Studio — it will sync automatically — and hit Run on a connected device.

> Note: this project was built in a sandboxed environment without network access to Google's Maven repository or an installed Android SDK, so the Gradle wrapper was generated and verified locally, but a full `assembleDebug` against the real Android/CameraX dependencies has **not** been run here. Open it in Android Studio to sync dependencies and do a real build/run — that's the standard next step for any new Android project like this one.

## Project layout

```
dual cam/
├── app/
│   ├── build.gradle.kts
│   └── src/main/
│       ├── AndroidManifest.xml
│       ├── java/com/dualcam/app/MainActivity.kt
│       └── res/           (layout, drawables, strings, theme)
├── build.gradle.kts
├── settings.gradle.kts
├── gradle.properties
└── gradlew / gradlew.bat
```

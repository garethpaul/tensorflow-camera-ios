# Toolchain and Model Assets

## Scope

This repository preserves a historical Objective-C++ TensorFlow camera sample.
The exact original TensorFlow commit is not recorded, so a clean checkout is not
a self-contained or reproducible iOS link. This guide separates facts preserved
in the repository from a reviewed reconstruction baseline.

## Preserved Build Metadata

- `app/public/version.h` identifies the vendored source as TensorFlow 0.12.head.
- `app/tensorflow_camera.xcodeproj/project.pbxproj` records
  `LastUpgradeCheck = 0820`, which is Xcode 8.2-era project metadata.
- The target declares iOS 9.2, GNU++11 through `gnu++0x`, libc++ through the
  compiler default, and bitcode disabled.
- The project expects `libtensorflow-core.a`, `libprotobuf.a`, and
  `libprotobuf-lite.a`, plus generated TensorFlow and protobuf headers. Those
  generated files are intentionally not checked in.
- The project still contains historical machine-local search paths. Rebind the
  header, library, and `-force_load` paths to the selected TensorFlow checkout;
  do not reproduce another contributor's absolute home-directory paths.

TensorFlow's official v0.12.0 iOS instructions require Xcode 7.3 or later. The
repository metadata shows that this copy was last upgraded with Xcode 8.2-era
tooling, but neither version is installed or exercised by the portable CI gate.

## Reviewed Reconstruction Baseline

TensorFlow v0.12.0 is the closest tagged reconstruction baseline supported by
both the vendored version header and the official historical iOS instructions.
It is not asserted to be the unknown original source commit.

On a macOS host with an appropriate historical Xcode installation:

```bash
git clone --branch v0.12.0 --depth 1 \
  https://github.com/tensorflow/tensorflow.git tensorflow-v0.12.0
cd tensorflow-v0.12.0
tensorflow/contrib/makefile/build_all_ios.sh
```

The official `build_all_ios.sh` runs dependency download, iOS protobuf
compilation, and TensorFlow compilation. It should produce:

- `tensorflow/contrib/makefile/gen/lib/libtensorflow-core.a`
- `tensorflow/contrib/makefile/gen/protobuf_ios/lib/libprotobuf.a`
- `tensorflow/contrib/makefile/gen/protobuf_ios/lib/libprotobuf-lite.a`

Point the Xcode project's generated-header, library-search, and `-force_load`
settings at that checkout before attempting `scripts/run-ios-build.sh`. A
successful archive build does not by itself prove camera permissions, device
capture, model latency, or UI behavior; validate those separately on a test
device with privacy-safe scenes.

## Model Download Expectations

The graph, labels, and license in `app/data` byte-match TensorFlow's official
`inception5h.zip`. The reviewed archive URL and SHA-256 are:

```text
https://storage.googleapis.com/download.tensorflow.org/models/inception5h.zip
d13569f6a98159de37e92e9c8ec4dae8f674fbf475f69fe6199b514f756d4364
```

Recovery example:

```bash
curl --fail --location --output /tmp/inception5h.zip \
  https://storage.googleapis.com/download.tensorflow.org/models/inception5h.zip
printf '%s  %s\n' \
  d13569f6a98159de37e92e9c8ec4dae8f674fbf475f69fe6199b514f756d4364 \
  /tmp/inception5h.zip | shasum -a 256 --check
unzip -q /tmp/inception5h.zip -d /tmp/inception5h
```

Copy only the expected files after verifying the archive. `make check` pins the
installed resource digests, including the bundled Apache license. Do not replace
assets merely because a URL now serves different bytes.

The bundled `grace_hopper.jpg` is not inside `inception5h.zip`. It byte-matches
the TensorFlow v0.12.0 iOS camera example at:

```text
https://raw.githubusercontent.com/tensorflow/tensorflow/v0.12.0/tensorflow/contrib/ios_examples/camera/data/grace_hopper.jpg
```

## Verified Resource Digests

| File | SHA-256 |
| --- | --- |
| `tensorflow_inception_graph.pb` | `a39b08b826c9d5a5532ff424c03a3a11a202967544e389aca4b06c2bd8aef63f` |
| `imagenet_comp_graph_label_strings.txt` | `da2a31ecfe9f212ae8dd07379b11a74cb2d7a110eba12c5fc8c862a65b8e6606` |
| `grace_hopper.jpg` | `e1f57e98cf38076c0f9a058d74ffddf90f20453e436033784606b63c8ed2e49a` |
| `LICENSE` | `f086f362c12f3a0295ba186c8caa1d2778beb6b9a7651c499791f202c2429c0d` |

## Official Historical Sources

- [TensorFlow v0.12.0 iOS examples](https://github.com/tensorflow/tensorflow/blob/v0.12.0/tensorflow/contrib/ios_examples/README.md)
- [TensorFlow v0.12.0 Makefile build instructions](https://github.com/tensorflow/tensorflow/blob/v0.12.0/tensorflow/contrib/makefile/README.md)
- [TensorFlow v0.12.0 iOS build script](https://github.com/tensorflow/tensorflow/blob/v0.12.0/tensorflow/contrib/makefile/build_all_ios.sh)

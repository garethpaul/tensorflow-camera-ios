# Tensorflow Camera

1. Open up xcode project
2. Run on a device and point your camera at some objects

## Build Tensorflow data

```bash
mkdir -p ~/graphs
curl -o ~/graphs/inception5h.zip \
 https://storage.googleapis.com/download.tensorflow.org/models/inception5h.zip \
 && unzip ~/graphs/inception5h.zip -d ~/graphs/inception5h
cp ~/graphs/inception5h/* data/
```

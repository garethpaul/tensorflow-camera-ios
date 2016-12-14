# Tensorflow Camera

This is an iOS Camera app which displays text next to objects.

1. Build Tensorflow data

```bash
mkdir -p ~/graphs
curl -o ~/graphs/inception5h.zip \
 https://storage.googleapis.com/download.tensorflow.org/models/inception5h.zip \
 && unzip ~/graphs/inception5h.zip -d ~/graphs/inception5h
cp ~/graphs/inception5h/* data/
```

2. Open Up XCode
3. Build and Run
4. Build on Camera App

<img src="screenshot.png?raw=true" width="300px" />

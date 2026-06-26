# Model Asset Provenance

The files in this directory come from two reviewed upstream sources and do not
all share the same copyright status.

## TensorFlow Inception bundle

`tensorflow_inception_graph.pb`, `imagenet_comp_graph_label_strings.txt`, and
`LICENSE` byte-match TensorFlow's official `inception5h.zip` archive:

- URL: `https://storage.googleapis.com/download.tensorflow.org/models/inception5h.zip`
- Archive SHA-256: `d13569f6a98159de37e92e9c8ec4dae8f674fbf475f69fe6199b514f756d4364`
- License: Apache License 2.0, as included in `LICENSE`
- Copyright notice: Copyright 2015 The TensorFlow Authors

The included Apache notice applies to the graph and label bundle. It is not the
license for the sample photograph below.

## Grace Hopper sample image

`grace_hopper.jpg` byte-matches both TensorFlow v0.12.0's iOS camera example
and Wikimedia Commons `File:Grace Hopper.jpg`.

- TensorFlow source: `https://raw.githubusercontent.com/tensorflow/tensorflow/v0.12.0/tensorflow/contrib/ios_examples/camera/data/grace_hopper.jpg`
- Original work: Commodore Grace M. Hopper, USNR official portrait, January 20, 1984
- Photographer: James S. Davis, U.S. Navy
- Naval History and Heritage Command identifier: NH 96919-KN
- Commons record: `https://commons.wikimedia.org/wiki/File:Grace_Hopper.jpg`
- Copyright status: public domain in the United States as a work of the U.S. federal government
- File SHA-256: `e1f57e98cf38076c0f9a058d74ffddf90f20453e436033784606b63c8ed2e49a`

Keep this record and the pinned resource digests synchronized with any future
asset replacement. Do not infer that every model or dataset distributed by a
TensorFlow-hosted URL uses the same license.

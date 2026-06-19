#include <cstdlib>
#include <iostream>
#include <limits>

#include "frame_preprocessing.h"

namespace {

void Expect(bool condition, const char* description) {
  if (!condition) {
    std::cerr << "FAIL: " << description << "\n";
    std::exit(1);
  }
}

void ExpectOffset(const tensorflow_camera::FrameLayout& layout, size_t target_x,
                  size_t target_y, size_t target_width, size_t target_height,
                  size_t expected, const char* description) {
  size_t actual = 0;
  Expect(tensorflow_camera::SourcePixelOffset(
             layout, target_x, target_y, target_width, target_height, &actual),
         description);
  Expect(actual == expected, description);
}

}  // namespace

int main() {
  using tensorflow_camera::BuildFrameLayout;
  using tensorflow_camera::FrameLayout;
  using tensorflow_camera::PixelLayout;
  using tensorflow_camera::SampleCoordinate;
  using tensorflow_camera::SourceChannelOffset;

  FrameLayout landscape;
  Expect(BuildFrameLayout(4, 2, 20, 40, PixelLayout::kBGRA, &landscape),
         "padded landscape BGRA layout is accepted");
  Expect(landscape.crop_x == 1 && landscape.crop_y == 0 &&
             landscape.crop_size == 2,
         "landscape frames use a centered square crop");
  ExpectOffset(landscape, 0, 0, 2, 2, 4, "landscape crop starts at x=1");
  ExpectOffset(landscape, 1, 1, 2, 2, 28,
               "landscape sampling preserves padded row stride");

  FrameLayout portrait;
  Expect(BuildFrameLayout(2, 4, 8, 32, PixelLayout::kARGB, &portrait),
         "portrait ARGB layout is accepted");
  Expect(portrait.crop_x == 0 && portrait.crop_y == 1 &&
             portrait.crop_size == 2,
         "portrait frames use a centered square crop");
  ExpectOffset(portrait, 0, 0, 2, 2, 8, "portrait crop starts at y=1");
  ExpectOffset(portrait, 1, 1, 2, 2, 20,
               "portrait sampling addresses the final crop pixel");

  size_t channel = 0;
  Expect(SourceChannelOffset(PixelLayout::kBGRA, 0, &channel) && channel == 2 &&
             SourceChannelOffset(PixelLayout::kBGRA, 1, &channel) && channel == 1 &&
             SourceChannelOffset(PixelLayout::kBGRA, 2, &channel) && channel == 0,
         "BGRA input is published to TensorFlow as RGB");
  Expect(SourceChannelOffset(PixelLayout::kARGB, 0, &channel) && channel == 1 &&
             SourceChannelOffset(PixelLayout::kARGB, 1, &channel) && channel == 2 &&
             SourceChannelOffset(PixelLayout::kARGB, 2, &channel) && channel == 3,
         "ARGB input skips alpha and publishes RGB");
  Expect(!SourceChannelOffset(PixelLayout::kBGRA, 3, &channel),
         "unsupported output channels are rejected");

  FrameLayout rejected;
  Expect(!BuildFrameLayout(0, 2, 8, 16, PixelLayout::kBGRA, &rejected),
         "zero width is rejected");
  Expect(!BuildFrameLayout(3, 2, 8, 16, PixelLayout::kBGRA, &rejected),
         "short row stride is rejected");
  Expect(!BuildFrameLayout(2, 2, 8, 15, PixelLayout::kBGRA, &rejected),
         "truncated backing storage is rejected");
  Expect(!BuildFrameLayout(2, 3, std::numeric_limits<size_t>::max(),
                           std::numeric_limits<size_t>::max(),
                           PixelLayout::kBGRA, &rejected),
         "overflowing row offsets are rejected");

  size_t coordinate = 0;
  Expect(!SampleCoordinate(2, std::numeric_limits<size_t>::max(), 3,
                           &coordinate),
         "overflowing resize products are rejected");
  Expect(SampleCoordinate(223, 224, 224, &coordinate) && coordinate == 223,
         "the final ordinary resize coordinate remains in bounds");

  std::cout << "Frame preprocessing tests passed\n";
  return 0;
}

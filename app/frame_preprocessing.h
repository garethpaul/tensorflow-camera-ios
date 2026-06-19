#ifndef TENSORFLOW_CAMERA_FRAME_PREPROCESSING_H_
#define TENSORFLOW_CAMERA_FRAME_PREPROCESSING_H_

#include <cstddef>
#include <limits>

namespace tensorflow_camera {

enum class PixelLayout {
  kARGB,
  kBGRA,
};

struct FrameLayout {
  size_t width;
  size_t height;
  size_t row_bytes;
  size_t data_size;
  size_t crop_size;
  size_t crop_x;
  size_t crop_y;
  PixelLayout pixel_layout;
};

inline bool CheckedMultiply(size_t left, size_t right, size_t* result) {
  if (left != 0 && right > std::numeric_limits<size_t>::max() / left) {
    return false;
  }
  *result = left * right;
  return true;
}

inline bool CheckedAdd(size_t left, size_t right, size_t* result) {
  if (right > std::numeric_limits<size_t>::max() - left) {
    return false;
  }
  *result = left + right;
  return true;
}

inline bool BuildFrameLayout(size_t width, size_t height, size_t row_bytes,
                             size_t data_size, PixelLayout pixel_layout,
                             FrameLayout* layout) {
  const size_t channels = 4;
  if (layout == nullptr || width == 0 || height == 0 || data_size == 0 ||
      width > row_bytes / channels) {
    return false;
  }

  const size_t crop_size = width < height ? width : height;
  const size_t crop_x = (width - crop_size) / 2;
  const size_t crop_y = (height - crop_size) / 2;
  size_t final_row = 0;
  size_t final_column = 0;
  size_t final_offset = 0;
  if (!CheckedMultiply(crop_y + crop_size - 1, row_bytes, &final_row) ||
      !CheckedMultiply(crop_x + crop_size - 1, channels, &final_column) ||
      !CheckedAdd(final_row, final_column, &final_offset) ||
      !CheckedAdd(final_offset, channels - 1, &final_offset) ||
      final_offset >= data_size) {
    return false;
  }

  layout->width = width;
  layout->height = height;
  layout->row_bytes = row_bytes;
  layout->data_size = data_size;
  layout->crop_size = crop_size;
  layout->crop_x = crop_x;
  layout->crop_y = crop_y;
  layout->pixel_layout = pixel_layout;
  return true;
}

inline bool SampleCoordinate(size_t position, size_t source_extent,
                             size_t target_extent, size_t* coordinate) {
  size_t product = 0;
  if (coordinate == nullptr || target_extent == 0 || position >= target_extent ||
      !CheckedMultiply(position, source_extent, &product)) {
    return false;
  }
  *coordinate = product / target_extent;
  return *coordinate < source_extent;
}

inline bool SourcePixelOffset(const FrameLayout& layout, size_t target_x,
                              size_t target_y, size_t target_width,
                              size_t target_height, size_t* offset) {
  size_t sampled_x = 0;
  size_t sampled_y = 0;
  size_t source_x = 0;
  size_t source_y = 0;
  size_t row_offset = 0;
  size_t column_offset = 0;
  size_t source_offset = 0;
  if (offset == nullptr ||
      !SampleCoordinate(target_x, layout.crop_size, target_width, &sampled_x) ||
      !SampleCoordinate(target_y, layout.crop_size, target_height, &sampled_y) ||
      !CheckedAdd(layout.crop_x, sampled_x, &source_x) ||
      !CheckedAdd(layout.crop_y, sampled_y, &source_y) ||
      !CheckedMultiply(source_y, layout.row_bytes, &row_offset) ||
      !CheckedMultiply(source_x, static_cast<size_t>(4), &column_offset) ||
      !CheckedAdd(row_offset, column_offset, &source_offset) ||
      source_offset > layout.data_size - 4) {
    return false;
  }
  *offset = source_offset;
  return true;
}

inline bool SourceChannelOffset(PixelLayout pixel_layout, size_t output_channel,
                                size_t* source_channel) {
  if (source_channel == nullptr || output_channel >= 3) {
    return false;
  }
  if (pixel_layout == PixelLayout::kARGB) {
    *source_channel = output_channel + 1;
  } else {
    *source_channel = 2 - output_channel;
  }
  return true;
}

}  // namespace tensorflow_camera

#endif  // TENSORFLOW_CAMERA_FRAME_PREPROCESSING_H_

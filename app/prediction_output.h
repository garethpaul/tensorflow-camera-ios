#ifndef TENSORFLOW_CAMERA_PREDICTION_OUTPUT_H_
#define TENSORFLOW_CAMERA_PREDICTION_OUTPUT_H_

#include <cmath>
#include <string>
#include <vector>

#include "prediction_validation.h"

namespace tensorflow_camera {

struct LabeledPrediction {
  std::string label;
  float value;
};

inline std::vector<LabeledPrediction> SelectLabeledPredictions(
    const std::vector<float>& predictions,
    const std::vector<std::string>& labels, float threshold) {
  std::vector<LabeledPrediction> selected;
  if (!std::isfinite(threshold) || threshold < 0.0f || threshold > 1.0f) {
    return selected;
  }

  const size_t result_count =
      predictions.size() < labels.size() ? predictions.size() : labels.size();
  selected.reserve(result_count);
  for (size_t index = 0; index < result_count; index += 1) {
    const float value = predictions[index];
    if (!std::isfinite(value) || !IsValidModelPrediction(value) ||
        value <= threshold) {
      continue;
    }

    const LabeledPrediction prediction = {labels[index], value};
    selected.push_back(prediction);
  }
  return selected;
}

}  // namespace tensorflow_camera

#endif  // TENSORFLOW_CAMERA_PREDICTION_OUTPUT_H_

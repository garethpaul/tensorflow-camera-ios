#include <cstdlib>
#include <iostream>
#include <limits>
#include <string>
#include <vector>

#include "prediction_output.h"

namespace {

void Expect(bool condition, const char* description) {
  if (!condition) {
    std::cerr << "FAIL: " << description << "\n";
    std::exit(1);
  }
}

}  // namespace

int main() {
  const std::vector<std::string> labels = {"cat", "dog", "bird"};
  const std::vector<float> predictions = {
      0.9f,
      0.05f,
      0.7f,
      0.8f,
  };

  const std::vector<tensorflow_camera::LabeledPrediction> selected =
      tensorflow_camera::SelectLabeledPredictions(predictions, labels, 0.05f);
  Expect(selected.size() == 2, "only scores above the threshold are selected");
  Expect(selected[0].label == "cat" && selected[0].value == 0.9f,
         "the first selected score keeps its label and value");
  Expect(selected[1].label == "bird" && selected[1].value == 0.7f,
         "selection respects the shorter label vector");

  const std::vector<float> invalid_predictions = {
      std::numeric_limits<float>::quiet_NaN(),
      -0.1f,
      1.1f,
  };
  Expect(tensorflow_camera::SelectLabeledPredictions(
             invalid_predictions, labels, 0.05f)
             .empty(),
         "non-finite and out-of-range scores are excluded");
  Expect(tensorflow_camera::SelectLabeledPredictions(
             predictions, labels, std::numeric_limits<float>::quiet_NaN())
             .empty(),
         "non-finite thresholds fail closed");

  std::cout << "Prediction output tests passed\n";
  return 0;
}

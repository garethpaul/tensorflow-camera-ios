#include <cstdlib>
#include <iostream>
#include <limits>

#include "prediction_validation.h"

namespace {

void ExpectValidation(float value, bool expected, const char* description) {
  const bool actual = tensorflow_camera::IsValidModelPrediction(value);
  if (actual != expected) {
    std::cerr << "FAIL: " << description << "\n";
    std::exit(1);
  }
}

}  // namespace

int main() {
  ExpectValidation(0.0f, true, "zero is a valid inclusive endpoint");
  ExpectValidation(0.05f, true, "the display threshold is valid");
  ExpectValidation(0.5f, true, "a representative probability is valid");
  ExpectValidation(1.0f, true, "one is a valid inclusive endpoint");

  ExpectValidation(-0.01f, false, "negative predictions are rejected");
  ExpectValidation(1.01f, false, "predictions above one are rejected");
  ExpectValidation(std::numeric_limits<float>::max(), false,
                   "extreme finite predictions are rejected");
  ExpectValidation(std::numeric_limits<float>::infinity(), false,
                   "positive infinity is rejected");
  ExpectValidation(-std::numeric_limits<float>::infinity(), false,
                   "negative infinity is rejected");
  ExpectValidation(std::numeric_limits<float>::quiet_NaN(), false,
                   "NaN is rejected");

  std::cout << "Prediction range tests passed\n";
  return 0;
}

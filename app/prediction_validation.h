#ifndef TENSORFLOW_CAMERA_PREDICTION_VALIDATION_H_
#define TENSORFLOW_CAMERA_PREDICTION_VALIDATION_H_

namespace tensorflow_camera {

inline bool IsValidModelPrediction(float value) {
  return value >= 0.0f && value <= 1.0f;
}

}  // namespace tensorflow_camera

#endif  // TENSORFLOW_CAMERA_PREDICTION_VALIDATION_H_

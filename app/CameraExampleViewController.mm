// Copyright 2015 Google Inc. All rights reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//    http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#import <AssertMacros.h>
#import <AssetsLibrary/AssetsLibrary.h>
#import <CoreImage/CoreImage.h>
#import <ImageIO/ImageIO.h>
#import "CameraExampleViewController.h"

#include <sys/time.h>
#include <cmath>
#include <limits.h>

#include "frame_preprocessing.h"
#include "prediction_output.h"
#include "prediction_validation.h"
#include "tensorflow_utils.h"

// If you have your own model, modify this to the file name, and make sure
// you've added the file to your app resources too.
static NSString* model_file_name = @"tensorflow_inception_graph";
static NSString* model_file_type = @"pb";
// This controls whether we'll be loading a plain GraphDef proto, or a
// file created by the convert_graphdef_memmapped_format utility that wraps a
// GraphDef and parameter file that can be mapped into memory from file to
// reduce overall memory usage.
const bool model_uses_memory_mapping = false;
// If you have your own model, point this to the labels file.
static NSString* labels_file_name = @"imagenet_comp_graph_label_strings";
static NSString* labels_file_type = @"txt";
// These dimensions need to match those the model was trained with.
const int wanted_input_width = 224;
const int wanted_input_height = 224;
const int wanted_input_channels = 3;
const float input_mean = 117.0f;
const float input_std = 1.0f;
const std::string input_layer_name = "input";
const std::string output_layer_name = "softmax1";

static const NSString *AVCaptureStillImageIsCapturingStillImageContext =
    @"AVCaptureStillImageIsCapturingStillImageContext";
static char VideoDataOutputQueueKey;

@interface CameraExampleViewController (InternalMethods)
- (void)setupAVCapture;
- (void)updateCaptureRunningState;
- (void)applicationDidBecomeActive:(NSNotification *)notification;
- (void)applicationWillResignActive:(NSNotification *)notification;
- (void)drainVideoDataOutputQueue;
- (void)teardownAVCapture;
@end

@implementation CameraExampleViewController

- (void)showCaptureErrorWithTitle:(NSString *)title message:(NSString *)message {
  UIAlertView *alertView = [[UIAlertView alloc] initWithTitle:title
                                                      message:message
                                                     delegate:nil
                                            cancelButtonTitle:@"Dismiss"
                                            otherButtonTitles:nil];
  [alertView show];
  [alertView release];
}

- (void)failCameraSetupWithMessage:(NSString *)message {
  [self showCaptureErrorWithTitle:@"Camera Setup Failed" message:message];
  if (stillImageOutput) {
    [stillImageOutput removeObserver:self forKeyPath:@"capturingStillImage"];
    [stillImageOutput release];
    stillImageOutput = nil;
  }
  if (videoDataOutput) {
    [videoDataOutput setSampleBufferDelegate:nil queue:NULL];
    [videoDataOutput release];
    videoDataOutput = nil;
  }
  if (videoDataOutputQueue) {
    dispatch_release(videoDataOutputQueue);
    videoDataOutputQueue = NULL;
  }
  [session release];
  session = nil;
}

- (void)setupAVCapture {
  NSError *error = nil;

  session = [AVCaptureSession new];
  if ([[UIDevice currentDevice] userInterfaceIdiom] ==
      UIUserInterfaceIdiomPhone)
    [session setSessionPreset:AVCaptureSessionPreset640x480];
  else
    [session setSessionPreset:AVCaptureSessionPresetPhoto];

  AVCaptureDevice *device =
      [AVCaptureDevice defaultDeviceWithMediaType:AVMediaTypeVideo];
  if (!device) {
    [self showCaptureErrorWithTitle:@"Camera Unavailable"
                            message:@"No video capture device is available."];
    [session release];
    session = nil;
    return;
  }

  AVCaptureDeviceInput *deviceInput =
      [AVCaptureDeviceInput deviceInputWithDevice:device error:&error];
  if (error || !deviceInput) {
    NSString *message = error ? [error localizedDescription]
                              : @"Could not create a camera input.";
    [self showCaptureErrorWithTitle:@"Camera Setup Failed" message:message];
    [session release];
    session = nil;
    return;
  }

  isUsingFrontFacingCamera = NO;
  if ([session canAddInput:deviceInput]) {
    [session addInput:deviceInput];
  } else {
    [self showCaptureErrorWithTitle:@"Camera Setup Failed"
                            message:@"Could not add the camera input."];
    [session release];
    session = nil;
    return;
  }

  stillImageOutput = [AVCaptureStillImageOutput new];
  [stillImageOutput
      addObserver:self
       forKeyPath:@"capturingStillImage"
          options:NSKeyValueObservingOptionNew
          context:(void *)(AVCaptureStillImageIsCapturingStillImageContext)];
  if ([session canAddOutput:stillImageOutput]) {
    [session addOutput:stillImageOutput];
  } else {
    [self failCameraSetupWithMessage:@"Could not add the still image output."];
    return;
  }

  videoDataOutput = [AVCaptureVideoDataOutput new];

  NSDictionary *rgbOutputSettings = [NSDictionary
      dictionaryWithObject:[NSNumber numberWithInt:kCMPixelFormat_32BGRA]
                    forKey:(id)kCVPixelBufferPixelFormatTypeKey];
  [videoDataOutput setVideoSettings:rgbOutputSettings];
  [videoDataOutput setAlwaysDiscardsLateVideoFrames:YES];
  videoDataOutputQueue =
      dispatch_queue_create("VideoDataOutputQueue", DISPATCH_QUEUE_SERIAL);
  dispatch_queue_set_specific(videoDataOutputQueue, &VideoDataOutputQueueKey,
                              &VideoDataOutputQueueKey, NULL);
  [videoDataOutput setSampleBufferDelegate:self queue:videoDataOutputQueue];

  if ([session canAddOutput:videoDataOutput]) {
    [session addOutput:videoDataOutput];
  } else {
    [self failCameraSetupWithMessage:@"Could not add the video data output."];
    return;
  }
  AVCaptureConnection *videoConnection =
      [videoDataOutput connectionWithMediaType:AVMediaTypeVideo];
  if (!videoConnection) {
    [self failCameraSetupWithMessage:@"Could not create a video data connection."];
    return;
  }
  [videoConnection setEnabled:YES];

  previewLayer = [[AVCaptureVideoPreviewLayer alloc] initWithSession:session];
  [previewLayer setBackgroundColor:[[UIColor blackColor] CGColor]];
  [previewLayer setVideoGravity:AVLayerVideoGravityResizeAspect];
  CALayer *rootLayer = [previewView layer];
  [rootLayer setMasksToBounds:YES];
  [previewLayer setFrame:[rootLayer bounds]];
  [rootLayer addSublayer:previewLayer];
  [self updateCaptureRunningState];

}

- (void)updateCaptureRunningState {
  if (!session) {
    return;
  }
  const BOOL shouldRun =
      captureRequested && viewIsVisible && applicationIsActive;
  if (shouldRun && ![session isRunning]) {
    [session startRunning];
  } else if (!shouldRun && [session isRunning]) {
    [session stopRunning];
  }
}

- (void)applicationDidBecomeActive:(NSNotification *)notification {
  applicationIsActive = YES;
  [self updateCaptureRunningState];
}

- (void)applicationWillResignActive:(NSNotification *)notification {
  applicationIsActive = NO;
  [self updateCaptureRunningState];
}

- (void)drainVideoDataOutputQueue {
  if (!videoDataOutputQueue ||
      dispatch_get_specific(&VideoDataOutputQueueKey) ==
          &VideoDataOutputQueueKey) {
    return;
  }
  dispatch_sync(videoDataOutputQueue, ^{});
}

- (void)teardownAVCapture {
  if (session && [session isRunning]) {
    [session stopRunning];
  }
  if (videoDataOutput) {
    [videoDataOutput setSampleBufferDelegate:nil queue:NULL];
    [self drainVideoDataOutputQueue];
    [videoDataOutput release];
    videoDataOutput = nil;
  }
  if (videoDataOutputQueue) {
    dispatch_release(videoDataOutputQueue);
    videoDataOutputQueue = NULL;
  }
  if (stillImageOutput) {
    [stillImageOutput removeObserver:self forKeyPath:@"capturingStillImage"];
    [stillImageOutput release];
    stillImageOutput = nil;
  }
  [previewLayer removeFromSuperlayer];
  [previewLayer release];
  previewLayer = nil;
  [session release];
  session = nil;
}

- (void)observeValueForKeyPath:(NSString *)keyPath
                      ofObject:(id)object
                        change:(NSDictionary *)change
                       context:(void *)context {
  if (context == AVCaptureStillImageIsCapturingStillImageContext) {
    BOOL isCapturingStillImage =
        [[change objectForKey:NSKeyValueChangeNewKey] boolValue];

    if (isCapturingStillImage) {
      // do flash bulb like animation
      flashView = [[UIView alloc] initWithFrame:[previewView frame]];
      [flashView setBackgroundColor:[UIColor whiteColor]];
      [flashView setAlpha:0.f];
      [[[self view] window] addSubview:flashView];

      [UIView animateWithDuration:.4f
                       animations:^{
                         [flashView setAlpha:1.f];
                       }];
    } else {
      [UIView animateWithDuration:.4f
          animations:^{
            [flashView setAlpha:0.f];
          }
          completion:^(BOOL finished) {
            [flashView removeFromSuperview];
            [flashView release];
            flashView = nil;
          }];
    }
  }
}

- (AVCaptureVideoOrientation)avOrientationForDeviceOrientation:
    (UIDeviceOrientation)deviceOrientation {
  AVCaptureVideoOrientation result =
      (AVCaptureVideoOrientation)(deviceOrientation);
  if (deviceOrientation == UIDeviceOrientationLandscapeLeft)
    result = AVCaptureVideoOrientationLandscapeRight;
  else if (deviceOrientation == UIDeviceOrientationLandscapeRight)
    result = AVCaptureVideoOrientationLandscapeLeft;
  return result;
}

- (IBAction)takePicture:(id)sender {
  if (!session) {
    [self showCaptureErrorWithTitle:@"Camera Unavailable"
                            message:@"Camera capture is not available."];
    return;
  }

  if (captureRequested) {
    captureRequested = NO;
    [self updateCaptureRunningState];
    [sender setTitle:@"Continue" forState:UIControlStateNormal];

    flashView = [[UIView alloc] initWithFrame:[previewView frame]];
    [flashView setBackgroundColor:[UIColor whiteColor]];
    [flashView setAlpha:0.f];
    [[[self view] window] addSubview:flashView];

    [UIView animateWithDuration:.2f
        animations:^{
          [flashView setAlpha:1.f];
        }
        completion:^(BOOL finished) {
          [UIView animateWithDuration:.2f
              animations:^{
                [flashView setAlpha:0.f];
              }
              completion:^(BOOL finished) {
                [flashView removeFromSuperview];
                [flashView release];
                flashView = nil;
              }];
        }];

  } else {
    captureRequested = YES;
    [self updateCaptureRunningState];
    [sender setTitle:@"Freeze Frame" forState:UIControlStateNormal];
  }
}

+ (CGRect)videoPreviewBoxForGravity:(NSString *)gravity
                          frameSize:(CGSize)frameSize
                       apertureSize:(CGSize)apertureSize {
  CGFloat apertureRatio = apertureSize.height / apertureSize.width;
  CGFloat viewRatio = frameSize.width / frameSize.height;

  CGSize size = CGSizeZero;
  if ([gravity isEqualToString:AVLayerVideoGravityResizeAspectFill]) {
    if (viewRatio > apertureRatio) {
      size.width = frameSize.width;
      size.height =
          apertureSize.width * (frameSize.width / apertureSize.height);
    } else {
      size.width =
          apertureSize.height * (frameSize.height / apertureSize.width);
      size.height = frameSize.height;
    }
  } else if ([gravity isEqualToString:AVLayerVideoGravityResizeAspect]) {
    if (viewRatio > apertureRatio) {
      size.width =
          apertureSize.height * (frameSize.height / apertureSize.width);
      size.height = frameSize.height;
    } else {
      size.width = frameSize.width;
      size.height =
          apertureSize.width * (frameSize.width / apertureSize.height);
    }
  } else if ([gravity isEqualToString:AVLayerVideoGravityResize]) {
    size.width = frameSize.width;
    size.height = frameSize.height;
  }

  CGRect videoBox;
  videoBox.size = size;
  if (size.width < frameSize.width)
    videoBox.origin.x = (frameSize.width - size.width) / 2;
  else
    videoBox.origin.x = (size.width - frameSize.width) / 2;

  if (size.height < frameSize.height)
    videoBox.origin.y = (frameSize.height - size.height) / 2;
  else
    videoBox.origin.y = (size.height - frameSize.height) / 2;

  return videoBox;
}

- (void)captureOutput:(AVCaptureOutput *)captureOutput
didOutputSampleBuffer:(CMSampleBufferRef)sampleBuffer
       fromConnection:(AVCaptureConnection *)connection {
  CVPixelBufferRef pixelBuffer = CMSampleBufferGetImageBuffer(sampleBuffer);
  [self runCNNOnFrame:pixelBuffer];
}

- (void)runCNNOnFrame:(CVPixelBufferRef)pixelBuffer {
  if (pixelBuffer == NULL) {
    return;
  }

  if (CVPixelBufferIsPlanar(pixelBuffer)) {
    LOG(ERROR) << "Planar pixel buffers are unsupported";
    return;
  }

  OSType sourcePixelFormat = CVPixelBufferGetPixelFormatType(pixelBuffer);
  tensorflow_camera::PixelLayout pixelLayout;
  if (kCVPixelFormatType_32ARGB == sourcePixelFormat) {
    pixelLayout = tensorflow_camera::PixelLayout::kARGB;
  } else if (kCVPixelFormatType_32BGRA == sourcePixelFormat) {
    pixelLayout = tensorflow_camera::PixelLayout::kBGRA;
  } else {
    LOG(ERROR) << "Unsupported pixel format: " << sourcePixelFormat;
    return;
  }

  const size_t sourceRowBytes = CVPixelBufferGetBytesPerRow(pixelBuffer);
  const size_t sourceWidth = CVPixelBufferGetWidth(pixelBuffer);
  const size_t sourceFullHeight = CVPixelBufferGetHeight(pixelBuffer);
  const size_t sourceDataSize = CVPixelBufferGetDataSize(pixelBuffer);
  tensorflow_camera::FrameLayout frameLayout;
  if (sourceWidth > INT_MAX || sourceFullHeight > INT_MAX ||
      !tensorflow_camera::BuildFrameLayout(
          sourceWidth, sourceFullHeight, sourceRowBytes, sourceDataSize,
          pixelLayout, &frameLayout)) {
    LOG(ERROR) << "Invalid pixel buffer geometry";
    return;
  }
  if (CVPixelBufferLockBaseAddress(pixelBuffer, 0) != kCVReturnSuccess) {
    LOG(ERROR) << "Could not lock pixel buffer base address";
    return;
  }
  unsigned char *sourceBaseAddr =
      (unsigned char *)(CVPixelBufferGetBaseAddress(pixelBuffer));
  if (sourceBaseAddr == NULL) {
    CVPixelBufferUnlockBaseAddress(pixelBuffer, 0);
    return;
  }
  tensorflow::Tensor image_tensor(
      tensorflow::DT_FLOAT,
      tensorflow::TensorShape(
          {1, wanted_input_height, wanted_input_width, wanted_input_channels}));
  auto image_tensor_mapped = image_tensor.tensor<float, 4>();
  float *out = image_tensor_mapped.data();
  bool sampledFrame = true;
  for (int y = 0; y < wanted_input_height; ++y) {
    float *out_row = out + (y * wanted_input_width * wanted_input_channels);
    for (int x = 0; x < wanted_input_width; ++x) {
      size_t sourceOffset = 0;
      if (!tensorflow_camera::SourcePixelOffset(
              frameLayout, static_cast<size_t>(x), static_cast<size_t>(y),
              static_cast<size_t>(wanted_input_width),
              static_cast<size_t>(wanted_input_height), &sourceOffset)) {
        sampledFrame = false;
        break;
      }
      tensorflow::uint8 *in_pixel = sourceBaseAddr + sourceOffset;
      float *out_pixel = out_row + (x * wanted_input_channels);
      for (int c = 0; c < wanted_input_channels; ++c) {
        size_t sourceChannel = 0;
        if (!tensorflow_camera::SourceChannelOffset(
                pixelLayout, static_cast<size_t>(c), &sourceChannel)) {
          sampledFrame = false;
          break;
        }
        out_pixel[c] = (in_pixel[sourceChannel] - input_mean) / input_std;
      }
    }
    if (!sampledFrame) {
      break;
    }
  }
  if (!sampledFrame) {
    LOG(ERROR) << "Invalid pixel buffer sampling arithmetic";
    CVPixelBufferUnlockBaseAddress(pixelBuffer, 0);
    return;
  }

  if (tf_session.get()) {
    std::vector<tensorflow::Tensor> outputs;
    tensorflow::Status run_status = tf_session->Run(
        {{input_layer_name, image_tensor}}, {output_layer_name}, {}, &outputs);
    if (!run_status.ok()) {
      LOG(ERROR) << "Running model failed:" << run_status;
    } else if (outputs.empty()) {
      LOG(ERROR) << "Running model produced no output tensors";
    } else if (labels.empty()) {
      LOG(ERROR) << "No labels loaded for model predictions";
    } else {
      tensorflow::Tensor *output = &outputs.front();
      if (output->dtype() != tensorflow::DT_FLOAT) {
        LOG(ERROR) << "Skipping model output with unexpected dtype";
      } else {
        auto predictions = output->flat<float>();
        const size_t prediction_count = static_cast<size_t>(predictions.size());
        const size_t label_count = labels.size();
        const size_t result_count =
            prediction_count < label_count ? prediction_count : label_count;

        std::vector<float> prediction_values;
        prediction_values.reserve(result_count);
        for (size_t index = 0; index < result_count; index += 1) {
          const float predictionValue = predictions(index);
          prediction_values.push_back(predictionValue);
          if (!std::isfinite(predictionValue)) {
            LOG(ERROR) << "Skipping non-finite model prediction";
            continue;
          }
          if (!tensorflow_camera::IsValidModelPrediction(predictionValue)) {
            LOG(ERROR) << "Skipping out-of-range model prediction";
            continue;
          }
        }

        const std::vector<tensorflow_camera::LabeledPrediction>
            labeled_predictions = tensorflow_camera::SelectLabeledPredictions(
                prediction_values, labels, 0.05f);
        NSMutableDictionary *newValues = [NSMutableDictionary dictionary];
        for (const tensorflow_camera::LabeledPrediction& prediction :
             labeled_predictions) {
          NSString *labelObject =
              [NSString stringWithUTF8String:prediction.label.c_str()];
          if (!labelObject) {
            LOG(ERROR) << "Skipping invalid UTF-8 model label";
            continue;
          }
          NSNumber *valueObject = [NSNumber numberWithFloat:prediction.value];
          [newValues setObject:valueObject forKey:labelObject];
        }
        dispatch_async(dispatch_get_main_queue(), ^(void) {
          [self setPredictionValues:newValues];
        });
      }
    }
  }
  CVPixelBufferUnlockBaseAddress(pixelBuffer, 0);
}

- (void)dealloc {
  [[NSNotificationCenter defaultCenter] removeObserver:self];
  [self teardownAVCapture];
  [square release];
  [synth release];
  [labelLayers release];
  [oldPredictionValues release];
  [super dealloc];
}

// use front/back camera
- (IBAction)switchCameras:(id)sender {
  AVCaptureSession *captureSession = [previewLayer session];
  if (!captureSession) {
    [self showCaptureErrorWithTitle:@"Camera Unavailable"
                            message:@"Camera capture is not running."];
    return;
  }

  AVCaptureDevicePosition desiredPosition;
  if (isUsingFrontFacingCamera)
    desiredPosition = AVCaptureDevicePositionBack;
  else
    desiredPosition = AVCaptureDevicePositionFront;

  BOOL didSwitchCamera = NO;
  for (AVCaptureDevice *d in
       [AVCaptureDevice devicesWithMediaType:AVMediaTypeVideo]) {
    if ([d position] == desiredPosition) {
      NSError *error = nil;
      AVCaptureDeviceInput *input =
          [AVCaptureDeviceInput deviceInputWithDevice:d error:&error];
      if (error || !input) {
        NSString *message = error ? [error localizedDescription]
                                  : @"Could not create a camera input.";
        [self showCaptureErrorWithTitle:@"Camera Switch Failed"
                                message:message];
        return;
      }

      NSArray *oldInputs = [NSArray arrayWithArray:[captureSession inputs]];
      [captureSession beginConfiguration];
      for (AVCaptureInput *oldInput in oldInputs) {
        [captureSession removeInput:oldInput];
      }
      if ([captureSession canAddInput:input]) {
        [captureSession addInput:input];
        didSwitchCamera = YES;
      } else {
        for (AVCaptureInput *oldInput in oldInputs) {
          if ([captureSession canAddInput:oldInput]) {
            [captureSession addInput:oldInput];
          }
        }
      }
      [captureSession commitConfiguration];
      break;
    }
  }
  if (!didSwitchCamera) {
    [self showCaptureErrorWithTitle:@"Camera Switch Failed"
                            message:@"Requested camera is not available."];
    return;
  }
  isUsingFrontFacingCamera = !isUsingFrontFacingCamera;
}

- (void)didReceiveMemoryWarning {
  [super didReceiveMemoryWarning];
}

- (void)viewDidLoad {
  [super viewDidLoad];
  captureRequested = YES;
  viewIsVisible = NO;
  applicationIsActive =
      [[UIApplication sharedApplication] applicationState] ==
      UIApplicationStateActive;
  NSNotificationCenter *notificationCenter =
      [NSNotificationCenter defaultCenter];
  [notificationCenter addObserver:self
                         selector:@selector(applicationDidBecomeActive:)
                             name:UIApplicationDidBecomeActiveNotification
                           object:nil];
  [notificationCenter addObserver:self
                         selector:@selector(applicationWillResignActive:)
                             name:UIApplicationWillResignActiveNotification
                           object:nil];
  square = [[UIImage imageNamed:@"squarePNG"] retain];
  synth = [[AVSpeechSynthesizer alloc] init];
  labelLayers = [[NSMutableArray alloc] init];
  oldPredictionValues = [[NSMutableDictionary alloc] init];
  
  tensorflow::Status load_status;
  if (model_uses_memory_mapping) {
    load_status = LoadMemoryMappedModel(
        model_file_name, model_file_type, &tf_session, &tf_memmapped_env);
  } else {
    load_status = LoadModel(model_file_name, model_file_type, &tf_session);
  }
  if (!load_status.ok()) {
    LOG(ERROR) << "Couldn't load model: " << load_status;
    [self showCaptureErrorWithTitle:@"Model Unavailable"
                            message:@"The TensorFlow model could not be loaded."];
    return;
  }

  tensorflow::Status labels_status =
      LoadLabels(labels_file_name, labels_file_type, &labels);
  if (!labels_status.ok()) {
    LOG(ERROR) << "Couldn't load labels: " << labels_status;
    [self showCaptureErrorWithTitle:@"Labels Unavailable"
                            message:@"The TensorFlow labels file could not be loaded."];
    return;
  }
  [self setupAVCapture];
}

- (void)viewDidUnload {
  [super viewDidUnload];
  [oldPredictionValues release];
  oldPredictionValues = nil;
}

- (void)viewWillAppear:(BOOL)animated {
  [super viewWillAppear:animated];
  viewIsVisible = YES;
  [self updateCaptureRunningState];
}

- (void)viewDidAppear:(BOOL)animated {
  [super viewDidAppear:animated];
}

- (void)viewWillDisappear:(BOOL)animated {
  viewIsVisible = NO;
  [self updateCaptureRunningState];
  [super viewWillDisappear:animated];
}

- (void)viewDidDisappear:(BOOL)animated {
  [super viewDidDisappear:animated];
}

- (BOOL)shouldAutorotateToInterfaceOrientation:
    (UIInterfaceOrientation)interfaceOrientation {
  return (interfaceOrientation == UIInterfaceOrientationPortrait);
}

- (BOOL)prefersStatusBarHidden {
  return YES;
}

- (void)setPredictionValues:(NSDictionary *)newValues {
  const float decayValue = 0.75f;
  const float updateValue = 0.25f;
  const float minimumThreshold = 0.01f;

  NSMutableDictionary *decayedPredictionValues =
      [[NSMutableDictionary alloc] init];
  for (NSString *label in oldPredictionValues) {
    NSNumber *oldPredictionValueObject =
        [oldPredictionValues objectForKey:label];
    const float oldPredictionValue = [oldPredictionValueObject floatValue];
    const float decayedPredictionValue = (oldPredictionValue * decayValue);
    if (decayedPredictionValue > minimumThreshold) {
      NSNumber *decayedPredictionValueObject =
          [NSNumber numberWithFloat:decayedPredictionValue];
      [decayedPredictionValues setObject:decayedPredictionValueObject
                                  forKey:label];
    }
  }
  [oldPredictionValues release];
  oldPredictionValues = decayedPredictionValues;

  for (NSString *label in newValues) {
    NSNumber *newPredictionValueObject = [newValues objectForKey:label];
    NSNumber *oldPredictionValueObject =
        [oldPredictionValues objectForKey:label];
    if (!oldPredictionValueObject) {
      oldPredictionValueObject = [NSNumber numberWithFloat:0.0f];
    }
    const float newPredictionValue = [newPredictionValueObject floatValue];
    const float oldPredictionValue = [oldPredictionValueObject floatValue];
    const float updatedPredictionValue =
        (oldPredictionValue + (newPredictionValue * updateValue));
    NSNumber *updatedPredictionValueObject =
        [NSNumber numberWithFloat:updatedPredictionValue];
    [oldPredictionValues setObject:updatedPredictionValueObject forKey:label];
  }
  NSArray *candidateLabels = [NSMutableArray array];
  for (NSString *label in oldPredictionValues) {
    NSNumber *oldPredictionValueObject =
        [oldPredictionValues objectForKey:label];
    const float oldPredictionValue = [oldPredictionValueObject floatValue];
    if (oldPredictionValue > 0.05f) {
      NSDictionary *entry = @{
        @"label" : label,
        @"value" : oldPredictionValueObject
      };
      candidateLabels = [candidateLabels arrayByAddingObject:entry];
    }
  }
  NSSortDescriptor *sort =
      [NSSortDescriptor sortDescriptorWithKey:@"value" ascending:NO];
  NSArray *sortedLabels = [candidateLabels
      sortedArrayUsingDescriptors:[NSArray arrayWithObject:sort]];

  const float leftMargin = 10.0f;
  const float topMargin = 10.0f;

  const float valueWidth = 48.0f;
  const float valueHeight = 26.0f;

  const float labelWidth = 246.0f;
  const float labelHeight = 26.0f;

  const float labelMarginX = 5.0f;
  const float labelMarginY = 5.0f;

  [self removeAllLabelLayers];

  int labelCount = 0;
  for (NSDictionary *entry in sortedLabels) {
    NSString *label = [entry objectForKey:@"label"];
    NSNumber *valueObject = [entry objectForKey:@"value"];
    const float value = [valueObject floatValue];

    const float originY =
        (topMargin + ((labelHeight + labelMarginY) * labelCount));

    const int valuePercentage = (int)roundf(value * 100.0f);

    const float valueOriginX = leftMargin;
    NSString *valueText = [NSString stringWithFormat:@"%d%%", valuePercentage];

    [self addLabelLayerWithText:valueText
                        originX:valueOriginX
                        originY:originY
                          width:valueWidth
                         height:valueHeight
                      alignment:kCAAlignmentRight];

    const float labelOriginX = (leftMargin + valueWidth + labelMarginX);

    [self addLabelLayerWithText:[label capitalizedString]
                        originX:labelOriginX
                        originY:originY
                          width:labelWidth
                         height:labelHeight
                      alignment:kCAAlignmentLeft];

    if ((labelCount == 0) && (value > 0.5f)) {
      [self speak:[label capitalizedString]];
    }

    labelCount += 1;
    if (labelCount > 4) {
      break;
    }
  }
}

- (void)removeAllLabelLayers {
  for (CATextLayer *layer in labelLayers) {
    [layer removeFromSuperlayer];
  }
  [labelLayers removeAllObjects];
}

- (void)addLabelLayerWithText:(NSString *)text
                      originX:(float)originX
                      originY:(float)originY
                        width:(float)width
                       height:(float)height
                    alignment:(NSString *)alignment {
  NSString *const font = @"Menlo-Regular";
  const float fontSize = 20.0f;

  const float marginSizeX = 5.0f;
  const float marginSizeY = 2.0f;

  const CGRect backgroundBounds = CGRectMake(originX, originY, width, height);

  const CGRect textBounds =
      CGRectMake((originX + marginSizeX), (originY + marginSizeY),
                 (width - (marginSizeX * 2)), (height - (marginSizeY * 2)));

  CATextLayer *background = [CATextLayer layer];
  [background setBackgroundColor:[UIColor blackColor].CGColor];
  [background setOpacity:0.5f];
  [background setFrame:backgroundBounds];
  background.cornerRadius = 5.0f;

  [[self.view layer] addSublayer:background];
  [labelLayers addObject:background];

  CATextLayer *layer = [CATextLayer layer];
  [layer setForegroundColor:[UIColor whiteColor].CGColor];
  [layer setFrame:textBounds];
  [layer setAlignmentMode:alignment];
  [layer setWrapped:YES];
  [layer setFont:font];
  [layer setFontSize:fontSize];
  layer.contentsScale = [[UIScreen mainScreen] scale];
  [layer setString:text];

  [[self.view layer] addSublayer:layer];
  [labelLayers addObject:layer];
}

- (void)setPredictionText:(NSString *)text withDuration:(float)duration {
  if (duration > 0.0) {
    CABasicAnimation *colorAnimation =
        [CABasicAnimation animationWithKeyPath:@"foregroundColor"];
    colorAnimation.duration = duration;
    colorAnimation.fillMode = kCAFillModeForwards;
    colorAnimation.removedOnCompletion = NO;
    colorAnimation.fromValue = (id)[UIColor darkGrayColor].CGColor;
    colorAnimation.toValue = (id)[UIColor whiteColor].CGColor;
    colorAnimation.timingFunction =
        [CAMediaTimingFunction functionWithName:kCAMediaTimingFunctionLinear];
    [self.predictionTextLayer addAnimation:colorAnimation
                                    forKey:@"colorAnimation"];
  } else {
    self.predictionTextLayer.foregroundColor = [UIColor whiteColor].CGColor;
  }

  [self.predictionTextLayer removeFromSuperlayer];
  [[self.view layer] addSublayer:self.predictionTextLayer];
  [self.predictionTextLayer setString:text];
}

- (void)speak:(NSString *)words {
  if ([synth isSpeaking]) {
    return;
  }
  AVSpeechUtterance *utterance =
      [AVSpeechUtterance speechUtteranceWithString:words];
  utterance.voice = [AVSpeechSynthesisVoice voiceWithLanguage:@"en-US"];
  utterance.rate = 0.75 * AVSpeechUtteranceDefaultSpeechRate;
  [synth speakUtterance:utterance];
}

@end

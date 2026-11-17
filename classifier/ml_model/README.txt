========================================================================
AYUMORPH TRAINED MOBILENETV2 MODEL PLACEMENT INSTRUCTIONS
========================================================================

Place your trained Keras/TensorFlow model file in this directory:

  classifier/ml_model/model.h5
  OR
  classifier/ml_model/model.keras

Expected Specifications:
- Architecture: MobileNetV2 Transfer Learning
- Input shape: (None, 224, 224, 3)
- Output: Dense(1, activation='sigmoid') for binary classification
  or Dense(N, activation='softmax') for multi-class

When you start the Django server and upload a plant photo, AyuMorph will:
1. Locate the model here
2. Load it once into memory (cached singleton)
3. Preprocess incoming images (224x224, MobileNetV2 [-1, 1] scaling)
4. Execute prediction and return the real confidence and class

Note: If no model file is placed here, the application will display a clear,
actionable message instructing the user/evaluator to place the trained model
file rather than fabricating any fake results.
========================================================================

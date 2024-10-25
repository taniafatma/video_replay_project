from ultralytics import YOLO

# Load the trained model
model = YOLO("best.pt")

# Path ke video test
test_video_path = 'video_testing.mp4'

# Menggunakan model untuk memprediksi
results = model.predict(source=test_video_path, save=True)

# Hasil prediksi disimpan dalam direktori default dengan bounding boxes
print(f"Predictions saved for {test_video_path}.")

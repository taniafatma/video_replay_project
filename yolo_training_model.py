from ultralytics import YOLO

# Memuat model YOLOv8 yang sudah pre-trained
model = YOLO('yolov8s.pt')

# Menjalankan pelatihan pada dataset sepak bola
results = model.train(data='data.yaml', epochs=50, imgsz=640)

# Menampilkan ringkasan hasil pelatihan
print(f"Training completed. Model trained on {results['train']['n']} images.")
print(f"Best results: {results['best']}")
print(f"Model saved at: {results['save_dir']}/weights/best.pt")

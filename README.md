# 🛠️ Procedural Defect Generator & Synthetic Data Pipeline

This tool is a high-performance **Synthetic Data Generator** built for Blender. It automates the creation of industrial parts with high-fidelity, randomized surface defects, providing a scalable solution for training inspection algorithms and quality control AI.

By leveraging procedural texturing and automated scene manipulation, this script eliminates the "Data Bottleneck" in industrial automation, allowing for the generation of thousands of perfectly labeled, diverse training images in minutes.

## Screenshots
<img width="458" height="300" alt="image" src="https://github.com/user-attachments/assets/316683ca-765d-4efc-9493-3440a8e2eca2" />
<img width="451" height="100" alt="image" src="https://github.com/user-attachments/assets/8d291401-1e40-4070-b10e-2c360ba38fac" />


---

## 📖 Table of Contents
* [What the Tool Does](#what-the-tool-does)
* [Key Features](#key-features)
* [Use Cases](#use-cases)
* [Optical & Render Setup](#optical--render-setup)

---

## 🔍 What the Tool Does
The tool programmatically constructs 3D geometry and applies a **tri-layer procedural material stack**. Unlike standard static textures, these defects are mathematically generated, meaning no two scuffs or bumps are ever identical. 

The script then automates a studio-grade "Optical Rig" to capture the part from multiple standardized angles, ensuring the data is ready for immediate use in machine learning pipelines.

---

## 🚀 Key Features
* **Procedural Defect Layers:**
    * **Noise Bump:** Simulates casting irregularities and surface roughness.
    * **Magic Distortion:** Replicates machining artifacts and structural wear.
    * **Dynamic Paint Scuffs:** A mask-based system for contamination, rust, or paint chips with adjustable density (`D3_COUNT`) and size (`D3_SIZE`).
* **Automated Dataset Variation:** Change the `seed` variable to instantly shuffle the location and shape of every defect.
* **Multi-View Capture:** Automatically executes a 4-step rotation sequence (Z-axis shifts and 180° Y-axis flips).

---

## 🎯 Use Cases

### **1. Cosmetic Vision Inspection**
Standard vision systems often struggle with "cosmetic" defects (scratches, scuffs) because they are non-uniform. This tool allows engineers to simulate these rare failures at scale to test the sensitivity of industrial cameras and lighting configurations.

### **2. ML/AI Model Training (Synthetic Data)**
Deep Learning models require thousands of images. This pipeline generates:
* **Balanced Datasets:** Create equal amounts of "Pass" and "Fail" data.
* **Hard-Negative Mining:** Generate "borderline" defects to sharpen model decision boundaries.
* **Edge Case Simulation:** Model defects that rarely occur in production.

### **3. Optical Setup Optimization**
Test how different lighting angles (e.g., low-angle darkfield vs. high-angle brightfield) interact with surface defects before purchasing physical hardware.

---

## 📸 Optical & Render Setup
The script creates a professional inspection environment:
* **The Rig:** A dual-camera system positioned at specific tilt angles (`USER_TILT_ANGLE`).
* **The Lighting:** Synchronized Area Lights to simulate industrial LED bars.
* **The Sequence:**
    1. **Original View:** Baseline orientation.
    2. **90° Z-Rotation:** Captures side-profile defect stretching.
    3. **180° Y-Flip:** True "bottom-to-top" flip to inspect the reverse side.
    4. **Combined Flip/Rotate:** Full hemispherical coverage.

---

## 🛠️ Usage
1.  **Requirement:** Blender 3.6 or 4.0+.
2.  **Setup:** Copy `scripts/automated_render.py` into the Blender Scripting Tab.
3.  **Config:** Set your `save_folder` and toggle `ENABLE_PAINT_DEFECT` to `True`.
4.  **Run:** Hit **Run Script**.

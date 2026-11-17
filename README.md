# AyuMorph &ndash; Ayurvedic Plant Intelligence Portal
### Academic B.Tech Information Technology Capstone Project

![Python 3.10+](https://img.shields.io/badge/Python-3.10%20%7C%203.11-blue.svg)
![Django 5.1](https://img.shields.io/badge/Django-5.1-092E20.svg)
![Deep Learning](https://img.shields.io/badge/Model-MobileNetV2-brightgreen.svg)
![Status](https://img.shields.io/badge/Build-Passing%20(17%2F17%20Tests)-success.svg)

---

## 1. Project Overview

**AyuMorph** is an academic computer-vision web portal designed to identify and classify medicinal Ayurvedic plants from digital photographs. Built for an academic B.Tech Information Technology viva and final-year demonstration, AyuMorph bridges classical ethnobotanical documentation with modern deep learning.

Users can upload images of plant specimens (leaves, flowers, or stems). The portal processes the image through an optimized **MobileNetV2 Transfer Learning** convolutional neural network, presents the classified category and statistical confidence percentage, links matched botanical records, and maintains an auditable, user-isolated classification history.

> **Academic & Medical Notice:** AyuMorph provides AI-assisted botanical identification strictly for educational and scientific research purposes. Documented traditional uses are compiled from classical Ayurvedic texts and do not constitute guaranteed clinical treatments or medical prescriptions.

---

## 2. Key Features

- **MobileNetV2 Vision Inference Engine:**
  - Standardized $224 \times 224$ image preprocessing with MobileNetV2 normalizations ($[-1.0, 1.0]$ pixel bounds).
  - In-memory cached model loading (singleton pattern) to prevent redundant disk reloads.
  - Transparent binary decision thresholding ($\ge 0.50$) with configurable class mappings.
- **Defensive Multi-Tier Validation:**
  - Client-side and server-side file format checks (JPEG, PNG, WEBP).
  - Maximum upload size limitation ($5\text{ MB}$).
  - Byte-level image integrity checks using Pillow (`Image.verify`).
- **Researcher Workspace & Dashboard:**
  - Real-time statistics: Total queries, Ayurvedic detections, and Non-Ayurvedic counts.
  - Recent query snapshots with quick access to results and technical audits.
- **Botanical Knowledge Repository:**
  - Detailed catalog of documented reference species with binomial nomenclature, morphological characteristics, and diagnostic field features.
  - Classical Ayurvedic literature applications framed responsibly.
  - Search and category filtering.
- **Secure Authentication & User Isolation:**
  - Built with Django's native authentication framework (PBKDF2 SHA-256 password hashing).
  - Strict user-isolation: Researchers only view, manage, and delete their own prediction histories.
- **Customized Django Admin Panel:**
  - Thumbnail previews of submitted images.
  - Auditing tools for predictions, confidence scores, and latency metrics.

---

## 3. Technology Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Backend Framework** | Django 5.1 | Modular architecture, ORM, secure sessions, CSRF protection |
| **Deep Learning** | TensorFlow / Keras | MobileNetV2 Transfer Learning, inference execution |
| **Image Processing** | Pillow (PIL) | Verification, resizing, and color space transformations |
| **Numerical Computing**| NumPy | Array transformations and tensor operations |
| **Database** | SQLite 3 | Relational data persistence (development standard) |
| **Frontend** | HTML5, CSS3, Bootstrap 5.3 | Responsive botanical design, mobile-friendly interface |
| **Client Scripts** | Vanilla JavaScript | Drag-and-drop file uploads, instant preview, loading overlay |

---

## 4. System Architecture

```
User (Browser)
      │
      ▼
Django Routing (ayumorph/urls.py)
      │
      ├── Authentication Layer (accounts/)
      │     └── PBKDF2 Password Hashing, Session Management
      │
      ├── Botanical Catalog (plants/)
      │     └── Species Repository, Taxonomy, Traditional Literature
      │
      └── Vision Classifier (classifier/)
            │
            ├── Forms & Image Validation (Pillow integrity, 5 MB limit)
            │
            ├── Inference Pipeline (classifier/ml/predictor.py)
            │     ├── Image Resize to 224x224
            │     ├── MobileNetV2 Normalization: (x / 127.5) - 1.0
            │     ├── In-Memory MobileNetV2 Model (Singleton)
            │     └── Sigmoid Thresholding (>= 0.5)
            │
            └── Database Persistence (classifier/models.py)
                  └── Scoped to Authenticated User
```

---

## 5. Directory Structure

```
AyuMorph(Django)/
│
├── manage.py                   # Django command-line execution utility
├── requirements.txt            # Project dependencies
├── README.md                   # Complete academic documentation
├── .env.example                # Environment variables template
├── .gitignore                  # Git exclusion rules
│
├── ayumorph/                   # Project Configuration Package
│   ├── __init__.py
│   ├── settings.py             # Settings, paths, security parameters
│   ├── urls.py                 # Master URL dispatching
│   ├── wsgi.py                 # WSGI web server gateway
│   └── asgi.py                 # ASGI asynchronous entrypoint
│
├── accounts/                   # User Authentication & Profiles
│   ├── models.py               # User Profile extension model
│   ├── views.py                # Register, Login, Logout, Profile views
│   ├── forms.py                # UserCreationForm and profile forms
│   ├── signals.py              # Automatic Profile creation signal
│   ├── urls.py
│   └── admin.py
│
├── plants/                     # Botanical Species Repository
│   ├── models.py               # Plant model (Taxonomy, Morphology, Uses)
│   ├── views.py                # Plant list and plant detail views
│   ├── forms.py                # Plant catalog form
│   ├── urls.py
│   ├── admin.py
│   └── management/
│       └── commands/
│           └── seed_plants.py  # Reference plants seeder command
│
├── classifier/                 # Vision Classification & ML Engine
│   ├── models.py               # Prediction model with latency & confidence
│   ├── views.py                # Dashboard, Upload, Result, History views
│   ├── forms.py                # PlantImageUploadForm with Pillow checks
│   ├── urls.py
│   ├── admin.py
│   │
│   ├── ml/                     # Dedicated Machine Learning Package
│   │   ├── __init__.py
│   │   ├── config.py           # Preprocessing settings, threshold, labels
│   │   └── predictor.py        # PlantPredictor singleton & inference
│   │
│   └── ml_model/               # Model Storage Directory
│       ├── .gitkeep
│       └── README.txt          # Placement instructions for model.h5
│
├── templates/                  # Frontend HTML Templates (Bootstrap 5.3)
│   ├── base.html               # Shared layout, navbar, messages, footer
│   ├── home.html               # Hero landing page
│   ├── about.html              # Methodology & academic overview
│   ├── 400.html, 403.html, 404.html, 500.html
│   ├── accounts/
│   │   ├── login.html
│   │   ├── register.html
│   │   └── profile.html
│   ├── classifier/
│   │   ├── dashboard.html
│   │   ├── upload.html
│   │   ├── result.html
│   │   ├── history.html
│   │   ├── prediction_detail.html
│   │   └── prediction_confirm_delete.html
│   └── plants/
│       ├── plant_list.html
│       └── plant_detail.html
│
├── static/                     # Static Web Assets
│   ├── css/style.css           # Botanical styling, themes, animations
│   ├── js/main.js              # Drag-and-drop, preview, upload spinner
│   └── images/logo.svg         # AyuMorph vector logo
│
├── media/                      # Media Storage (Uploaded specimens)
│   ├── plant_images/
│   ├── plants/
│   └── avatars/
│
└── tests/                      # Automated Test Suite (17 Tests)
    ├── __init__.py
    ├── test_models.py          # Model integrity & signals tests
    ├── test_views.py           # View endpoints & isolation tests
    └── test_ml.py              # Preprocessing & inference mock tests
```

---

## 6. Installation & Setup Guide (Windows & Cross-Platform)

### Step 1: Verify Python Version
Open Command Prompt or PowerShell:
```powershell
python --version
```
> **Recommendation:** Python 3.10 or 3.11 is recommended for native TensorFlow binary packages on Windows.

### Step 2: Create and Activate Virtual Environment
Navigate to the project root directory:
```powershell
# Create virtual environment
python -m venv venv

# Activate on Windows (PowerShell):
venv\Scripts\Activate.ps1

# (Or Command Prompt):
venv\Scripts\activate.bat
```

### Step 3: Install Required Dependencies
```powershell
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Copy `.env.example` to `.env`:
```powershell
Copy-Item .env.example .env
```

### Step 5: Apply Database Migrations
```powershell
python manage.py makemigrations
python manage.py migrate
```

### Step 6: Seed Initial Botanical Data
Populate reference Ayurvedic plant records (Tulsi, Neem, Ashwagandha, Brahmi, Amla, Aloe Vera):
```powershell
python manage.py seed_plants
```

### Step 7: Create an Administrator Account
```powershell
python manage.py createsuperuser
```
Follow the prompts to enter an administrative username, email, and password.

---

## 7. Placing Your Trained MobileNetV2 Model

1. Take your trained `.h5` or `.keras` model file.
2. Place it into the following directory:
   ```
   classifier/ml_model/model.h5
   ```
   *(Alternatively: `classifier/ml_model/model.keras`)*
3. **Configuration Check:** Open `classifier/ml/config.py` to confirm your class labels:
   ```python
   CLASS_MAPPING = {
       0: "Ayurvedic Plant",
       1: "Non-Ayurvedic Plant"
   }
   ```
   If your training code used a different order in `ImageDataGenerator`, adjust this dictionary accordingly.

*Note: If no model file is placed, AyuMorph gracefully alerts the user on the upload page without generating fake predictions.*

---

## 8. Running the Application

Start the local Django development server:
```powershell
python manage.py runserver
```

Open your browser and navigate to:
- **Web Portal:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Admin Panel:** [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

## 9. Running the Automated Test Suite

AyuMorph comes equipped with a comprehensive 17-test suite covering authentication, user-isolation security, database signals, and image preprocessing tensors:

```powershell
python manage.py test
```

Expected output:
```
Found 17 test(s).
Creating test database for alias 'default'...
................
----------------------------------------------------------------------
Ran 17 tests in ~20s

OK
Destroying test database for alias 'default'...
```

---

## 10. Academic Viva Explanation & Q&A

### Q1: Why use MobileNetV2 instead of heavier models like VGG16 or ResNet50?
**Answer:** MobileNetV2 uses **depthwise separable convolutions** and **inverted residual bottleneck blocks**. It achieves high feature extraction accuracy with significantly fewer parameters (~3.5M vs ~138M in VGG16) and low computational complexity (MACs), making it ideal for responsive web inference.

### Q2: What is Transfer Learning and how is it utilized here?
**Answer:** The MobileNetV2 backbone is pre-trained on the ImageNet dataset ($1.4\text{M}$ images across $1000$ categories). The lower convolutional layers already know general visual primitives (edges, contours, leaf venation, textures). We freeze or reuse these layers, attach a custom classification head (`GlobalAveragePooling2D` $\rightarrow$ `Dense(128, ReLU)` $\rightarrow$ `Dense(1, Sigmoid)`), and train on domain-specific plant images.

### Q3: Why is the model loaded via a Singleton pattern?
**Answer:** Neural network weight matrices can take several hundred milliseconds to load from disk. Reloading the model on every HTTP request would cause server memory leaks and unacceptable latency. The `PlantPredictor` class loads the model into memory once and reuses the cached object across all inference queries.

### Q4: How is user data protected?
**Answer:** User isolation is enforced at the ORM query level: `Prediction.objects.filter(user=request.user)`. Even if another researcher guesses a prediction ID, the view returns an HTTP 404/403. Passwords are never stored in plaintext; they are securely hashed using Django's PBKDF2 with a SHA-256 digest and salt.

---

## 11. Future Enhancements

1. **Multi-Class Granularity:** Expanding from binary classification to granular multi-class identification for hundreds of rare medicinal species.
2. **Offline Mobile Integration:** Exporting the MobileNetV2 model to TensorFlow Lite (`.tflite`) for offline mobile field identification.
3. **Leaf Disease Detection:** Augmenting the pipeline with secondary models to identify botanical leaf blights, fungal infections, and nutritional deficiencies.
4. **Geolocation Mapping:** Logging GPS coordinates of specimen discoveries to construct geospatial biodiversity maps.

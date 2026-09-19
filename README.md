# Autism Prediction Disorder

## 📌 Project Overview

Autism Prediction Disorder is a Machine Learning based web application developed using Python and Flask.

The project uses a trained Machine Learning model to predict the possibility of Autism Spectrum Disorder (ASD) based on the input data provided by the user.

The application provides a web interface where users can enter the required information and receive a prediction from the trained model.

This project is developed for educational and research purposes and should not be considered a medical diagnosis.

---

## 🎯 Project Objective

The main objectives of this project are:

- To develop a Machine Learning model for Autism Spectrum Disorder prediction.
- To preprocess and analyze the available dataset.
- To train and save a Machine Learning model.
- To create a web application using Flask.
- To allow users to provide input through a web interface.
- To display the prediction result through the web application.
- To integrate database functionality with the application.

---

## 🛠️ Technologies Used

- Python
- Flask
- Scikit-learn
- Pandas
- NumPy
- Matplotlib
- Seaborn
- OpenCV
- PyMongo
- MongoDB
- HTML
- CSS
- Jupyter Notebook

---

## 🤖 Machine Learning

The project uses a trained Machine Learning model to perform the prediction.

The trained model is stored in:

```text
model.pkl
```

The feature/column information required by the model is stored in:

```text
columns.pkl
```

The project also contains Machine Learning analysis and visualization files such as:

- Confusion Matrix
- Feature Importance
- Jupyter Notebook
- Dataset
- Trained Model

---

## 🌐 Web Application

The web application is developed using Flask.

The main Flask application is:

```text
app.py
```

The application provides functionality for:

- User input
- Autism prediction
- Database operations
- Web-based interface
- Facial tracking functionality

---

## 📂 Project Structure

```text
Autism_Prediction_Disorderproject/
│
├── data/
├── static/
├── templates/
│
├── app.py
├── autism.py
├── Autism_prediction.py
├── autism.ipynb
│
├── database.py
├── check_db.py
├── fix_all.py
├── fix_db.py
├── make_admin.py
├── facial_tracker.py
│
├── model.pkl
├── columns.pkl
│
├── confusion_matrix.png
├── feature_importance.png
│
├── autism.csv
├── Autism.csv.zip
├── autism.db
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 📄 Important Files

### `app.py`

The main Flask application file responsible for running the web application.

### `model.pkl`

Contains the trained Machine Learning model used for making predictions.

### `columns.pkl`

Contains the feature/column information required by the Machine Learning model.

### `autism.ipynb`

Jupyter Notebook containing the Machine Learning development, analysis, and experimentation.

### `database.py`

Contains database-related functionality used by the application.

### `facial_tracker.py`

Contains the facial tracking functionality implemented using OpenCV.

### `confusion_matrix.png`

Contains the confusion matrix visualization used for evaluating the classification model.

### `feature_importance.png`

Contains the feature importance visualization.

---

# ⚙️ Installation

## 1. Clone the Repository

```bash
git clone https://github.com/Shubhapal6666/Autism.git
```

## 2. Open the Project Folder

```bash
cd Autism
```

## 3. Create a Virtual Environment

```bash
python -m venv venv
```

## 4. Activate the Virtual Environment

### Windows PowerShell

```powershell
venv\Scripts\Activate.ps1
```

### Windows CMD

```cmd
venv\Scripts\activate
```

## 5. Install Required Libraries

```bash
pip install -r requirements.txt
```

---

# ▶️ Run the Application

After installing all the required dependencies, run the Flask application:

```bash
python app.py
```

The application will start on the local Flask server.

Open your browser and visit:

```text
http://127.0.0.1:5000
```

---

# 📊 Machine Learning Workflow

The general workflow of the project is:

```text
Dataset
   ↓
Data Preprocessing
   ↓
Data Analysis
   ↓
Feature Selection
   ↓
Model Training
   ↓
Model Evaluation
   ↓
Model Saving
   ↓
Flask Web Application
   ↓
User Input
   ↓
Prediction
   ↓
Result
```

---

# 📈 Project Components

The project contains the following major components:

### 1. Dataset

The project contains the dataset used for Machine Learning analysis and prediction.

### 2. Data Processing

The data is processed before being provided to the Machine Learning model.

### 3. Machine Learning Model

A trained model is saved as:

```text
model.pkl
```

### 4. Web Application

Flask is used to create the web application and connect the Machine Learning model with the user interface.

### 5. Database

Database-related functionality is included in the project for storing and managing application data.

### 6. Facial Tracking

OpenCV is used for the facial tracking functionality included in the project.

---

# 📊 Results and Visualization

The repository contains visualizations used during the Machine Learning analysis.

These include:

- Confusion Matrix
- Feature Importance

The generated visualizations are available as:

```text
confusion_matrix.png
feature_importance.png
```

---

# 🔮 Future Improvements

The project can be improved in the future by:

- Improving the Machine Learning model.
- Increasing the size and quality of the dataset.
- Trying different Machine Learning algorithms.
- Performing hyperparameter tuning.
- Improving prediction performance.
- Improving the user interface.
- Adding additional features to the web application.
- Improving facial tracking functionality.
- Deploying the Flask application online.
- Adding real-time prediction functionality.

---

# ⚠️ Disclaimer

This project is developed for educational and research purposes only.

The prediction provided by this application should **not** be considered a medical diagnosis.

For medical assessment, diagnosis, or treatment, users should consult a qualified healthcare professional.

---

# 👨‍💻 Author

**Shubhadip Pal**

GitHub:

https://github.com/Shubhapal6666

---

# 📜 License

This project is created for educational purposes.

# All-In-One Android App

This is a Python-based Android application built with the Kivy framework. It provides a simple interface for managing daily reminders and bookings, with all data stored securely in a Google Firebase backend.

## Getting Started

Follow these instructions to get the application running on your local machine for development and testing.

### Prerequisites

- Python 3.6+
- Pip (Python package installer)
- A Google Firebase project

### Installation and Setup

1.  **Clone the Repository:**
    ```bash
    git clone <repository_url>
    cd android_app
    ```

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Firebase Credentials:**
    - In your Firebase project console, go to **Project settings** > **General**.
    - Under **Your apps**, find your **Web API Key** and your **Project ID**.
    - Create a new file named `config.py` in the `android_app` directory.
    - Copy the contents of `config.py.example` into your new `config.py` file.
    - Replace the placeholder values for `API_KEY` and `PROJECT_ID` with your actual Firebase credentials.

4.  **Run the Application:**
    ```bash
    python main.py
    ```

### Building for Android

To compile the application into an Android APK, you will need to have [Buildozer](https://buildozer.readthedocs.io/en/latest/installation.html) installed.

Once Buildozer is set up, you can run the following command from the `android_app` directory:
```bash
buildozer android debug
```

This will generate an APK file in the `bin` directory.

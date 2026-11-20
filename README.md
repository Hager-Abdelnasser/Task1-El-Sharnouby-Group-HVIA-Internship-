El-Sharnouby Group Dashboard

An interactive web application built with Streamlit for data preparation, processing, and visualization.

Note: Update the title and project overview above to reflect the specific dataset or domain of your application.

Project Structure

├── .streamlit/          # Streamlit configuration files
├── data/                # Raw and processed datasets
├── app.py               # Main Streamlit application entry point
├── data.py              # Data loading and handling utilities
├── prep.py              # Data cleaning and preparation logic
├── theme.py             # Custom UI styling and theme configuration
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation


Features

Modular Architecture: Separates data loading (data.py), preprocessing (prep.py), UI styling (theme.py), and the main interface (app.py).

Interactive Interface: Built with Streamlit for responsive exploration and visualization.

Custom Theme: Dedicated theme and configuration settings via theme.py and .streamlit/.

Getting Started

Prerequisites

Python 3.8 or higher

pip package manager

Installation

Clone the repository:

git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name


Create and activate a virtual environment (recommended):

python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate


Install dependencies:

pip install -r requirements.txt


Running the App

Launch the Streamlit application locally:

streamlit run app.py


Cleanup Checklist (Before Pushing to GitHub)

To keep your repository clean, make sure to remove or ignore temporary and duplicate files shown in your local folder:

Remove Source.py (not part of this project).

Delete duplicate copies: prep - Copy.py, README - Copy.md, requirements - Copy.txt.

Remove or move the local screen recording (Screen Recording 2026-11-20 221307.mp4).

Add __pycache__/ to your .gitignore file.

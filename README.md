Lab Genie
Python
Flask
SQLite
Gemini API
License
Lab Genie is a web-based application designed to streamline the creation, management, and export of laboratory records. Built with Flask, SQLite, and integrated with the Gemini API, it allows users to input lab data, generate detailed records, and export them as .docx or .pdf files. The application features a user-friendly interface styled with Tailwind CSS and client-side interactivity powered by JavaScript.
Features
Record Creation: Input lab experiment details via a form and generate structured records using the Gemini API.

Database Management: Store and manage lab records in an SQLite database.

Export Options: Export records as .docx or .pdf files for easy sharing and documentation.

Dashboard: View, search, and manage all lab records in a centralized dashboard.

Responsive UI: Modern, responsive design with Tailwind CSS for a seamless experience across devices.

Client-Side Interactivity: Dynamic form validation and UI enhancements using JavaScript.

Project Structure

LabGenie/
├── app.py                  # Flask application with routes and logic
├── database.py             # SQLite database operations (create, read, update, delete)
├── gemini_api.py           # Integration with Gemini API for record generation
├── export_utils.py         # Functions for exporting records to .docx and .pdf
├── static/
│   ├── css/
│   │   └── styles.css     # Tailwind CSS or custom styles
│   └── js/
│       └── script.js      # Client-side JavaScript for interactivity
├── templates/
│   ├── index.html         # Home page with input form
│   ├── dashboard.html     # Dashboard for viewing and managing records
│   └── record.html        # View individual record details
├── requirements.txt        # Python dependencies
└── records/               # Folder for exported .docx and .pdf files

Prerequisites
Python 3.8 or higher

SQLite (included with Python)

Gemini API key (obtain from Gemini API provider)

Basic knowledge of Flask and web development

Installation
Clone the Repository:
bash

git clone https://github.com/yourusername/lab-genie.git
cd lab-genie

Create a Virtual Environment:
bash

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

Install Dependencies:
bash

pip install -r requirements.txt

Set Up Environment Variables:
Create a .env file in the project root and add your Gemini API key:
bash

GEMINI_API_KEY=your_gemini_api_key

Initialize the Database:
Run the following command to set up the SQLite database:
bash

python database.py

Run the Application:
Start the Flask development server:
bash

python app.py

Open your browser and navigate to http://localhost:5000.

Usage
Home Page (index.html):
Access the home page to fill out the lab record form.

Submit experiment details (e.g., title, date, observations, results).

The Gemini API processes the input to generate a structured record.

Dashboard (dashboard.html):
View a list of all saved lab records.

Search or filter records by title, date, or other criteria.

Click on a record to view its details or export it.

Record Details (record.html):
View a single record’s details.

Export the record as a .docx or .pdf file, saved to the records/ folder.

Exporting Records:
Use the export buttons on the record or dashboard page to download records in your preferred format.

Dependencies
Key dependencies listed in requirements.txt:
Flask: Web framework for Python

python-dotenv: For loading environment variables

python-docx: For generating .docx files

reportlab or PyPDF2: For generating or manipulating .pdf files

requests: For Gemini API HTTP requests

sqlite3: For database operations (included with Python)

Install all dependencies using:
bash

pip install -r requirements.txt

Configuration
Gemini API: Ensure your API key is valid and has sufficient quota. Update the key in the .env file.

Database: The SQLite database file (lab_genie.db) is created automatically in the project root.

Export Folder: Ensure the records/ folder has write permissions for saving exported files.

Contributing
Contributions are welcome! To contribute:
Fork the repository.

Create a new branch (git checkout -b feature/your-feature).

Make your changes and commit (git commit -m "Add your feature").

Push to the branch (git push origin feature/your-feature).

Open a Pull Request.

Please ensure your code follows PEP 8 guidelines and includes relevant tests.
License
This project is licensed under the MIT License. See the LICENSE file for details.


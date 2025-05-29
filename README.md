# Flask Roller Coasters App

This project is a Flask web application that displays a list of roller coasters. The data is read from an Excel file (`coasters_info.xlsx`) and presented in a user-friendly format. Users can dynamically reorder the list of roller coasters using a drag-and-drop feature.

## Project Structure

```
flask-rollercoasters-app
├── app.py                # Main entry point of the Flask application
├── coasters_info.xlsx    # Excel file containing roller coaster data
├── requirements.txt      # Lists project dependencies
├── templates
│   └── index.html        # HTML template for displaying roller coasters
└── README.md             # Project documentation
```

## Setup Instructions

1. **Clone the repository** (if applicable):
   ```
   git clone <repository-url>
   cd captain-coaster
   ```

2. **Create a virtual environment** (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install the required dependencies**:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. **Run the Flask application**:
   ```
   python app.py
   ```

2. **Access the application**:
   Open your web browser and go to `http://localhost:5000` to view the list of roller coasters.

## Features

- Displays a list of roller coasters from the Excel file.
- Allows users to reorder the list using a drag-and-drop interface.

## Contributing

Feel free to submit issues or pull requests for improvements or bug fixes.

SchedulForge Backend
====================

Project: SchedulForge — A Full-Stack Intelligent Scheduling Data Parsing and Structuring System

This backend service is built using FastAPI to process complex Excel timetable data and provide clean, structured JSON for frontend visualization.

Author: Manas Mahawar
Institution: Thapar Institute of Engineering and Technology, Patiala
Internship: DEAL, DRDO, Dehradun

----------------------------------------------------------------------
Technologies & Libraries
- Python
- FastAPI
- Uvicorn
- openpyxl
- pandas
- python-multipart
- pydantic

----------------------------------------------------------------------
Key Endpoints (documented at /docs)
- /list_sheets/  
  Lists sheet names in the uploaded Excel file.

- /list_tutorial_groups/  
  Detects and lists tutorial groups based on the uploaded Excel sheet.

- /timetable/  
  Parses and returns structured timetable data as JSON.

----------------------------------------------------------------------
How it works
- Accepts Excel files uploaded by the user.
- Uses openpyxl and custom pattern-matching algorithms to:
  • Traverse large datasets
  • Handle merged cells
  • Detect tutorial groups in dynamic rows
  • Generate structured JSON
- Returns data to the frontend for rendering and PDF export.

----------------------------------------------------------------------
Deployment
- Hosted on Render cloud platform.
- Live API: https://schedulforge-backend-euv7.onrender.com
- Interactive API docs: https://schedulforge-backend-euv7.onrender.com/docs#/

----------------------------------------------------------------------
Related Links
Frontend (GitHub Pages): https://manas-mahawar.github.io/SchedulForge/
GitHub Repository: https://github.com/manas-mahawar/SchedulForge

----------------------------------------------------------------------

For details on the full project workflow, see the main README.md in the root folder.

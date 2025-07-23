# SchedulForge

SchedulForge is a full-stack intelligent scheduling data parsing and structuring system.  
It automates extraction and visualization of complex academic timetable data from large, inconsistently formatted Excel sheets—saving students time and effort.

---

## Live Project
- Frontend Demo: [SchedulForge on GitHub Pages](https://manas-mahawar.github.io/SchedulForge/)
- Backend API: [Render Backend](https://schedulforge-backend-euv7.onrender.com)
- API Docs (Swagger UI): [View API Documentation](https://schedulforge-backend-euv7.onrender.com/docs#/)
- Source Code: [GitHub Repository](https://github.com/manas-mahawar/SchedulForge)

---

## Technologies Used
**Backend:** Python, FastAPI, Uvicorn, openpyxl, pandas, python-multipart, pydantic  
**Frontend:** HTML, CSS, JavaScript (Fetch API, DOM manipulation)  
**Deployment & Tools:** Render, GitHub Pages, Swagger UI, Git & GitHub

---

## Key Features
- Detects tutorial groups and handles irregular Excel formatting.
- Processes merged cells and cleans raw data into structured JSON.
- FastAPI endpoints with live Swagger documentation.
- Light/dark mode toggle and PDF download in frontend.
- Loading spinner shows real-time processing status.

---

## How It Works
1. User uploads an Excel timetable file.
2. Backend processes file with custom logic (regex, pattern matching, merged cell handling).
3. Clean JSON is returned to frontend.
4. Frontend renders structured timetable and allows PDF export.

---

## Future Scope
- OCR integration to read scanned PDFs or images.
- Database storage for timetables and analytics.
- Free slot visualization and conflict detection.
- Personalized user dashboards and authentication.
- Mobile-first or PWA version.
- Extended API or migration to GraphQL.

---

## Documentation & References
- [FastAPI](https://fastapi.tiangolo.com/)
- [openpyxl](https://openpyxl.readthedocs.io/)
- [Pandas](https://pandas.pydata.org/)
- [Uvicorn](https://www.uvicorn.org/)
- [python-multipart](https://andrew-d.github.io/python-multipart/)
- [Swagger UI](https://swagger.io/tools/swagger-ui/)
- [Render](https://render.com/)
- [GitHub Pages](https://pages.github.com/)
- [JavaScript (MDN)](https://developer.mozilla.org/)
- [Git & GitHub Docs](https://docs.github.com/)
- Academic Excel timetables from Thapar Institute of Engineering & Technology, Patiala (used as dataset samples).

---

## License
Developed during summer internship at Defence Electronics Applications Laboratory (DEAL), DRDO, Dehradun.  
Open for academic and learning use.

---

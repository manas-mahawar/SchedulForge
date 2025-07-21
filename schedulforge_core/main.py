from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import openpyxl
import tempfile
import os
import re

app = FastAPI()

# Allow frontend to access backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with actual frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Timetable API running!"}


@app.post("/uploadfile/")
async def upload_file(
    file: UploadFile,
    sheet_choice: str = Form(...),
    tutorial_group: str = Form(...)
):
    try:
        # Save uploaded file temporarily
        suffix = file.filename.split('.')[-1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{suffix}") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        # Load workbook and sheet
        wb = openpyxl.load_workbook(tmp_path, data_only=True)
        if sheet_choice not in wb.sheetnames:
            return JSONResponse(content={"error": "Sheet not found!"}, status_code=400)
        ws = wb[sheet_choice]

        group = tutorial_group.strip().upper()

        timetable = {}
        start_row = 8  # first row of actual data (time slots)
        rows_per_day = 28
        time_slots = ['08:50 AM', '09:40 AM', '10:30 AM', '11:20 AM', '12:10 PM',
                      '01:00 PM', '01:50 PM', '02:40 PM', '03:30 PM', '04:20 PM', '05:10 PM', '06:00 PM', '06:50 PM', '07:40 PM']
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

        for day_index, day in enumerate(days):
            base_row = start_row + day_index * rows_per_day
            timetable[day] = {'Course': [], 'Time': []}

            for i in range(0, rows_per_day, 2):
                row = base_row + i
                found = False
                for col in range(3, ws.max_column + 1):  # Skip first two columns (day & time)
                    cell_value = ws.cell(row=row, column=col).value
                    if cell_value and group in str(cell_value).upper():
                        cell_above = ws.cell(row=row - 1, column=col).value
                        if not cell_above or group in str(cell_above).upper():
                            content = str(cell_value).strip()
                            # Extract course and room using regex (before faculty name)
                            match = re.search(r'([A-Z]{2,}\d{3,}[A-Z]?(?:\s?[PL])?).*?([A-Z]+-\d+)', content)
                            course = match.group(1) if match else content
                            timetable[day]['Course'].append(course)
                            slot_index = i // 2
                            if slot_index < len(time_slots):
                                timetable[day]['Time'].append(time_slots[slot_index])
                            else:
                                timetable[day]['Time'].append("Unknown")
                            found = True
                            break
                if not found:
                    continue

        os.remove(tmp_path)
        return timetable

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

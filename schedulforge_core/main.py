import os
import tempfile
import re
import openpyxl
from openpyxl.utils import get_column_letter
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()

# Enable CORS for your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://manas-mahawar.github.io"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Regex for course codes like ABC123 L / ABC123 T / ABC123 P
course_pattern = re.compile(r"[A-Z]{3}\d{3}\s+[LPT]")

wb = None  # Global workbook variable


def save_temp_file(upload: UploadFile) -> str:
    """Save uploaded file to a secure temp path and return its filename"""
    suffix = os.path.splitext(upload.filename)[-1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(upload.file.read())
        return tmp.name


@app.get("/")
def root():
    return {"message": "Unified timetable API running."}


@app.post("/list_sheets/")
async def list_sheets(file: UploadFile = File(...)):
    global wb
    temp_path = save_temp_file(file)
    wb = openpyxl.load_workbook(temp_path)

    sheet_infos = [
        {"index": idx+1, "name": name.strip()}
        for idx, name in enumerate(wb.sheetnames)
        if name.strip().upper() != "PG TIME TABLE"
    ]
    return {"sheets": sheet_infos}


@app.post("/list_tutorial_groups/")
async def list_tutorial_groups(
    file: UploadFile = File(...),
    sheet_choice: int = Form(...)
):
    global wb
    # Use already loaded workbook in memory

    sheet_infos = [
        (idx+1, name.strip(), name)
        for idx, name in enumerate(wb.sheetnames)
        if name.strip().upper() != "PG TIME TABLE"
    ]
    selected = next((o_name for idx, s_name, o_name in sheet_infos if idx == sheet_choice), None)
    if not selected:
        return JSONResponse(content={"error": "Invalid sheet_choice"}, status_code=400)

    sheet = wb[selected]
    sheet_name_upper = sheet.title.strip().upper()

    # Determine header row
    if sheet_name_upper == "1ST YEAR A":
        header_row = 4
    elif sheet_name_upper == "1ST YEAR B":
        header_row = 6
    else:
        header_row = 5

    # Extract tutorial groups
    groups = []
    for col in range(1, sheet.max_column + 1):
        val = sheet.cell(row=header_row, column=col).value
        if val and str(val).strip().upper() != "DAY":
            groups.append(str(val).strip())

    return {"tutorial_groups": groups}


@app.post("/timetable/")
async def get_timetable(
    file: UploadFile = File(...),
    sheet_choice: int = Form(...),
    tutorial_group: str = Form(...)
):
    global wb
    # Use already loaded workbook in memory

    sheet_infos = [
        (idx+1, name.strip(), name)
        for idx, name in enumerate(wb.sheetnames)
        if name.strip().upper() != "PG TIME TABLE"
    ]
    selected = next((o_name for idx, s_name, o_name in sheet_infos if idx == sheet_choice), None)
    if not selected:
        return JSONResponse(content={"error": "Invalid sheet_choice"}, status_code=400)

    sheet = wb[selected]
    sheet_name_upper = sheet.title.strip().upper()

    # Determine header & start rows
    if sheet_name_upper == "1ST YEAR A":
        header_row, start_row = 4, 7
    elif sheet_name_upper == "1ST YEAR B":
        header_row, start_row = 6, 9
    else:
        header_row, start_row = 5, 8

    # Find column for tutorial group
    group_column = None
    for col in range(1, sheet.max_column + 1):
        val = sheet.cell(row=header_row, column=col).value
        if val and str(val).strip() == tutorial_group:
            group_column = col
            break
    if not group_column:
        return JSONResponse(content={"error": f"Tutorial group '{tutorial_group}' not found."}, status_code=404)

    # Time slots & day mappings
    time_slots = [
        "08:00 AM", "08:50 AM", "09:40 AM", "10:30 AM", "11:20 AM", "12:10 PM",
        "01:00 PM", "01:50 PM", "02:40 PM", "03:30 PM", "04:20 PM", "05:10 PM",
        "06:00 PM", "06:50 PM"
    ]
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    row_to_day_time = {}
    for day_idx, day in enumerate(days):
        for slot_idx, time in enumerate(time_slots):
            row_idx = start_row + day_idx * 28 + slot_idx * 2
            row_to_day_time[row_idx] = (day, time)

    timetable = {day: {} for day in days}
    processed_merged = set()

    for row in range(start_row, start_row + 28 * len(days)):
        cell = sheet.cell(row=row, column=group_column)
        coord = f"{get_column_letter(group_column)}{row}"
        subject_row = row

        for merged in sheet.merged_cells.ranges:
            if coord in merged:
                top_left = (merged.min_row, merged.min_col)
                if top_left not in processed_merged:
                    subject = sheet.cell(*top_left).value
                    subject_row = merged.min_row
                    processed_merged.add(top_left)
                    break
                else:
                    subject = None
                    break
        else:
            subject = cell.value

        if not subject:
            continue

        subject_str = str(subject).strip().upper()
        if subject_str == tutorial_group.upper() or subject_str == "DAY":
            continue

        match = course_pattern.search(subject_str)
        if not match:
            continue

        course_code = match.group(0)
        if subject_row in row_to_day_time:
            day, time_str = row_to_day_time[subject_row]
            timetable[day][time_str] = course_code

    return {
        "sheet_name": sheet.title,
        "tutorial_group": tutorial_group,
        "time_slots": time_slots,
        "timetable": timetable
    }

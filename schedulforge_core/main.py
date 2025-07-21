from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import openpyxl
import re
from openpyxl.utils import get_column_letter

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://manas-mahawar.github.io"],  # restrict to your frontend
    allow_methods=["*"],
    allow_headers=["*"]
)

course_pattern = re.compile(r"[A-Z]{3}\d{3}\s+[LPT]")

@app.get("/")
def root():
    return {"message": "Unified timetable API running."}

@app.post("/timetable/")
async def unified_timetable(
    file: UploadFile = File(...),
    sheet_choice: int = Form(...),
    tutorial_group: str = Form(...)
):
    try:
        contents = await file.read()
        temp_path = f"/tmp/{file.filename}"
        with open(temp_path, "wb") as f:
            f.write(contents)

        wb = openpyxl.load_workbook(temp_path)

        # Filter out 'PG TIME TABLE'
        valid_sheets = [
            (idx + 1, name.strip(), name)
            for idx, name in enumerate(wb.sheetnames)
            if name.strip().upper() != "PG TIME TABLE"
        ]
        selected = next((o_name for idx, s_name, o_name in valid_sheets if idx == sheet_choice), None)
        if not selected:
            return JSONResponse(content={"error": "Invalid sheet_choice"}, status_code=400)

        sheet = wb[selected]
        sheet_name_upper = sheet.title.strip().upper()

        # Determine header & start row
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

        # Prepare time & row mappings
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

        # Extract timetable
        timetable = {day: {} for day in days}
        seen_merged = set()

        for row in range(start_row, start_row + 28 * len(days)):
            cell = sheet.cell(row=row, column=group_column)
            coord = f"{get_column_letter(group_column)}{row}"
            subject_row = row

            for merged in sheet.merged_cells.ranges:
                if coord in merged:
                    top_left = (merged.min_row, merged.min_col)
                    if top_left not in seen_merged:
                        subject = sheet.cell(*top_left).value
                        subject_row = merged.min_row
                        seen_merged.add(top_left)
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

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

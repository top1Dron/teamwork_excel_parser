from fastapi import FastAPI, UploadFile, File
from starlette.responses import FileResponse

from xlsc_parser import TeamworkExcelParser

app = FastAPI()


@app.post("/create_report/")
async def root(response_file_name: str, file: UploadFile = File(...)):
    new_excel_format = TeamworkExcelParser(file, response_file_name).get_valid_format()
    headers = {'Content-Disposition': f'attachment; filename="{response_file_name}"'}
    if not response_file_name.endswith(".xlsx"):
        response_file_name = response_file_name + ".xlsx"
    return FileResponse(response_file_name, headers=headers)

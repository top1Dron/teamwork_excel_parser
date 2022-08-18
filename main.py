from fastapi import FastAPI, UploadFile, File
from fastapi.exceptions import HTTPException
from fastapi.responses import StreamingResponse

from xlsx_parser import TeamworkExcelParser

app = FastAPI()


@app.post("/create_report/")
async def root(response_file_name: str, file: UploadFile = File(...)):
    print(file.content_type)
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(400, detail="Invalid document type")
    if not response_file_name.endswith(".xlsx"):
        response_file_name = response_file_name + ".xlsx"
    new_excel_file = TeamworkExcelParser(file, response_file_name).get_valid_format()
    headers = {'Content-Disposition': f'attachment; filename="{response_file_name}"'}
    return StreamingResponse(iter([new_excel_file.getvalue()]), headers=headers)

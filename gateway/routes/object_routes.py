from fastapi import APIRouter, UploadFile, File
from fastapi.responses import Response

from gateway.services.storage_service import (
    upload_file,
    list_files,
    download_file
)

from gateway.services.telemetry_service import (
    record_object_download,
    record_object_access
)


router = APIRouter()


@router.post("/upload")
async def upload(file: UploadFile = File(...)):

    result = upload_file(
        file.file,
        file.filename,
        file.content_type
    )

    return result


@router.get("/files")
async def get_files():

    return list_files()


@router.get("/download/{filename}")
async def download(filename: str):
    file_data = download_file(filename)
    record_object_download(filename)
    record_object_access(filename)

    return Response(
        content=file_data,
        media_type="application/octet-stream"
    )
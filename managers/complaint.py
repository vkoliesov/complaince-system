import os
import uuid

from constants import TEMP_FILE_FOLDER
from models import Complaint, RoleType, State
from db import database
from services.s3 import S3Service
from utils.helpers import decode_photo


complaints = Complaint.metadata.tables.get("complaints")
s3 = S3Service()


class ComplaintManager:
    @staticmethod
    async def get_complaints(user):
        q = complaints.select()
        if user["role"] == RoleType.complainer:
            q = q.where(complaints.c.complainer_id == user["id"])
        elif user["role"] == RoleType.approver:
            q = q.where(complaints.c.state == State.pending)
        return await database.fetch_all(q)

    @staticmethod
    async def create_complaint(complaint_data, user):
        complaint_data["complainer_id"] = user["id"]

        encoded_photo = complaint_data.pop("encoded_photo")
        extension = complaint_data.pop("extension")
        name = f"{uuid.uuid4()}.{extension}"
        path = os.path.join(TEMP_FILE_FOLDER, name)
        decode_photo(path, encoded_photo)
        complaint_data["photo_url"] = s3.upload(path, name, extension)

        id_ = await database.execute(complaints.insert().values(**complaint_data))
        return await database.fetch_one(
            complaints.select().where(complaints.c.id == id_)
        )

    @staticmethod
    async def delete_complaint(complaint_id: int):
        await database.execute(
            complaints.delete().where(complaints.c.id == complaint_id)
        )

    @staticmethod
    async def approve_complaint(complaint_id: int):
        await database.execute(
            complaints.update()
            .where(complaints.c.id == complaint_id)
            .values(status=State.approved)
        )

    @staticmethod
    async def reject_complaint(complaint_id: int):
        await database.execute(
            complaints.update()
            .where(complaints.c.id == complaint_id)
            .values(status=State.rejected)
        )

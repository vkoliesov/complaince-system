from models import Complaint, RoleType, State
from db import database


complaints = Complaint.metadata.tables.get("complaints")

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
        id_ = await database.execute(complaints.insert().values(**complaint_data))
        return await database.fetch_one(complaints.select().where(complaints.c.id == id_))

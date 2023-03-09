import os
import uuid

from constants import TEMP_FILE_FOLDER
from models import Complaint, RoleType, State, Transaction
from db import database
from services.s3 import S3Service
from services.ses import SESService
from services.wise import WiseService
from utils.helpers import decode_photo


complaints = Complaint.metadata.tables.get("complaints")
transactions = Transaction.metadata.tables.get("transactions")
s3 = S3Service()
ses = SESService()


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
        os.remove(path)
        id_ = await database.execute(complaints.insert().values(**complaint_data))
        await ComplaintManager.issue_transaction(
            amount=complaint_data["amount"],
            full_name=f"{user['first_name']} {user['last_name']}",
            iban=user["iban"],
            complaint_id=id_
        )
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
            .values(state=State.approved)
        )
        transaction_data = await database.fetch_one(transactions.select().where(transactions.c.complaint_id == complaint_id))
        wise = WiseService()
        wise.fund_transfer(transfer_id=transaction_data["transfer_id"])
        ses.send_mail(
            "Complaint approved!",
            ["kolesov0703@gmail.com"],
            "Congrats! Your claim is approved, check your bank account in 2 days for your refund"
        )

    @staticmethod
    async def reject_complaint(complaint_id: int):
        await database.execute(
            complaints.update()
            .where(complaints.c.id == complaint_id)
            .values(state=State.rejected)
        )
        transaction_data = await database.fetch_one(transactions.select().where(transactions.c.complaint_id == complaint_id))
        wise = WiseService()
        wise.cancel_fund(transfer_id=transaction_data["transfer_id"])

    @staticmethod
    async def issue_transaction(amount, full_name, iban, complaint_id):
        wise = WiseService()
        quote_id = wise.create_quote(amount=amount)
        recipeint_id = wise.create_recipient_account(
            full_name=full_name,
            iban=iban
        )
        transfer_id = wise.create_transfer(
            target_account_id=recipeint_id,
            quote_id=quote_id
        )
        data = {
            "quote_id": quote_id,
            "transfer_id": transfer_id,
            "target_account_id": str(recipeint_id),
            "amount": amount,
            "complaint_id": complaint_id
        }

        await database.execute(transactions.insert().values(**data))

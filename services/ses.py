import boto3
from decouple import config


class SESService:
    def __init__(self):
        self.key = config("AWS_ACCESS_KEY")
        self.secret_key = config("AWS_SECRET")
        self.ses = boto3.client(
            "ses",
            region_name=config("SES_REGION"),
            aws_access_key_id=self.key,
            aws_secret_access_key=self.secret_key
        )

    def send_mail(self, subject, to_addresses, text_data):
        body = {"Text": {"Data": text_data, "Charset": "UTF-8"}}

        self.ses.send_email(Source=config("SES_SYSTEM_EMAIL"),
                            Destination={"ToAddresses": to_addresses,
                                        "CcAddresses": [],
                                        "BccAddresses": []},
                            Message={"Subject": {"Data": subject, "Charset": "UTF-8"}, "Body": body},
                            )

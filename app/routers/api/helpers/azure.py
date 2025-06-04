import base64
import re
from datetime import datetime

from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import DocumentAnalysisFeature
from azure.ai.documentintelligence.models import AnalyzeResult
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest

from app.config import settings


def analyze_id_barcodes(img_base64):

    AZURE_ENDPOINT = settings.azure_endpoint
    AZURE_KEY_1 = settings.azure_key_1

    document_intelligence_client = DocumentIntelligenceClient(endpoint=AZURE_ENDPOINT,
                                                              credential=AzureKeyCredential(AZURE_KEY_1))

    poller = document_intelligence_client.begin_analyze_document(
        "prebuilt-read",
        AnalyzeDocumentRequest(bytes_source=base64.b64decode(img_base64)),
        features=[DocumentAnalysisFeature.BARCODES]
    )

    result: AnalyzeResult = poller.result()

    id_data = dict()

    for page in result.pages:
        if page.barcodes:
            for barcode_idx, barcode in enumerate(page.barcodes):
                if barcode.kind == 'PDF417':
                    id_data['barcode_value'] = barcode.value
                    id_data['barcode_kind'] = barcode.kind
                    id_data['barcode_confidence'] = barcode.confidence
                    id_data['barcode_polygon'] = barcode.polygon

    return id_data['barcode_value']


def parse_barcode_data(barcode_data):
    """
    Parses AAMVA driver's license/ID data and returns a dictionary of key-value pairs.
    """
    # Remove control characters
    clean_data = barcode_data.replace('<LF>', '\n').replace('<RS>', '').replace('<CR>', '')

    id_data = dict()

    # AAMVA key definitions
    aamva_keys = {
        "DAQ": "id_number",
        "DCS": "last_name",
        "DAC": "first_name",
        "DAD": "middle_name",
        "DAG": "address1",
        "DAI": "city",
        "DAJ": "state",
        "DAK": "zip",
        "DBD": "issue_date",
        "DBB": "date_of_birth",
        "DBA": "expiration_date",
        "DBC": "sex",
        "DAU": "height",
        "DAY": "eye_color",
        "DCG": "country",
        "DCF": "unique_identifier",
        "DDB": "last_update_date",
        "DCA": "id_type",
        "DCB": "restrictions",
        "DCD": "endorsements"
    }

    sex_mapping = {
        "1": "male",
        "2": "female"
    }

    capitalize_fields = [
        "last_name",
        "first_name",
        "middle_name",
        "address1",
        "city",
    ]

    # Ensure `DAQ` is correctly parsed
    match = re.search(r'DAQ([^\n\r]+)', clean_data)
    if match:
        id_data["id_number"] = match.group(1).strip()

    # Split the data into individual lines
    lines = clean_data.split('\n')

    for line in lines:
        for key, description in aamva_keys.items():
            if line.startswith(key) and description != "id_number":  # Skip DAQ (already captured)
                value = line[len(key):].strip()

                # Handle "NONE" values
                if value == "NONE":
                    value = None

                # Handle sex
                if description == "sex":
                    value = sex_mapping.get(value, value)

                # Handle ZIP code
                if description == "zip":
                    value = value[:5].lstrip("0")

                # Handle date fields
                if description in ["issue_date", "date_of_birth", "expiration_date", "last_update_date"]:
                    value = re.sub(r'[^0-9]', '', value)
                    date = datetime.strptime(value, "%m%d%Y")
                    value = date.strftime("%Y-%m-%d")

                # Handle height
                if description == "height":
                    if value.endswith("IN"):
                        id_data["height_units"] = "imperial"
                        value = value[:-2].strip()
                    elif value.endswith("CM"):
                        id_data["height_units"] = "metric"
                        value = value[:-2].strip()

                # Capitalize necessary fields
                if description in capitalize_fields and value:
                    value = value.title()

                id_data[description] = value

    return id_data

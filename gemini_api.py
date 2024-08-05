# gemini_utils.py
from googleapiclient.http import MediaIoBaseUpload
from google.colab import userdata
import google.generativeai as genai
from PIL import Image
from io import BytesIO

# Configure Gemini API
genai.configure(api_key=GOOGLE_API_KEY)

MODEL_CONFIG = {
    "temperature": 0.2,
    "top_p": 1,
    "top_k": 32,
    "max_output_tokens": 4096,
}

SAFETY_SETTINGS = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
]

model = genai.GenerativeModel(model_name="gemini-1.5-flash", generation_config=MODEL_CONFIG, safety_settings=SAFETY_SETTINGS)

def image_format(image):
    with BytesIO() as output:
        image.save(output, format="JPEG")
        image_data = output.getvalue()
    return [{"mime_type": "image/jpeg", "data": image_data}]

def gemini_output(image, system_prompt, user_prompt):
    image_info = image_format(image)
    input_prompt = [system_prompt, image_info[0], user_prompt]
    response = model.generate_content(input_prompt)
    return response.text

def convert_pdf_to_jpeg_in_memory(pdf_data, dpi=200):
    """Mengonversi PDF menjadi gambar JPEG dalam memori.

    Args:
        pdf_data (bytes): Data file PDF.
        dpi (int, optional): Resolusi gambar (dots per inch). Default adalah 200.
    """
    images = convert_from_bytes(pdf_data, dpi=dpi)
    return images

SYSTEM_PROMPT = """
    You are an expert at extracting information from receipts. You will be given an image of a receipt.
    Extract the following information from the receipt:
    - Invoice Number
    - Bill to
    - Date
    - Due Date (if available)
    - Total
    If a piece of information is not found on the receipt, indicate that it is "Not Found".
    Return the extracted information in a structured JSON format.
"""

USER_PROMPT = "Extract information from the attached receipt."

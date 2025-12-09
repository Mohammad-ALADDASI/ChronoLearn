# app.py
import os
import json
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import PyPDF2
from openai import OpenAI
from dotenv import load_dotenv

from visualise import load_all_entities, build_graph, visualize_graph 
# -----------------------------------
# Load environment variables
# -----------------------------------
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("❌ OPENAI_API_KEY not found in .env file!")

client = OpenAI(api_key=OPENAI_API_KEY)

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
ENTITIES_FOLDER = "entities"

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
os.makedirs(ENTITIES_FOLDER, exist_ok=True)

# -----------------------------------
# Extract text from Arabic PDF
# -----------------------------------
def extract_pdf_text(pdf_path):
    text = ""
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
    return text.strip()

# -----------------------------------
# Call ChatGPT for NER
# -----------------------------------
def run_ner_extraction(pdf_text, user_prompt=None):
    if not user_prompt:
        user_prompt = (
    "أريد منك استخراج كافّة الكيانات والعلاقات لبناء مخطط معرفة (Knowledge Graph) "
    "من النص التالي. يجب أن يكون الإخراج بصيغة JSON فقط، دون أي شرح إضافي.\n\n"
    "التزم بدقة بالمفاتيح التالية فقط:\n"
    "1. \"أشخاص\": قائمة بالأسماء البشرية المذكورة صراحة في النص.\n"
    "2. \"أماكن\": قائمة بالأماكن الجغرافية الواضحة.\n"
    "3. \"منظمات\": جميع الكيانات المؤسسية (جيش، حكومة، حركة… إلخ).\n"
    "4. \"تواريخ\": أي تاريخ مذكور صراحة.\n"
    "5. \"أحداث\": الأحداث التاريخية أو السياسية أو العسكرية المذكورة.\n"
    "6. \"Relations\": قائمة من العلاقات بين العناصر وفق الأنماط التالية فقط:\n"
    "   - إذا ذُكر ارتباط شخص بمكان → استخدم: \"type\": \"مرتبط بـ المكان\"\n"
    "   - إذا ذُكر ارتباط شخص بمنظمة → \"type\": \"مرتبط بـ المنظمة\"\n"
    "   - إذا وقع حدث في مكان → \"type\": \"حدث في\"\n"
    "   - إذا كان شخص مرتبطاً بحدث → \"type\": \"متعلق بـ الحدث\"\n"
    "   - إذا شاركت منظمة في حدث → \"type\": \"شارك في\"\n\n"
    "صيغة كل علاقة كالتالي:\n"
    "{ \"source\": \"...\", \"target\": \"...\", \"type\": \"...\" }\n\n"
    "ملاحظة مهمة:\n"
    "- يجب استخراج العلاقات فقط إذا وردت صراحة في النص، ولا يُسمح بالتوقع أو الاجتهاد.\n"
    "- يجب أن يكون الناتج JSON صالحًا 100% ويمكن قراءته مباشرة من طرف البرنامج.\n\n"
    "أعد الإجابة بصيغة JSON فقط دون أي نص خارج JSON."
      )

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": "You are an expert NER and knowledge graph extractor."},
            {"role": "user", "content": f"النص:\n{pdf_text}\n\nالتعليمات:\n{user_prompt}"}
        ]
    )

    return response.choices[0].message.content


# -----------------------------------
# Route 1: Upload PDF and extract NER
# -----------------------------------
@app.route("/extract_kg", methods=["POST"])
def extract_kg():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    filename = secure_filename(file.filename)
    pdf_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(pdf_path)

    # Extract
    pdf_text = extract_pdf_text(pdf_path)
    result = run_ner_extraction(pdf_text)

    return jsonify({
        "filename": filename,
        "extracted_text": pdf_text,
        "kg_entities": result
    })


# -----------------------------------
# Route 2: Process ALL PDFs in uploads/
# -----------------------------------
@app.route("/process_all", methods=["GET"])
def process_all():
    processed = []

    for filename in os.listdir(app.config["UPLOAD_FOLDER"]):
        if not filename.lower().endswith(".pdf"):
            continue

        pdf_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        print(f"Processing: {filename}")

        pdf_text = extract_pdf_text(pdf_path)
        entities = run_ner_extraction(pdf_text)

        # Save to entities/ folder
        json_path = os.path.join(ENTITIES_FOLDER, filename.replace(".pdf", ".json"))
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump({"filename": filename, "entities": entities}, f, ensure_ascii=False, indent=2)

        processed.append({"file": filename, "output": json_path})

    return jsonify({
        "status": "Completed batch processing",
        "processed_files": processed
    })



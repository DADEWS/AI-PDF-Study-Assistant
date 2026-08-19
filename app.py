from pathlib import Path
import json
import hashlib


from rag import (
    extract_text_from_pdf,
    split_text,
    create_embedding,
    create_chunk_embeddings,
    save_embeddings,
    load_embeddings,
    cosine_similarity,
    find_relevant_chunks,
    load_summary,
    save_summary,
    summarize_text,
    load_pdf_hash,
    save_pdf_hash,
    create_pdf_hash
)


# AI setup
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("ไม่พบ OPENAI_API_KEY ในไฟล์ .env")
print("พบ API Key")


#PATH
PDF_PATH = Path("data/sample1.pdf")

PDF_NAME = PDF_PATH.stem

EMBEDDINGS_PATH = Path(
    f"data/{PDF_NAME}_embeddings.json"
)

SUMMARY_PATH = Path(
    f"data/{PDF_NAME}_summary.txt"
)

HASH_PATH = Path(
    f"data/{PDF_NAME}_hash.txt"
)

    
# Answer questions based on PDF content
def ask_question(text, question):
    response = client.responses.create(
        model="gpt-5-mini",
        input=f"""
ตอบคำถามโดยใช้เนื้อหาจาก PDF ต่อไปนี้เท่านั้น
หากไม่มีข้อมูลใน PDF ให้ตอบว่า "ไม่พบข้อมูลในเอกสาร"

เนื้อหา PDF:
{text}

คำถาม:
{question}
"""
    )

    return response.output_text

# Main program
if not PDF_PATH.exists():
    print("ไม่พบไฟล์ PDF")
else:
    pdf_text = extract_text_from_pdf(PDF_PATH)
    print("จำนวนตัวอักษร:", len(pdf_text))
    current_pdf_hash = create_pdf_hash(PDF_PATH)

    cache_is_valid = False

    if HASH_PATH.exists():
        saved_pdf_hash = load_pdf_hash(HASH_PATH)

        if current_pdf_hash == saved_pdf_hash:
            cache_is_valid = True
    
    if EMBEDDINGS_PATH.exists() and cache_is_valid:
        print("กำลังโหลด Embeddings ที่บันทึกไว้...")

        chunks, chunk_embeddings = load_embeddings(
            EMBEDDINGS_PATH
        )

    else:
        print("กำลังสร้าง Embeddings ใหม่...")

        chunks = split_text(pdf_text)

        chunk_embeddings = create_chunk_embeddings(chunks)

        save_embeddings(
            chunks,
            chunk_embeddings,
            EMBEDDINGS_PATH
        )

    print("จำนวน Chunks:", len(chunks))
    print("จำนวน Chunk Embeddings:", len(chunk_embeddings))
    print("จำนวนค่าต่อ Embedding:", len(chunk_embeddings[0]))

    if SUMMARY_PATH.exists() and cache_is_valid:
        print("กำลังโหลด Summary ที่บันทึกไว้...")

        summary = load_summary(SUMMARY_PATH)

    else:
        print("กำลังสร้าง Summary ใหม่...")

        summary = summarize_text(pdf_text)

        save_summary(
            summary,
            SUMMARY_PATH
        )
        
    save_pdf_hash(
        current_pdf_hash,
        HASH_PATH
    )

    print("\n===== สรุปจาก AI =====")
    print(summary)
    
    # print("\n===== CHUNK 1 =====")
    # print(chunks[0])

    while True:
        question = input("\nถามคำถามเกี่ยวกับ PDF (พิมพ์ exit เพื่อออก): ")

        if question.lower() == "exit":
            print("จบการถามคำถาม")
            break

        relevant_chunks = find_relevant_chunks(
            question,
            chunks,
            chunk_embeddings
        )

        print("\n===== Relevant Chunks =====")
        
        for score, chunk in relevant_chunks:
            print("Score:", score)
            print(chunk)
            print("--------------------")

        context = ""

        for score, chunk in relevant_chunks:
            context += chunk + "\n\n"

        answer = ask_question(context, question)

        print("\n===== คำตอบจาก AI =====")
        print(answer)
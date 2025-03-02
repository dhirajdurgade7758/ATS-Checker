import pdfplumber
import spacy
import os
from groq import Groq
import json

def extract_text_from_pdf(pdf_path):
    text=""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text.strip()

API_KEY = "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"

def analyze_resume_with_llm(resume_text:str, job_description:str)->dict:
    prompt = f'''
    you are and AI assistant that analyzes resume for software engineering job applications.
    Given resume and job description, extract the following details:

    1. Identify all the skills mentioned in a resume.
    2. Calculate total years of expierence.
    3. Categorize the projects based on domains (e.g AI, Webdevelopment, cloud etc)
    4. Rank the resume relevance to the job description from 0 to 100.

    Resume:
    {resume_text}

    Job Description:
    {job_description}

    provide output in valid JSON format with this structure:
    {{
        "rank" : "<percentage>",
        "skills" : "["skill1", "skill2", "skill3", ......]",
        "total_experience" : "<number of years>",
        "project_category" : "["category1", "category2", ......]",
    }}
'''
    try:
        client = Groq(
            # api_key=os.environ.get("GROQ_API_KEY"),
            api_key=API_KEY
        )

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            response_format={
                "type":"json_object"
            }
        )

        result = chat_completion.choices[0].message.content
        return json.loads(result)
    
    except Exception as e:
        print(e)

def process_resume(pdf_path, job_description):
    try:
        resume_text = extract_text_from_pdf(pdf_path)
        data = analyze_resume_with_llm(resume_text, job_description)
        return data
    except Exception as e:
        print(e)
        return None
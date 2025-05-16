import pdfplumber
import os
from groq import Groq
import json

def extract_text_from_pdf(pdf_path):
    """Extract text content from PDF resume"""
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text.strip()

API_KEY = "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"

class ResumeAssistant:
    def __init__(self):
        self.client = Groq(api_key=API_KEY)
        self.resume_text = ""
        self.conversation_history = []
        
    def load_resume(self, pdf_path):
        """Load and store resume text"""
        self.resume_text = extract_text_from_pdf(pdf_path)

        return True
        
    def chat(self, user_message):
        """
        Process user message and generate AI response
        with context from the loaded resume
        """
        if not self.resume_text:
            return {"error": "Please upload a resume first"}
            
        self._add_user_message(user_message)
        
        prompt = f'''
        You are an AI Resume Assistant helping a job seeker with their resume.
        The user has uploaded their resume which you can reference.
        Be specific and provide actionable advice based on their actual resume content.
        
        Resume Content:
        {self.resume_text}
        
        Current Conversation:
        {self._format_conversation()}
        
        Guidelines:
        1. Always reference specific parts of the resume when possible
        2. Provide concrete suggestions for improvement
        3. Answer questions about career paths based on their experience
        4. Help tailor the resume for specific jobs when asked
        5. Keep responses professional but conversational
        '''
        
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": prompt
                    },
                    {
                        "role": "user",
                        "content": user_message
                    }
                ],
                model="llama3-70b-8192",
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content
            self._add_assistant_message(ai_response)
            return {"response": ai_response}
            
        except Exception as e:
            print("Groq API error:", e)
            return {"error": str(e)}
    
    def _add_system_message(self, message):
        self.conversation_history.append({"role": "system", "content": message})
        
    def _add_user_message(self, message):
        self.conversation_history.append({"role": "user", "content": message})
        
    def _add_assistant_message(self, message):
        self.conversation_history.append({"role": "assistant", "content": message})
        
    def _format_conversation(self):
        return "\n".join(
            f"{msg['role']}: {msg['content']}" 
            for msg in self.conversation_history[-6:]  # Keep last 6 messages for context
        )

# Example usage:
if __name__ == "__main__":
    assistant = ResumeAssistant()
    assistant.load_resume("sample_resume.pdf")
    
    # Interactive chat loop
    print("Resume Assistant ready. Type 'quit' to exit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'quit':
            break
            
        response = assistant.chat(user_input)
        print("Assistant:", response.get("response", "Error occurred"))
import random
import fitz  #type:ignore # PyMuPDF library for extracting text from PDFs
import re
from collections import defaultdict
import spacy  # SpaCy for NLP processing

class Chatbot:
    def __init__(self):
        # Initialize an empty knowledge base and NLP model
        self.knowledge_base = defaultdict(str)
        self.extracted_sentences = []  # Stores extracted sentences from PDFs
        self.nlp = spacy.load("en_core_web_sm")  # Load spaCy's English model for NLP tasks

    def extract_text_from_pdf(self, file_path):
        """
        Extracts text from a given PDF file and populates the knowledge base.
        This function reads all pages of the PDF and processes the text.
        """
        try:
            doc = fitz.open(file_path)  # Open the PDF file
            text = ""
            for page in doc:
                text += page.get_text()  # Extract text from each page
            doc.close()

            # Split text into sentences using regex to handle various sentence endings
            self.extracted_sentences = re.split(r'\.\s+', text)
            self._build_knowledge_base()  # Build the knowledge base from extracted sentences
            return "PDF successfully processed and added to the knowledge base."
        except Exception as e:
            return f"Error reading PDF: {e}"

    def _build_knowledge_base(self):
        """
        Builds a knowledge base from extracted sentences by identifying keywords.
        Uses spaCy NLP to categorize sentences based on common IT keywords like CPU, RAM, HTTP.
        """
        for sentence in self.extracted_sentences:
            doc = self.nlp(sentence)  # Process the sentence with spaCy
            for token in doc:
                # Categorize sentences into different knowledge areas based on keywords
                if "cpu" in token.text.lower():
                    self.knowledge_base["cpu"] += sentence + ". "
                elif "ram" in token.text.lower():
                    self.knowledge_base["ram"] += sentence + ". "
                elif "http" in token.text.lower():
                    self.knowledge_base["http"] += sentence + ". "

    def teach(self, user_input):
        """
        Responds to user's IT-related questions using the knowledge base.
        Matches keywords in user input to the knowledge categories available.
        """
        user_input = user_input.lower()
        # Match input to known categories and provide relevant information
        if "cpu" in user_input and self.knowledge_base["cpu"]:
            return self.knowledge_base["cpu"]
        elif "ram" in user_input and self.knowledge_base["ram"]:
            return self.knowledge_base["ram"]
        elif "http" in user_input and self.knowledge_base["http"]:
            return self.knowledge_base["http"]
        else:
            return "I'm sorry, I don't have information on that topic. Please upload a textbook for me to learn from."

    def generate_quiz_question(self):
        """
        Generates a quiz question based on the extracted sentences.
        Uses NLP to identify key terms and create fill-in-the-blank questions.
        """
        if not self.extracted_sentences:
            return {"question": "No content available to generate questions. Please upload a PDF."}

        # Randomly select a sentence and identify key terms for quizzing
        sentence = random.choice(self.extracted_sentences)
        doc = self.nlp(sentence)
        # Extract key terms such as nouns, proper nouns, verbs, and adjectives
        key_terms = [token.text for token in doc if token.pos_ in ["NOUN", "PROPN", "VERB", "ADJ"]]
        
        if not key_terms:
            return {"question": "Unable to generate a valid question from the sentence."}

        masked_term = random.choice(key_terms)  # Randomly choose a term to mask
        question = sentence.replace(masked_term, "____", 1)  # Create a fill-in-the-blank question
        return {
            "question": f"Fill in the blank: {question}",
            "answer": masked_term
        }

    def evaluate_quiz_answer(self, user_answer, correct_answer):
        """
        Evaluates the user's answer against the correct answer.
        Provides feedback on whether the answer is correct or not.
        """
        if user_answer.lower() == correct_answer.lower():
            return True, "Correct! Great job!"
        else:
            return False, f"Incorrect. The correct answer was: {correct_answer}"

    def chat(self, user_input):
        """
        Main interaction method. Decides whether to teach or quiz based on user input.
        If 'quiz' is mentioned, it generates a quiz question, otherwise it provides information.
        """
        if "quiz" in user_input.lower():
            question_data = self.generate_quiz_question()
            return {
                "type": "quiz",
                "question": question_data["question"],
                "answer": question_data.get("answer", "")
            }
        else:
            return {
                "type": "teach",
                "response": self.teach(user_input)
            }

# Example usage
if __name__ == "__main__":
    bot = Chatbot()
    
    # Load PDF and extract knowledge base
    response = bot.extract_text_from_pdf("sample.pdf")  # Replace with your PDF file path
    print(response)
    
    print("Welcome to the IT Chatbot! Ask a question or type 'quiz' to start a quiz.")
    while True:
        user_input = input("You: ")
        response = bot.chat(user_input)

        if response["type"] == "teach":
            print("Bot:", response["response"])
        elif response["type"] == "quiz":
            print("Bot: Let's start a quiz!")
            print("Question:", response["question"])
            user_answer = input("Your answer: ")
            correct, feedback = bot.evaluate_quiz_answer(user_answer, response["answer"])
            print("Bot:", feedback)

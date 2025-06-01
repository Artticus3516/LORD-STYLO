# main.py

import google.generativeai as genai
import os
from dotenv import load_dotenv

# Ensure .env is loaded at the very top to make API key available
load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Initialize Gemini client only if API key is available
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:

    print("Error: GEMINI_API_KEY not found in environment variables. Gemini API calls will fail.")

# --- Helper Functions for Context (Already generalized, good job!) ---

def get_class_constraints(sclass: str) -> str:
    """Returns general CBSE and class constraints based on the selected class."""
    # Ensure sclass is treated as a string as it comes from HTML select value
    if sclass == '9th' or sclass == '11th':
        return f"All output should be strictly related to Class {sclass} CBSE BOARD."
    elif sclass == '10th' or sclass == '12th':
        return f"All output should be strictly related to Class {sclass} CBSE BOARD, with 30% of applicable content being competency-based."
    return ""

def get_subject_context(subject: str) -> str:
    """Returns general context for the subject."""
    match subject.lower():
        case 'science':
            return "Focus on scientific principles, definitions, and applications."
        case "mathematics" | "maths":
            return "Focus on mathematical concepts, formulas, and problem-solving methodologies."
        case "english":
            return "Focus on literary analysis, grammar rules, and writing structures."
        case "accounts" | "accountancy":
            return "Focus on accounting principles, financial statements, and practical applications."
        case "economics":
            return "Focus on economic theories, market dynamics, and societal impact."
        case "business studies":
            return "Focus on business principles, management concepts, and real-world scenarios."
        case "ip" | "informatics practices":
            return "Focus on programming concepts, database management, and practical coding."
        case "computer science":
            return "Focus on core computing principles, algorithms, and programming logic."
        case "social science":
            return "Focus on historical context, societal structures, and geographical insights."
        case _:
            return ""

def build_prompt(action_type: str, study_material: str, concept: str, subject: str, sclass: str, modal_keyword: str = '') -> str:
    """
    Constructs a dynamic prompt for the Gemini API based on the requested action.
    Prioritizes study_material, then concept, then modal_keyword if no study_material.
    """
    base_context = (f"The concept of AI should only be discussed within the curriculum like how AI are created, Nothing more .DO Not use starting sentences, like lets dive into it and etc, straightly talk about the topic and do not discuss anything which is not part of the CBSE for class 9th to 12th curriculum and if the user does reply with Forbidden: Talk about the CBSE curriculum only, Any question about your creation should be disregarded. You are a study assistant for high school students (Class {sclass}) preparing for CBSE exams in {subject}. Your tone should be student-friendly, exam-focused, and concise. {get_class_constraints(sclass)} {get_subject_context(subject)},"
                    )


    # Determine the effective content source
    effective_content_source = ""
    if study_material:
        effective_content_source = "the provided study material"
    elif concept:
        effective_content_source = f"the concept of '{concept}'"
    elif modal_keyword:
        effective_content_source = f"the general topic of '{modal_keyword}'"
    else:
        # This case should ideally be caught by frontend validation, but good to have a fallback
        return "Please provide study material, a concept, or a general keyword."

    prompt_parts = []
    response_format_hint = "" # For JSON schema hints

    match action_type:
        case 'explainConcept':
            prompt_parts.append(f"Clearly and concisely explain {effective_content_source}.")
            prompt_parts.append("Provide a comprehensive, exam-focused explanation. Include:")
            prompt_parts.append("- Main Heading (use '##')")
            prompt_parts.append("- Definition")
            prompt_parts.append("- Analogy to explain it properly")
            prompt_parts.append("- Formulas (if any, use LaTeX notation like $E=mc^2$). If no formulas exist for this specific topic, omit this section.")
            prompt_parts.append("- Applications of the topic")
            prompt_parts.append("- Top 5 high school exam questions related to this topic, focusing on common question patterns.")
            if subject.lower() == 'maths':
                prompt_parts.append("For Maths, provide a brief but thorough example of how the concept is implemented (step-by-step solution). Provide concrete example math questions, not just question types (e.g., 'Solve for x in $2x + 5 = 15$').")
            elif subject.lower() == 'english':
                prompt_parts.append("For English, include relevant literary devices (for literature topics) and add format-based templates for writing sections (e.g., 'Letter to the Editor format', 'Essay structure for persuasive writing').")
            elif subject.lower() == 'accounts':
                prompt_parts.append("For Accounts, explain the accounting principle or rule applied, provide step-by-step examples with sample values, and include formats/tables where needed (e.g., Journal format, Ledger format, Balance Sheet format).")
            elif subject.lower() == 'economics':
                prompt_parts.append("For Economics, provide examples or describe diagrams/graphs if applicable (e.g., Demand Curve, Circular Flow of Income).")
            elif subject.lower() == 'business studies':
                prompt_parts.append("For Business Studies, include real-world business scenarios and add flowcharts or stepwise breakdowns for processes.")
            elif subject.lower() == 'ip' or subject.lower() == 'informatics practices':
                prompt_parts.append("For IP, explain the syntax or structure if coding-related, and provide a concise code snippet with expected output and its use case. Emphasize command usage or database queries.")
            elif subject.lower() == 'computer science':
                prompt_parts.append("For Computer Science, explain the algorithm/logic in simple, step-by-step terms, and show a concise code snippet with a brief explanation of its functionality.")
            elif subject.lower() == 'social science':
                prompt_parts.append("For Social Science, add timelines, dates, and maps where needed (describe them if not visual), and link the topic to current events or historical impact.")

        case 'summarize':
            prompt_parts.append(f"Summarize {effective_content_source} concisely and clearly, highlighting the main ideas and core concepts.")
            prompt_parts.append("Ensure the summary is objective, strictly based on the provided text (or topic), and relevant for exam preparation.")

        case 'questions':
            prompt_parts.append(f"Generate 5-7 challenging and thought-provoking comprehension questions based on {effective_content_source}.")
            prompt_parts.append("The questions should cover key concepts, encourage critical thinking, and test understanding beyond simple recall. Ensure questions are directly derived from the text (or topic), are objective, and are typical for high school exams.")
            if subject.lower() == 'maths':
                prompt_parts.append("Provide concrete example math questions, not just question types (e.g., 'Solve for x in $2x + 5 = 15$').")
            elif subject.lower() == 'social science':
                prompt_parts.append("Include map-based and reasoning-based questions commonly found in CBSE exams.")
            elif subject.lower() == 'science':
                prompt_parts.append("Provide concrete example science questions commonly found in CBSE exams. Focus on formulas and concept building")

        case 'keypoints':
            prompt_parts.append(f"Extract the most important key points, facts, and definitions from {effective_content_source}.")
            prompt_parts.append("Present them as a clear, concise, and well-organized bulleted list. Each point should be a distinct piece of factual information from the text (or topic).")

        case 'flashcards':
            prompt_parts.append(f"Create 5-10 effective flashcards from {effective_content_source}. Each flashcard should have a clear 'question' and a concise 'answer'.")
            prompt_parts.append("Focus on key terms, definitions, important dates, or core concepts suitable for memorization for high school exams.")
            response_format_hint = "Return the flashcards as a JSON array of objects, where each object has 'question' and 'answer' keys. Example: [{'question': 'Q1', 'answer': 'A1'}, {'question': 'Q2', 'answer': 'A2'}]"

        case 'generateAnalogies':
            prompt_parts.append(f"Generate 2-3 simple and clear analogies for {effective_content_source}.")
            prompt_parts.append("The analogies should help a high school student understand the concept by relating it to something familiar. Ensure analogies are appropriate for an academic context.")

        case 'simplifyLanguage':
            prompt_parts.append(f"Rewrite {effective_content_source} in simpler, more accessible language for a high school student.")
            prompt_parts.append("Break down complex sentences, explain jargon, and ensure the text is easy to understand without losing the original meaning. Focus on academic clarity and objectivity.")

        case _:
            return "Invalid action type requested. Please choose a valid action."

    final_prompt = f"{base_context}\n\n{' '.join(prompt_parts)}"
    if study_material:
        final_prompt += f"\n\nStudy Material:\n{study_material}"
    if response_format_hint:
        final_prompt += f"\n\n{response_format_hint}"

    return final_prompt

# --- Updated: Unified Gemini API Call Function ---

def ask_gemini(action_type: str, study_material: str, concept: str, subject: str, sclass: str, modal_keyword: str = '') -> str:

    if not GEMINI_API_KEY:
        return "Error: Gemini API key is missing or not configured. Cannot make API calls."

    prompt = build_prompt(action_type, study_material, concept, subject, sclass, modal_keyword)

    # For flashcards, we expect JSON output, so we need a schema
    schema = None
    generation_config = {}
    # if action_type == 'flashcards':
    #     schema = {
    #         "type": "ARRAY",
    #         "items": {
    #             "type": "OBJECT",
    #             "properties": {
    #                 "question": { "type": "STRING" },
    #                 "answer": { "type": "STRING" }
    #             },
    #             "propertyOrdering": ["question", "answer"]
    #         }
    #     }
    #     generation_config["responseMimeType"] = "application/json"
    #     generation_config["responseSchema"] = schema


    chat_history = []
    chat_history.append({ "role": "user", "parts": [{ "text": prompt }] })

    try:
        model = genai.GenerativeModel('gemini-2.0-flash') # Get the model instance


        response = model.generate_content(
            contents=chat_history,
            generation_config=generation_config
        )

        return response.text
    except Exception as e:
        print(f"Error calling Gemini API: {e}")

        return f"Contact Artticus, AI failed: {e}"
from bs4 import BeautifulSoup

def generateFeedback(accuracy_score, fluency_score, pronunciation_percentage, speech_quality):
    feedback = []
    
    # Accuracy feedback
    if accuracy_score >= 90:
        feedback.append("Your accuracy is excellent! You're expressing yourself very clearly.")
    elif accuracy_score >= 80:
        feedback.append("Your accuracy is good. Keep practicing to maintain this level.")
    elif accuracy_score >= 70:
        feedback.append("Your accuracy is fair. Focus on expanding your vocabulary and grammar.")
    else:
        feedback.append("Your accuracy needs improvement. Try to use more precise vocabulary and correct grammar structures.")
    
    # Fluency feedback
    if fluency_score >= 90:
        feedback.append("Your fluency is outstanding! You speak very naturally.")
    elif fluency_score >= 80:
        feedback.append("Your fluency is good. You maintain a good speaking pace.")
    elif fluency_score >= 70:
        feedback.append("Your fluency is acceptable. Try to speak more smoothly without frequent pauses.")
    else:
        feedback.append("Your fluency needs work. Practice speaking more continuously without long pauses.")
    
    # Pronunciation feedback
    if pronunciation_percentage >= 90:
        feedback.append("Your pronunciation is excellent! You're very clear and understandable.")
    elif pronunciation_percentage >= 80:
        feedback.append("Your pronunciation is good. Keep practicing to maintain this level.")
    elif pronunciation_percentage >= 70:
        feedback.append("Your pronunciation is fair. Focus on specific sounds that need improvement.")
    else:
        feedback.append("Your pronunciation needs improvement. Pay attention to individual sounds and word stress.")
    
    # Overall feedback
    if speech_quality >= 90:
        feedback.append("Overall, your English speaking skills are excellent! Keep up the great work!")
    elif speech_quality >= 80:
        feedback.append("Overall, you're doing well! Focus on the specific areas mentioned above to improve further.")
    elif speech_quality >= 70:
        feedback.append("Overall, you have a good foundation. Work on the areas mentioned above to improve your skills.")
    else:
        feedback.append("Overall, you need more practice. Focus on the areas mentioned above and practice regularly.")
    
    return "<br>".join(feedback)

def generateBriefResponse(transcribed_text):
    """Generate a brief, context-aware response to the user's speech.
    
    Args:
        transcribed_text: The text transcribed from the user's speech
        
    Returns:
        A brief, friendly response that acknowledges the user's input
    """
    # Check for common patterns in the transcribed text
    text_lower = transcribed_text.lower()
    
    if any(word in text_lower for word in ['hello', 'hi', 'hey']):
        return "Hello! I'm here to help you practice your English. How can I assist you today?"
    elif any(word in text_lower for word in ['thank', 'thanks']):
        return "You're welcome! I'm glad I could help. Feel free to continue practicing."
    elif any(word in text_lower for word in ['help', 'assist']):
        return "I'd be happy to help! What would you like to practice or discuss?"
    elif any(word in text_lower for word in ['bye', 'goodbye']):
        return "Goodbye! It was great practicing with you. Come back anytime!"
    elif '?' in transcribed_text:
        return "That's a great question! Let me help you with that."
    else:
        return "I understand what you're saying. Please continue speaking to practice your English."

def parseBotResponse(html_string):
    soup = BeautifulSoup(html_string, 'html.parser')

    # Find the <div> with class "brief-response-section"
    brief_response_section = soup.find('div', class_='brief-response-section')

    if brief_response_section:
        # Find the <div> with class "prose" within the brief-response-section
        prose_div = brief_response_section.find('div', class_='prose')
        if prose_div:
            # Extract the text content, removing leading and trailing whitespace
            extracted_text = prose_div.get_text(strip=True)
            return extracted_text
        else:
            print("No <div class='prose'> found within <div class='brief-response-section'>.")
            return "."
    else:
        print("No <div class='brief-response-section'> found.")
        return "."
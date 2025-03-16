from google.cloud import speech
import pyaudio
import wave
import time
import string
import difflib

wrong_pronounce = []
is_listening = False

def record_audio(filename, duration=5, sample_rate=16000, channels=1):
    """Records audio from the microphone and saves it to a file."""
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=channels, rate=sample_rate, input=True, frames_per_buffer=1024)
    frames = []

    print("Recording...")
    for _ in range(0, int(sample_rate / 1024 * duration)):
        data = stream.read(1024)
        frames.append(data)
    print("Finished recording.")

    stream.stop_stream()
    stream.close()
    p.terminate()

    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(sample_rate)
        wf.writeframes(b''.join(frames))

def pronunciation_assessment_from_microphone(language, reference, filename):
    """Performs pronunciation assessment using Google Speech-to-Text.
    
    Args:
        language: Language code (e.g., 'en-US')
        reference: Reference text to compare against
        filename: Path to the audio file
        
    Returns:
        Tuple of (accuracy_score, completeness_score, fluency_score, word_evaluation, final_words)
    """
    try:
        client = speech.SpeechClient()

        # Read the audio file
        with wave.open(filename, 'rb') as audio_file:
            content = audio_file.readframes(audio_file.getnframes())
            sample_rate = audio_file.getframerate()

        audio = speech.RecognitionAudio(content=content)

        # Configure recognition
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=sample_rate,  # Use the actual sample rate from the file
            language_code=language,
            enable_word_time_offsets=True,
            enable_word_confidence=True  # Enable confidence scores for better accuracy assessment
        )

        # Get the transcribed text and word timings
        response = client.recognize(config=config, audio=audio)
        
        if not response.results:
            raise Exception("No speech detected")

        recognized_words = []
        word_timings = []
        word_confidences = []
        
        for result in response.results:
            alternative = result.alternatives[0]
            for word in alternative.words:
                recognized_words.append(word.word.lower())
                word_timings.append(word.end_time.total_seconds() - word.start_time.total_seconds())
                # Get confidence if available, otherwise use 1.0
                confidence = getattr(word, 'confidence', 1.0)
                word_confidences.append(confidence)

        # Clean reference text
        reference_words = [w.strip(string.punctuation).lower() for w in reference.split()]

        # Calculate word-level metrics using confidence scores
        final_words = []
        for word, confidence in zip(recognized_words, word_confidences):
            if word in reference_words:
                error_type = 'None' if confidence > 0.8 else 'Mispronounced'
                final_words.append({
                    'word': word,
                    'error_type': error_type,
                    'confidence': confidence
                })
            else:
                final_words.append({
                    'word': word,
                    'error_type': 'Mispronounced',
                    'confidence': confidence
                })

        # Calculate accuracy score using confidence scores
        accuracy_score = (
            sum(w['confidence'] * 100 for w in final_words if w['error_type'] == 'None') /
            len(final_words) if final_words else 0
        )

        # Calculate fluency score (words per minute)
        if word_timings:
            total_duration = sum(word_timings)
            words_per_minute = (len(recognized_words) / total_duration) * 60
            # Normalize to 0-100 scale (assuming 150 wpm is "perfect")
            fluency_score = min(100, (words_per_minute / 150) * 100)
        else:
            fluency_score = 0

        # Calculate completeness score (percentage of reference words covered)
        completeness_score = (len(recognized_words) / len(reference_words) * 100) if reference_words else 0
        completeness_score = min(100, completeness_score)  # Cap at 100%

        # Generate word-by-word evaluation with confidence scores
        word_evaluation = []
        for idx, word in enumerate(final_words):
            confidence_percent = round(word['confidence'] * 100, 1)
            word_evaluation.append(
                f'word {idx + 1}: {word["word"]}, error type: {word["error_type"]}, confidence: {confidence_percent}%'
            )

        return (
            accuracy_score,
            completeness_score,
            fluency_score,
            word_evaluation,
            final_words
        )

    except Exception as e:
        print(f"Error in pronunciation assessment: {str(e)}")
        raise
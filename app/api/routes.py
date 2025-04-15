from flask import Blueprint, request, jsonify, render_template
from werkzeug.utils import secure_filename
import os
from app.core.helper import generateBriefResponse, generateFeedback, parseBotResponse
from datetime import datetime
from app.core.file_extractor import load_pdf, split_text
from app.core.rag import create_chroma_db, load_chroma_collection, generate_answer
from app.core.chat_room import ChatManager
from config import Config
import google.generativeai as genai
from app.core.pronounce_assessment_mic import pronunciation_assessment_from_microphone
from app.core.intonation import pitch
import base64
import tempfile

# Create the blueprint
api = Blueprint('api', __name__)

# Initialize chat manager
chat_manager = ChatManager(os.path.join(Config.BASE_DIR, 'data', 'chat_rooms'))

@api.route('/', methods=['GET'])
def index():
    # Get all chat rooms for the sidebar
    rooms = chat_manager.list_rooms()
    return render_template('index.html', rooms=rooms)

@api.route('/rooms', methods=['GET'])
def list_rooms():
    rooms = chat_manager.list_rooms()
    return jsonify([{
        'id': room.id,
        'name': room.name,
        'created_at': room.created_at,
        'has_file': bool(room.file_context)
    } for room in rooms])

@api.route('/rooms', methods=['POST'])
def create_room():
    data = request.get_json()
    name = data.get('name', f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    # Handle file upload if provided
    file_context = None
    collection_name = None
    
    if 'file' in request.files:
        file = request.files['file']
        if file and file.filename:
            # Save file
            filename = secure_filename(file.filename)
            file_path = os.path.join(Config.DOCUMENT_DIR, filename)
            file.save(file_path)
            
            # Process file for RAG
            pdf_text = load_pdf(file_path=file_path)
            chunked_text = split_text(text=pdf_text)
            
            # Create ChromaDB collection
            collection_name = f"collection_{int(datetime.now().timestamp())}"
            create_chroma_db(
                documents=chunked_text,
                path=Config.VECTOR_STORE_DIR,
                name=collection_name
            )
            
            file_context = file_path
    
    # Create new room
    room = chat_manager.create_room(
        name=name,
        file_context=file_context,
        collection_name=collection_name
    )
    
    return jsonify({
        'id': room.id,
        'name': room.name,
        'created_at': room.created_at,
        'has_file': bool(room.file_context)
    })

@api.route('/rooms/<room_id>/messages', methods=['GET'])
def get_messages(room_id):
    try:
        messages = chat_manager.get_room_history(room_id)
        return jsonify([{
            'content': msg.content,
            'role': msg.role,
            'timestamp': msg.timestamp,
            'context': msg.context
        } for msg in messages])
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    
@api.route('/rooms/<int:room_id>/upload', methods=['POST'])
def upload(room_id):
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if not file or not file.filename:
            return jsonify({'error': 'Invalid file'}), 400
            
        # Get room
        room = chat_manager.get_room(room_id)
        if not room:
            return jsonify({'error': 'Room not found'}), 404
            
        # Save file with timestamp
        filename = secure_filename(f"{int(datetime.now().timestamp())}_{file.filename}")
        file_path = os.path.join(Config.DOCUMENT_DIR, filename)
        file.save(file_path)
        
        try:
            print("1")
            # Process file for RAG - with status updates
            chat_manager.add_message(
                room_id=room_id,
                content="Processing document... This may take a moment.",
                role="system"
            )
            
            # Load and chunk the PDF
            pdf_text = load_pdf(file_path=file_path)
            chunked_text = split_text(
                text=pdf_text,
                chunk_size=500,  # Smaller chunks for faster processing
                chunk_overlap=50  # Minimal overlap
            )
            print("2")
            
            # Create ChromaDB collection with optimized settings
            collection_name = f"collection_{int(datetime.now().timestamp())}"
            create_chroma_db(
                documents=chunked_text,
                path=Config.VECTOR_STORE_DIR,
                name=collection_name
            )

            print("2.1")
            
            # Update room with file context
            chat_manager.update_room(
                room_id=room_id,
                file_context=file_path,
                collection_name=collection_name
            )
            print("3")
            
            # Add success message
            chat_manager.add_message(
                room_id=room_id,
                content=f"Document processed successfully! You can now ask questions about {file.filename}",
                role="system"
            )

            print("4")
            
            return jsonify({
                'message': 'File uploaded and processed successfully',
                'filename': filename,
                'collection': collection_name
            })
            
        except Exception as e:
            # Clean up on error
            print(e)
            if os.path.exists(file_path):
                os.remove(file_path)
            raise e
            
    except Exception as e:
        print(f'Error processing file: {str(e)}')
        return jsonify({
            'error': f'Error processing file: {str(e)}'
        }), 500

@api.route('/rooms/<int:room_id>/chat', methods=['POST'])
def chat(room_id):
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'No message provided'}), 400
        
        room = chat_manager.get_room(room_id)
        if not room:
            return jsonify({'error': 'Room not found'}), 404
        
        user_message = data['message']
        
        # Get relevant context based on the user's query
        relevant_context = chat_manager.get_relevant_context(
            room_id=room_id,
            query=user_message,
            limit=5
        )
        
        # Format chat history for context
        chat_history = [
            {
                'role': msg.role,
                'content': msg.content
            }
            for msg in relevant_context
        ]
        
        # Add user message
        chat_manager.add_message(
            room_id=room_id,
            content=user_message,
            role='user'
        )
        
        # Generate response
        if room.collection_name:
            # Use RAG for rooms with documents
            db = load_chroma_collection(
                path=str(Config.VECTOR_STORE_DIR),
                name=room.collection_name
            )
            result = generate_answer(
                db=db,
                query=user_message,
                chat_history=chat_history
            )
            response_content = result['answer']
            context = {
                'passages': result['supporting_info']['passages'],
                'metadata': result['supporting_info']['metadata']
            }
        else:
            # Use regular chat for rooms without documents
            # Format messages for Gemini
            model = genai.GenerativeModel('gemini-2.0-flash')
            chat = model.start_chat()
            
            # Add system message
            chat.send_message("""You are a friendly and engaging English language tutor. 
Your responses should be:
1. Natural and conversational - like talking to a friend
2. Warm and encouraging - always find something positive to say
3. Specific and actionable - give clear, practical advice
4. Brief but meaningful - keep responses concise but helpful
5. Personal - use "you" and "your" to make it more engaging

Remember to:
- Start with a friendly greeting or acknowledgment
- Use contractions (e.g., "you're" instead of "you are")
- Keep the tone light and supportive""")
            
            # Add chat history
            for msg in chat_history:
                chat.send_message(msg['content'])
            
            # Send user message and get response
            response = chat.send_message(user_message)
            
            response_content = response.text
            # Include conversation context
            context = {
                'conversation_history': chat_history,
                'current_query': {
                    'content': user_message,
                    'timestamp': datetime.now().isoformat()
                }
            }
        
        # Add assistant response
        response = chat_manager.add_message(
            room_id=room_id,
            content=response_content,
            role='assistant',
            context=context
        )
        
        return jsonify({
            'transcription': response.content,
            'content': response.content,
            'role': response.role,
            'timestamp': response.timestamp.isoformat(),
            'context': response.context
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api.route('/rooms/<int:room_id>/voice_chat', methods=['POST'])
def voice_chat(room_id):
    temp_audio_path = None
    temp_wav_path = None
    response_audio_path = None
    
    try:
        data = request.get_json()
        if not data or 'audio' not in data:
            return jsonify({'error': 'No audio data provided'}), 400
        
        room = chat_manager.get_room(room_id)
        if not room:
            return jsonify({'error': 'Room not found'}), 404

        # Decode base64 audio data
        try:
            audio_data = base64.b64decode(data['audio'])
        except Exception as e:
            return jsonify({'error': 'Invalid audio data format'}), 400

        # Save initial audio to temporary file (WebM)
        temp_audio_path = str(Config.TEMP_DIR / f'audio_{datetime.now().timestamp()}.webm')
        temp_wav_path = str(Config.TEMP_DIR / f'audio_{datetime.now().timestamp()}.wav')
        response_audio_path = str(Config.TEMP_DIR / f'response_{datetime.now().timestamp()}.wav')
        
        try:
            with open(temp_audio_path, 'wb') as temp_audio:
                temp_audio.write(audio_data)
        except Exception as e:
            return jsonify({'error': 'Failed to save audio file'}), 500

        # Convert WebM to WAV using ffmpeg
        try:
            import subprocess
            subprocess.run([
                'ffmpeg', '-i', temp_audio_path,
                '-acodec', 'pcm_s16le',
                '-ar', '16000',
                '-ac', '1',
                temp_wav_path
            ], check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            return jsonify({
                'error': 'Failed to convert audio format',
                'details': str(e.stderr)
            }), 500

        # Get the transcribed text from audio
        try:
            from app.core.stt import recognize_from_microphone
            transcribed_text = recognize_from_microphone(temp_wav_path)

            print("transcribed_text", transcribed_text)
            
            if not transcribed_text:
                return jsonify({
                    'error': 'Could not transcribe audio. Please speak clearly and try again.',
                    'details': 'No speech detected in the audio'
                }), 400
                
        except Exception as e:
            return jsonify({
                'error': 'Speech recognition failed',
                'details': str(e)
            }), 500

        # Get pronunciation assessment
        try:
            accuracy_score, completeness_score, fluency_score, word_evaluation, final_words = \
                pronunciation_assessment_from_microphone('en-US', transcribed_text, str(temp_wav_path))
        except Exception as e:
            print(f"Pronunciation assessment error: {str(e)}")
            # Provide default values if pronunciation assessment fails
            accuracy_score = completeness_score = fluency_score = 0
            word_evaluation = [f"Could not evaluate pronunciation: {str(e)}"]
            final_words = [{'word': word, 'error_type': 'Unknown'} for word in transcribed_text.split()]

        # Get pitch analysis
        input_words = transcribed_text.split()
        try:
            per_word_pitch, overall_pitch = pitch(input_words, str(temp_wav_path))
        except Exception as e:
            print(f"Pitch analysis error: {str(e)}")
            per_word_pitch = [f"{word}: N/A" for word in input_words]
            overall_pitch = 0

        # Calculate speech quality score
        total_words = len(final_words)
        mispronounced_count = len([w for w in final_words if w['error_type'] != 'None'])
        correct_pronunciation_percentage = ((total_words - mispronounced_count) / total_words) * 100 if total_words > 0 else 0
        
        speech_quality = (
            (accuracy_score * 0.4) +          # 40% weight to accuracy
            (completeness_score * 0.3) +      # 30% weight to completeness
            (fluency_score * 0.2) +           # 20% weight to fluency
            (correct_pronunciation_percentage * 0.1)  # 10% weight to pronunciation
        )

        # Process the transcribed text as a regular chat message
        chat_history = chat_manager.get_relevant_context(room_id, transcribed_text, limit=5)
        chat_history = [{'role': msg.role, 'content': msg.content} for msg in chat_history]

        # Add user message with speech metrics
        chat_manager.add_message(
            room_id=room_id,
            content=transcribed_text,
            role='user',
            context={
                'speech_metrics': {
                    'accuracy': round(accuracy_score, 2),
                    'completeness': round(completeness_score, 2),
                    'fluency': round(fluency_score, 2),
                    'pronunciation_accuracy': round(correct_pronunciation_percentage, 2),
                    'speech_quality': round(speech_quality, 2),
                    'word_evaluation': word_evaluation,
                    'pitch_analysis': per_word_pitch,
                    'overall_pitch': round(overall_pitch, 2)
                }
            }
        )

        # Generate response using existing logic
        if room.collection_name:
            db = load_chroma_collection(path=str(Config.VECTOR_STORE_DIR), name=room.collection_name)
            result = generate_answer(db=db, query=transcribed_text, chat_history=chat_history)
            response_content = result['answer']
            context = {
                'passages': result['supporting_info']['passages'],
                'metadata': result['supporting_info']['metadata']
            }
        else:
            model = genai.GenerativeModel('gemini-2.0-flash')
            chat = model.start_chat()
            chat.send_message("""You are a friendly and engaging English language tutor. 
Your responses should be:
1. Natural and conversational - like talking to a friend
2. Warm and encouraging - always find something positive to say
3. Specific and actionable - give clear, practical advice
4. Brief but meaningful - keep responses concise but helpful
5. Personal - use "you" and "your" to make it more engaging

Remember to:
- Start with a friendly greeting or acknowledgment
- Use contractions (e.g., "you're" instead of "you are")
- Keep the tone light and supportive""")
            
            for msg in chat_history:
                chat.send_message(msg['content'])
            
            response = chat.send_message(f"""User said: {transcribed_text}
Speech metrics:
- Accuracy: {round(accuracy_score, 2)}%
- Fluency: {round(fluency_score, 2)}%
- Pronunciation: {round(correct_pronunciation_percentage, 2)}%
- Overall Quality: {round(speech_quality, 2)}%

Please provide a friendly, conversational response that includes:
1. A brief answer to their question
2. Feedback on their English speaking skills
3. Specific suggestions for improvement

Format your response in HTML with the following structure:

<div class="brief-response-section">
    <h3 class="text-lg font-semibold mb-2">Response</h3>
    <div class="prose">
        {generateBriefResponse(transcribed_text)}
    </div>
</div>

<div class="feedback-section">
    <h3 class="text-lg font-semibold mb-2">Speech Analysis</h3>
    <div class="grid grid-cols-2 gap-2 mb-4">
        <div class="bg-gray-50 p-2 rounded">
            <div class="text-sm text-gray-500">Accuracy</div>
            <div class="text-lg font-bold text-blue-600">{round(accuracy_score, 2)}%</div>
        </div>
        <div class="bg-gray-50 p-2 rounded">
            <div class="text-sm text-gray-500">Fluency</div>
            <div class="text-lg font-bold text-green-600">{round(fluency_score, 2)}%</div>
        </div>
        <div class="bg-gray-50 p-2 rounded">
            <div class="text-sm text-gray-500">Pronunciation</div>
            <div class="text-lg font-bold text-purple-600">{round(correct_pronunciation_percentage, 2)}%</div>
        </div>
        <div class="bg-gray-50 p-2 rounded">
            <div class="text-sm text-gray-500">Overall Quality</div>
            <div class="text-lg font-bold text-indigo-600">{round(speech_quality, 2)}%</div>
        </div>
    </div>
    <div class="word-analysis bg-white p-3 rounded-lg shadow max-h-40 overflow-y-auto mb-4">
        <h4 class="font-semibold mb-2">Word Analysis</h4>
        {''.join([f'<div class="mb-2 p-2 rounded {("bg-green-50" if "error type: None" in eval else "bg-red-50")}">{eval}</div>' for eval in word_evaluation])}
    </div>
    <div class="feedback-content">
        <h3 class="text-lg font-semibold mb-2">Feedback</h3>
        <div class="prose">
            {generateFeedback(accuracy_score, fluency_score, correct_pronunciation_percentage, speech_quality)}
        </div>
    </div>
</div>

Remember to keep the tone friendly and conversational throughout! 😊
""")
            
            response_content = response.text
            print("res", response_content)
            context = {
                'conversation_history': chat_history,
                'current_query': {
                    'content': transcribed_text,
                    'timestamp': datetime.now().isoformat()
                }
            }

        # Convert response to speech
        try:
            from app.core.tts import text_to_speech
            text_for_speech = parseBotResponse(response_content)
            text_to_speech('en-US-Standard-C', text_for_speech, str(response_audio_path))

            # Read response audio file and convert to base64
            with open(response_audio_path, 'rb') as audio_file:
                response_audio = base64.b64encode(audio_file.read()).decode('utf-8')
        except Exception as e:
            print(f"TTS error: {str(e)}")
            response_audio = None

        # Add assistant response
        response = chat_manager.add_message(
            room_id=room_id,
            content=response_content,
            role='assistant',
            context=context
        )

        result = {
            'transcription': transcribed_text,
            'content': response.content,
            'role': response.role,
            'timestamp': response.timestamp.isoformat(),
            'context': response.context,
            'speech_metrics': {
                'accuracy': round(accuracy_score, 2),
                'completeness': round(completeness_score, 2),
                'fluency': round(fluency_score, 2),
                'pronunciation_accuracy': round(correct_pronunciation_percentage, 2),
                'speech_quality': round(speech_quality, 2),
                'word_evaluation': word_evaluation,
                'pitch_analysis': per_word_pitch,
                'overall_pitch': round(overall_pitch, 2)
            }
        }

        print("result", result)
        
        if response_audio:
            result['response_audio'] = response_audio

        return jsonify(result)

    except Exception as e:
        print(f"Voice chat error: {str(e)}")
        return jsonify({'error': str(e)}), 500
        
    finally:
        # Clean up temporary files
        if temp_audio_path and os.path.exists(str(temp_audio_path)):
            try:
                os.unlink(temp_audio_path)
            except:
                pass
        if temp_wav_path and os.path.exists(str(temp_wav_path)):
            try:
                os.unlink(temp_wav_path)
            except:
                pass
        if response_audio_path and os.path.exists(str(response_audio_path)):
            try:
                os.unlink(response_audio_path)
            except:
                pass
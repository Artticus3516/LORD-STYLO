from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
from Main import ask_gemini
app = Flask(__name__)
CORS(app)

@app.route('/feedback')
def lead():
    return send_from_directory('public','feed.html')
@app.route('/api/process', methods=['POST'])
async def explain_concept():
    try:
        data = request.json
        action_type = data.get('action_type')
        study_material = data.get('study_material', '')
        concept = data.get('concept', '')
        subject = data.get('subject', '')
        sclass = data.get('class', '')
        modal_keyword = data.get('modal_keyword', '')

        explanation = await ask_gemini(action_type,study_material,concept,subject,sclass,modal_keyword)
        if action_type == "flashcards":
            try:
                resp = json.loads(explanation)
                if isinstance(resp,list):
                    return jsonify({'flashcards':resp})
                else:
                    return jsonify({'error':"AI failed error occured"})
            except json.JSONDecodeError:
                return jsonify({'error':"Failed to decode json"})


        return jsonify({'explanation': explanation})
    except Exception as e:
        print("Exception occured ==> ",str(e))
        return jsonify({'error' : "Error occured {}".format(str(e))})

@app.route('/')
def home():
    return send_from_directory('public', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('public', path)

if __name__ == '__main__':
    app.run(debug=True)

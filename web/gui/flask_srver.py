from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import gcode

app = Flask(__name__)
CORS(app)

@app.route('/search', methods=['POST'])
def image_fetch():
    data = request.get_json()
    input_value = data.get('input')

    if not input_value:
        return jsonify({"status": "error", "message": "No input provided"}), 400

    try:
        result = gcode.main_func(input_value)   # your custom logic
        if result == 0:
            return jsonify({"status": "success", "result": result})
            #return jsonify({"status": "error", "message": "Failed to generate G-code"}), 500
        if result == 1:
            return jsonify({"status": "error", "message": "All image URLs failed. Cannot generate G-code."}), 500
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500



UPLOAD_FOLDER = "images"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/upload", methods=["POST"])
def upload_file():
    file = request.files["image"]
    #save_path = os.path.join(UPLOAD_FOLDER, file.filename)
    save_path = "images/sketch.jpg"
    file.save(save_path)
    #return f"File saved at {save_path}"

    try:
        result = gcode.gcode_generation()   # your custom logic
        if result == 0:
            return jsonify({"status": "success", "result": result})
            #return jsonify({"status": "error", "message": "Failed to generate G-code"}), 500
        else:
            return jsonify({"status": "error", "message": "Gcode generation failed."}), 500
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500




if __name__ == '__main__':
    app.run(debug=True)

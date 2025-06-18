import os, shutil
from flask import Flask, request, render_template, Response, send_from_directory
from PIL import Image
import pillow_heif

pillow_heif.register_heif_opener()

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "output"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route("/")
def index():
    # Clean up files
    for folder in [UPLOAD_FOLDER, OUTPUT_FOLDER]:
        for file in os.listdir(folder):
            os.remove(os.path.join(folder, file))
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    files = request.files.getlist("heic_files")
    for f in files:
        filename = os.path.basename(f.filename)
        f.save(os.path.join(UPLOAD_FOLDER, filename))
    return "Files uploaded", 200

@app.route("/convert")
def convert():
    def generate():
        files = [f for f in os.listdir(UPLOAD_FOLDER) if f.lower().endswith(".heic")]
        converted = []

        for idx, filename in enumerate(files, 1):
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            image = Image.open(filepath)
            png_name = os.path.splitext(filename)[0] + ".png"
            image.save(os.path.join(OUTPUT_FOLDER, png_name), "PNG")
            converted.append(png_name)
            yield f"{idx}. {filename} → converted to {png_name}\n"

        yield "DONE\n"
        yield "FILES:" + "|".join(converted) + "\n"

    return Response(generate(), mimetype="text/plain")


@app.route("/download-all")
def download_all():
    zip_name = "converted_images"
    shutil.make_archive(zip_name, 'zip', OUTPUT_FOLDER)
    return send_from_directory(".", f"{zip_name}.zip", as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)

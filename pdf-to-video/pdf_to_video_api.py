from flask import Flask, request, send_file, jsonify
import pdfplumber, os
from gtts import gTTS
from diffusers import StableDiffusionPipeline
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
import torch
from PIL import Image
import uuid
import tempfile
import shutil

app = Flask(__name__)

@app.route('/')
def home():
    return "🎉 PDF to Video Backend is Live on Render!"

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "message": "PDF to Video API is running",
        "version": "1.0.0"
    })

@app.route('/upload', methods=['POST'])
def upload_pdf():
    try:
        file = request.files.get('file')
        if not file:
            return jsonify({"error": "No file uploaded"}), 400

        # Check if file is PDF
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({"error": "Please upload a PDF file"}), 400

        uid = str(uuid.uuid4())[:8]
        
        # Create temporary directories
        temp_dir = tempfile.mkdtemp()
        filename = os.path.join(temp_dir, f"input_{uid}.pdf")
        file.save(filename)

        # Extract text from PDF
        pdf_text = ""
        try:
            with pdfplumber.open(filename) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        pdf_text += text + "\n"
        except Exception as e:
            return jsonify({"error": f"Error reading PDF: {str(e)}"}), 400

        if not pdf_text.strip():
            return jsonify({"error": "No text found in PDF"}), 400

        paragraphs = [p.strip() for p in pdf_text.split('\n') if p.strip() and len(p.strip()) > 10]
        
        if not paragraphs:
            return jsonify({"error": "No readable content found in PDF"}), 400

        # Limit to first 3 paragraphs for demo/performance
        paragraphs = paragraphs[:3]

        # Generate audio clips
        audio_dir = os.path.join(temp_dir, f"audio_{uid}")
        os.makedirs(audio_dir, exist_ok=True)
        audio_files = []
        
        for i, para in enumerate(paragraphs):
            try:
                tts = gTTS(text=para, lang='en', slow=False)
                audio_path = os.path.join(audio_dir, f"audio_{i}.mp3")
                tts.save(audio_path)
                audio_files.append(audio_path)
            except Exception as e:
                print(f"Error generating audio for paragraph {i}: {e}")
                continue

        if not audio_files:
            return jsonify({"error": "Failed to generate audio"}), 500

        # Generate images
        image_dir = os.path.join(temp_dir, f"images_{uid}")
        os.makedirs(image_dir, exist_ok=True)
        
        try:
            pipe = StableDiffusionPipeline.from_pretrained(
                "runwayml/stable-diffusion-v1-5", 
                torch_dtype=torch.float16,
                safety_checker=None
            )
            if torch.cuda.is_available():
                pipe = pipe.to("cuda")
            else:
                pipe = pipe.to("cpu")
        except Exception as e:
            return jsonify({"error": f"Error loading AI model: {str(e)}"}), 500

        image_files = []
        for i, para in enumerate(paragraphs):
            try:
                # Use a simple prompt for better performance
                prompt = f"illustration of: {para[:100]}"
                image = pipe(prompt, num_inference_steps=20).images[0]
                image_path = os.path.join(image_dir, f"image_{i}.png")
                image.save(image_path)
                image_files.append(image_path)
            except Exception as e:
                print(f"Error generating image for paragraph {i}: {e}")
                continue

        if not image_files:
            return jsonify({"error": "Failed to generate images"}), 500

        # Combine into video
        clips = []
        for i in range(min(len(audio_files), len(image_files))):
            try:
                img_clip = ImageClip(image_files[i]).set_duration(AudioFileClip(audio_files[i]).duration)
                img_clip = img_clip.set_audio(AudioFileClip(audio_files[i]))
                clips.append(img_clip)
            except Exception as e:
                print(f"Error creating clip {i}: {e}")
                continue

        if not clips:
            return jsonify({"error": "Failed to create video clips"}), 500

        final_video = concatenate_videoclips(clips, method="compose")
        output_video = os.path.join(temp_dir, f"output_{uid}.mp4")
        final_video.write_videofile(output_video, fps=24, verbose=False, logger=None)

        # Clean up intermediate files
        for clip in clips:
            clip.close()
        final_video.close()

        # Send the video file
        return send_file(
            output_video, 
            as_attachment=True,
            download_name=f"converted_video_{uid}.mp4",
            mimetype='video/mp4'
        )

    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500
    
    finally:
        # Clean up temporary directory
        try:
            if 'temp_dir' in locals():
                shutil.rmtree(temp_dir, ignore_errors=True)
        except:
            pass

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

import os
import pytesseract
from flask import Flask, render_template, request, jsonify
from PIL import Image
import io
import base64
import re
import tempfile

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # Batas ukuran file 5MB
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}

# ==================== KONFIGURASI TESSERACT ====================
# UNTUK WINDOWS - HAPUS KOMENTAR PADA BARIS BERIKUT:
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Jika path di atas tidak berhasil, coba path alternatif:
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'
# ==============================================================

# Buat folder upload jika belum ada
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def allowed_file(filename):
    """Memeriksa apakah ekstensi file diizinkan"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def preprocess_image(image):
    """Preprocessing gambar untuk meningkatkan akurasi OCR"""
    try:
        # Konversi ke grayscale jika belum
        if image.mode != 'L':
            image = image.convert('L')
        
        # Tingkatkan kontras
        from PIL import ImageEnhance
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.5)  # Tingkatkan kontras 1.5x
        
        # Tingkatkan kecerahan jika perlu
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(1.2)
        
        return image
    except Exception as e:
        print(f"Error preprocessing: {str(e)}")
        return image

def check_tesseract_installed():
    """Cek apakah Tesseract terinstall"""
    try:
        pytesseract.get_tesseract_version()
        return True, "Tesseract OCR siap digunakan"
    except Exception as e:
        error_msg = str(e)
        if "is not installed or it's not in your PATH" in error_msg:
            return False, "Tesseract tidak ditemukan. Pastikan Tesseract terinstall di 'C:\\Program Files\\Tesseract-OCR'"
        return False, f"Error: {error_msg}"

@app.route('/', methods=['GET', 'POST'])
def index():
    """Route utama untuk halaman web"""
    # Cek status Tesseract
    tesseract_status, tesseract_message = check_tesseract_installed()
    
    if request.method == 'POST':
        # Periksa apakah Tesseract terinstall
        if not tesseract_status:
            return jsonify({'error': tesseract_message}), 500
        
        # Periksa apakah ada file yang diunggah
        if 'image' not in request.files:
            return jsonify({'error': 'Tidak ada file yang diunggah'}), 400
        
        file = request.files['image']
        
        # Periksa apakah file kosong
        if file.filename == '':
            return jsonify({'error': 'Tidak ada file yang dipilih'}), 400
        
        # Periksa ekstensi file
        if not allowed_file(file.filename):
            return jsonify({'error': 'Format file tidak didukung. Gunakan PNG, JPG, atau JPEG'}), 400
        
        try:
            # Baca gambar dari file
            image_data = file.read()
            image = Image.open(io.BytesIO(image_data))
            
            # Validasi gambar
            image.verify()  # Verifikasi bahwa ini adalah gambar yang valid
            image = Image.open(io.BytesIO(image_data))  # Buka ulang setelah verify
            
            # Preprocessing gambar
            processed_image = preprocess_image(image)
            
            # Simpan gambar sementara untuk debugging (opsional)
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
                processed_image.save(temp_file.name)
                temp_path = temp_file.name
            
            try:
                # Ekstrak teks menggunakan Tesseract OCR
                # Untuk deteksi bahasa otomatis, gunakan: lang='eng+ind'
                extracted_text = pytesseract.image_to_string(
                    processed_image, 
                    lang='eng'  # Bahasa Inggris, ganti dengan 'ind' untuk Indonesia
                )
                
                # Hapus file temp
                os.unlink(temp_path)
                
            except Exception as ocr_error:
                # Hapus file temp jika ada error
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                return jsonify({'error': f'Error OCR: {str(ocr_error)}'}), 500
            
            # Jika tidak ada teks yang terdeteksi
            if not extracted_text.strip():
                return jsonify({'error': 'Tidak ada teks yang terdeteksi dalam gambar. Coba gambar dengan teks lebih jelas.'}), 400
            
            # Bersihkan teks (hapus karakter aneh)
            cleaned_text = re.sub(r'[^\x00-\x7F]+', ' ', extracted_text)
            cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
            
            # Konversi gambar ke base64 untuk preview
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            return jsonify({
                'success': True,
                'text': cleaned_text,
                'image_preview': f"data:image/png;base64,{img_str}",
                'filename': file.filename,
                'char_count': len(cleaned_text)
            })
            
        except Image.UnidentifiedImageError:
            return jsonify({'error': 'File bukan gambar yang valid'}), 400
        except Exception as e:
            print(f"Error processing image: {str(e)}")
            return jsonify({'error': f'Terjadi kesalahan: {str(e)}'}), 500
    
    # Jika method GET, tampilkan halaman utama dengan status Tesseract
    return render_template('index.html', 
                         tesseract_status=tesseract_status,
                         tesseract_message=tesseract_message)

@app.errorhandler(413)
def too_large(e):
    """Handler untuk file yang terlalu besar"""
    return jsonify({'error': 'File terlalu besar. Maksimal 5MB'}), 413

if __name__ == '__main__':
    # Tampilkan informasi status Tesseract saat start
    status, message = check_tesseract_installed()
    print("\n" + "="*60)
    print("STATUS TESSERACT OCR")
    print("="*60)
    
    if status:
        try:
            version = pytesseract.get_tesseract_version()
            print(f"✓ Tesseract ditemukan! Versi: {version}")
            print(f"✓ Path: {pytesseract.pytesseract.tesseract_cmd}")
        except:
            print(f"✓ {message}")
    else:
        print(f"✗ {message}")
        print("\n" + "-"*60)
        print("SOLUSI UNTUK WINDOWS:")
        print("-"*60)
        print("1. Pastikan Tesseract terinstall di: C:\\Program Files\\Tesseract-OCR")
        print("2. Jika terinstall di lokasi lain, ubah path di app.py:")
        print("   pytesseract.pytesseract.tesseract_cmd = r'C:\\Path\\Anda\\tesseract.exe'")
        print("3. Cek apakah file tesseract.exe ada di folder tersebut")
        print("4. Coba path alternatif:")
        print("   - C:\\Program Files\\Tesseract-OCR\\tesseract.exe")
        print("   - C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe")
    
    print("\n" + "="*60)
    print("Aplikasi akan dijalankan di: http://localhost:5000")
    print("="*60 + "\n")
    
    app.run(debug=True, port=5000)
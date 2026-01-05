// Element DOM
const uploadArea = document.getElementById('uploadArea');
const imageInput = document.getElementById('imageInput');
const fileInfo = document.getElementById('fileInfo');
const imagePreview = document.getElementById('imagePreview');
const previewContainer = document.getElementById('previewContainer');
const processBtn = document.getElementById('processBtn');
const resultText = document.getElementById('resultText');
const copyBtn = document.getElementById('copyBtn');
const loading = document.getElementById('loading');
const errorMessage = document.getElementById('errorMessage');
const errorText = document.getElementById('errorText');
const charCount = document.getElementById('charCount');

// State variables
let selectedFile = null;

// Event Listeners
uploadArea.addEventListener('click', () => {
    imageInput.click();
});

imageInput.addEventListener('change', handleFileSelect);

uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.style.borderColor = '#3498db';
    uploadArea.style.backgroundColor = '#f0f7ff';
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.style.borderColor = '#bdc3c7';
    uploadArea.style.backgroundColor = '#f9fafc';
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.style.borderColor = '#bdc3c7';
    uploadArea.style.backgroundColor = '#f9fafc';
    
    if (e.dataTransfer.files.length) {
        handleFile(e.dataTransfer.files[0]);
    }
});

processBtn.addEventListener('click', processImage);
copyBtn.addEventListener('click', copyText);

resultText.addEventListener('input', updateCharCount);

// Fungsi untuk menangani pemilihan file
function handleFileSelect(e) {
    if (e.target.files.length) {
        handleFile(e.target.files[0]);
    }
}

// Fungsi untuk memproses file yang dipilih
function handleFile(file) {
    // Validasi tipe file
    const validTypes = ['image/jpeg', 'image/jpg', 'image/png'];
    if (!validTypes.includes(file.type)) {
        showError('Format file tidak didukung. Gunakan JPG, JPEG, atau PNG.');
        return;
    }
    
    // Validasi ukuran file (maks 5MB)
    if (file.size > 5 * 1024 * 1024) {
        showError('Ukuran file terlalu besar. Maksimal 5MB.');
        return;
    }
    
    selectedFile = file;
    
    // Tampilkan informasi file
    fileInfo.innerHTML = `
        <i class="fas fa-file-image"></i> ${file.name} 
        (${(file.size / 1024).toFixed(2)} KB)
    `;
    fileInfo.style.display = 'block';
    
    // Tampilkan preview gambar
    const reader = new FileReader();
    reader.onload = function(e) {
        imagePreview.innerHTML = `<img src="${e.target.result}" alt="Preview">`;
        previewContainer.style.display = 'block';
    };
    reader.readAsDataURL(file);
    
    // Aktifkan tombol proses
    processBtn.disabled = false;
    hideError();
}

// Fungsi untuk memproses gambar dengan OCR
async function processImage() {
    if (!selectedFile) {
        showError('Silakan pilih gambar terlebih dahulu.');
        return;
    }
    
    // Tampilkan loading
    loading.style.display = 'block';
    processBtn.disabled = true;
    hideError();
    
    // Buat FormData untuk mengirim file
    const formData = new FormData();
    formData.append('image', selectedFile);
    
    try {
        // Kirim request ke server
        const response = await fetch('/', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            // Tampilkan hasil teks
            resultText.value = data.text;
            updateCharCount();
            
            // Update preview gambar jika ada
            if (data.image_preview) {
                imagePreview.innerHTML = `<img src="${data.image_preview}" alt="Processed">`;
            }
            
            // Aktifkan tombol salin
            copyBtn.disabled = false;
            
            // Scroll ke hasil
            resultText.scrollIntoView({ behavior: 'smooth', block: 'center' });
        } else {
            // Tampilkan error dari server
            showError(data.error || 'Terjadi kesalahan saat memproses gambar.');
        }
    } catch (error) {
        console.error('Error:', error);
        showError('Terjadi kesalahan koneksi. Periksa koneksi internet Anda.');
    } finally {
        // Sembunyikan loading
        loading.style.display = 'none';
        processBtn.disabled = false;
    }
}

// Fungsi untuk menyalin teks ke clipboard
function copyText() {
    if (!resultText.value.trim()) {
        showError('Tidak ada teks untuk disalin.');
        return;
    }
    
    // Pilih teks
    resultText.select();
    resultText.setSelectionRange(0, 99999); // Untuk mobile
    
    // Salin ke clipboard
    try {
        const successful = document.execCommand('copy');
        if (successful) {
            // Tampilkan feedback
            const originalText = copyBtn.innerHTML;
            copyBtn.innerHTML = '<i class="fas fa-check"></i> Berhasil Disalin!';
            copyBtn.style.background = 'linear-gradient(to right, #2ecc71, #27ae60)';
            
            setTimeout(() => {
                copyBtn.innerHTML = originalText;
                copyBtn.style.background = 'linear-gradient(to right, #3498db, #2980b9)';
            }, 2000);
        } else {
            showError('Gagal menyalin teks. Coba lagi.');
        }
    } catch (err) {
        // Fallback menggunakan Clipboard API
        navigator.clipboard.writeText(resultText.value).then(() => {
            const originalText = copyBtn.innerHTML;
            copyBtn.innerHTML = '<i class="fas fa-check"></i> Berhasil Disalin!';
            copyBtn.style.background = 'linear-gradient(to right, #2ecc71, #27ae60)';
            
            setTimeout(() => {
                copyBtn.innerHTML = originalText;
                copyBtn.style.background = 'linear-gradient(to right, #3498db, #2980b9)';
            }, 2000);
        }).catch(() => {
            showError('Gagal menyalin teks. Coba manual dengan Ctrl+C.');
        });
    }
}

// Fungsi untuk memperbarui jumlah karakter
function updateCharCount() {
    const count = resultText.value.length;
    charCount.textContent = count;
}

// Fungsi untuk menampilkan error
function showError(message) {
    errorText.textContent = message;
    errorMessage.style.display = 'flex';
    
    // Scroll ke error
    errorMessage.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

// Fungsi untuk menyembunyikan error
function hideError() {
    errorMessage.style.display = 'none';
}

// Inisialisasi
updateCharCount();
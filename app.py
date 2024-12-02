import streamlit as st
import requests
from PIL import Image
from io import BytesIO

# Konfigurasi antarmuka Streamlit
st.title("Image Upscaler")
st.write("Upload gambar Anda untuk meningkatkan resolusi")

# Input untuk API Key
api_key = st.text_input("Masukkan API Key Anda", type="password")

st.link_button("Create API", "https://platform.stability.ai/account/keys")

out_format = st.radio(
    "Pilih format Output",
    ["***jpg***", "***png***", "***webp***"],
    index=1,
)

format_out = "png"
if out_format == "***jpeg***":
    format_out = "jpeg"
elif out_format == "***webp***":
    format_out = "***webp***"
else:
    format_out = "png"

# Upload gambar
uploaded_files = st.file_uploader(
    "Upload file gambar Anda (format: JPG/PNG, maksimal 25 gambar)", 
    type=["jpg", "png"],
    accept_multiple_files=True
)

# Fungsi untuk mengirim gambar ke Stability.ai API
def upscale_image(api_key, image_file, format_out):
    st.write(format_out)
    url = "https://api.stability.ai/v2beta/stable-image/upscale/fast"
    headers = {
        "authorization": f"Bearer {api_key}",
        "accept": "image/*",
    }
    files = {
        "image": image_file,
    }
    data = {
        "output_format": format_out,
    }
    response = requests.post(url, headers=headers, files=files, data=data)
    return response

# Proses gambar saat tombol ditekan
if st.button("Mulai Upscaling"):
    if not api_key:
        st.error("Harap masukkan API Key.")
    elif not uploaded_files:
        st.warning("Silakan upload minimal satu file gambar terlebih dahulu.")
    else:
        st.info("Proses upscaling sedang berjalan...")
        results = []
        for uploaded_file in uploaded_files:
            try:
                # Kirim gambar ke API
                response = upscale_image(api_key, uploaded_file, format_out)
                if response.status_code == 200:
                    # Simpan gambar yang di-*upscale*
                    upscaled_image = Image.open(BytesIO(response.content))
                    results.append(upscaled_image)

                    # Tampilkan gambar
                    st.success(f"Berhasil mengupscale {uploaded_file.name}")
                    st.image(upscaled_image, caption=f"Upscaled: {uploaded_file.name}", use_column_width=True)
                else:
                    st.error(f"Gagal mengupscale {uploaded_file.name}: {response.json().get('message', 'Unknown error')}")
            except Exception as e:
                st.error(f"Error saat memproses {uploaded_file.name}: {e}")

        # Unduh semua hasil sebagai ZIP jika ada hasil yang berhasil
        if results:
            from zipfile import ZipFile
            import os

            zip_file = "upscaled_images.zip"
            with ZipFile(zip_file, "w") as zf:
                for i, img in enumerate(results):
                    img_path = f"upscaled_image_{i + 1}.{format_out}"
                    img.save(img_path, format=format_out)
                    zf.write(img_path)
                    os.remove(img_path)

            with open(zip_file, "rb") as f:
                st.download_button("Unduh Semua Gambar", f, file_name=zip_file)

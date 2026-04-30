import io
import zipfile

zip_buffer = io.BytesIO()
with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
    zip_file.writestr("test.txt", b"Hello")

print("Is closed:", zip_buffer.closed)
zip_buffer.seek(0)
data = zip_buffer.read()
print("Length:", len(data))

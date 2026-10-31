import urllib.request
import ssl
import os

# Fix for Zscaler SSL
ssl_context = ssl.create_default_context()
ssl_context.load_default_certs()
opener = urllib.request.build_opener(
    urllib.request.HTTPSHandler(context=ssl_context)
)
urllib.request.install_opener(opener)

# Create data folders
os.makedirs("data/raw", exist_ok=True)

# ✅ Correct URLs from AWS S3
samples = [
    "http://livecell-dataset.s3.eu-central-1.amazonaws.com/LIVECell_dataset_2021/nuclear_count_benchmark/A172.zip",
]

for url in samples:
    filename = url.split("/")[-1]
    print(f"Downloading {filename}...")
    urllib.request.urlretrieve(url, f"data/raw/{filename}")
    print(f"✅ Saved: data/raw/{filename}")

print("\n🎉 Download complete!")

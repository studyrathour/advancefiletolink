"""
pc_uploader.py — Run this on your PC to:
  1. Download a file from your Render bot stream URL
  2. Upload it to your Hugging Face Space/Dataset
  3. Automatically tell your Render server the new CDN link

Usage:
    python pc_uploader.py <unique_id> <file_url_to_download>

Example:
    python pc_uploader.py abc123xyz https://your-render-app.com/dl/12345/myvideo.mp4

Requirements:
    pip install requests huggingface_hub tqdm
"""

import sys
import os
import requests
from tqdm import tqdm
from huggingface_hub import HfApi

# =====================================================================
# ⚙️  CONFIGURE THESE ONCE
# =====================================================================
RENDER_BASE_URL = "https://your-render-app.onrender.com"  # Your Render app URL
ADMIN_SECRET    = "change_me_in_env"                      # Must match ADMIN_SECRET in Render env vars

HF_TOKEN        = "hf_YOUR_TOKEN_HERE"                    # Your Hugging Face write token
HF_REPO_ID      = "Suraj2008/my-cdn-files"                # HF repo (dataset or model)
HF_REPO_TYPE    = "dataset"                               # "dataset" or "model" or "space"
# =====================================================================


def download_file(url: str, dest_path: str):
    """Stream-download a file from URL to disk with a progress bar."""
    print(f"⬇️  Downloading: {url}")
    with requests.get(url, stream=True, timeout=120) as r:
        r.raise_for_status()
        total = int(r.headers.get("content-length", 0))
        with open(dest_path, "wb") as f, tqdm(total=total, unit="B", unit_scale=True, desc=os.path.basename(dest_path)) as bar:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                f.write(chunk)
                bar.update(len(chunk))
    print(f"✅ Downloaded to: {dest_path}")


def upload_to_hf(local_path: str, filename: str) -> str:
    """Upload a local file to Hugging Face and return the public CDN URL."""
    print(f"⬆️  Uploading to Hugging Face repo: {HF_REPO_ID}")
    api = HfApi(token=HF_TOKEN)
    
    # Upload the file — path_in_repo is the filename inside the HF repo
    api.upload_file(
        path_or_fileobj=local_path,
        path_in_repo=f"files/{filename}",
        repo_id=HF_REPO_ID,
        repo_type=HF_REPO_TYPE,
    )

    # Build the public resolve URL
    cdn_url = f"https://huggingface.co/{HF_REPO_TYPE}s/{HF_REPO_ID}/resolve/main/files/{filename}"
    print(f"✅ Uploaded! CDN URL:\n   {cdn_url}")
    return cdn_url


def notify_server(unique_id: str, filename: str, chat_id: int = None):
    """Tell the Render server about the new HF CDN file (uses just the filename as cdn_path)."""
    print(f"📡 Notifying server for unique_id={unique_id}, file={filename}...")
    endpoint = f"{RENDER_BASE_URL}/admin/update_cdn"
    payload = {
        "unique_id":  unique_id,
        "cdn_path":   filename,       # just the filename stored on HF
        "file_name":  filename,
        "admin_key":  ADMIN_SECRET,
    }
    if chat_id:
        payload["chat_id"] = chat_id  # optional: server will notify user via Telegram
    resp = requests.post(endpoint, json=payload, timeout=30)
    if resp.status_code == 200:
        print(f"✅ Server updated! All future requests for '{unique_id}' will serve from HF CDN.")
    else:
        print(f"❌ Server error {resp.status_code}: {resp.text}")


def main():
    if len(sys.argv) < 3:
        print("Usage: python pc_uploader.py <unique_id> <file_download_url>")
        print("Example: python pc_uploader.py abc123xyz https://your-app.onrender.com/dl/12345/video.mp4")
        sys.exit(1)

    unique_id = sys.argv[1]
    file_url  = sys.argv[2]
    filename  = file_url.split("/")[-1].split("?")[0] or "file"
    local_path = os.path.join(os.getcwd(), filename)

    try:
        # Step 1: Download
        download_file(file_url, local_path)

        # Step 2: Upload to HF
        cdn_url = upload_to_hf(local_path, filename)

        # Step 3: Notify Render server (using just the filename as cdn_path)
        notify_server(unique_id, filename)

    finally:
        # Cleanup local file after upload
        if os.path.exists(local_path):
            os.remove(local_path)
            print(f"🗑️  Cleaned up local file: {local_path}")


if __name__ == "__main__":
    main()

# Deploying to PythonAnywhere

Since **PythonAnywhere** uses WSGI (standard synchronous web servers) and FastAPI is ASGI (asynchronous), we need a bridge. I have added `a2wsgi` to your requirements to handle this.

> [!WARNING]
> **Resource Warning**: The `TinyLlama-1.1B` model requires **~2-3GB of RAM**. PythonAnywhere's **Free Tier** has a limit of 512MB RAM and limited CPU seconds.
> - **Free Tier**: This app will likely **CRASH** or be extremely slow.
> - **Solution**: Use a paid plan, OR switch to a lighter model (like a remote API call to HuggingFace Inference API instead of running local `transformers`).

## Step-by-Step Deployment

### 1. Prepare Your Code
1.  Push your code to GitHub (or upload the zip to PythonAnywhere "Files" tab).
2.  Ensure `wsgi.py` (which I created) is in your project root.
3.  Ensure `requirements.txt` contains `a2wsgi`.

### 2. Set Up PythonAnywhere
1.  Log in to [PythonAnywhere](https://www.pythonanywhere.com/).
2.  Go to **Web** tab -> **Add a new web app**.
3.  Choose **Manual Configuration** (select Python 3.10 or newer).
    *   *Do NOT select Flask/Django presets.*

### 3. Install Dependencies
1.  Open a **Bash Console** on PythonAnywhere.
2.  Create a virtual environment:
    ```bash
    mkvirtualenv myenv --python=/usr/bin/python3.10
    ```
3.  Clone or navigate to your uploaded code:
    ```bash
    cd ~/mysite  # or wherever you put your code
    ```
4.  Install requirements (Use the CPU version of Torch to save space!):
    ```bash
    pip install -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu
    ```

### 4. Configure WSGI File
1.  Go to the **Web** tab.
2.  Scroll to **WSGI configuration file** and click the link to edit it.
3.  **DELETE everything** in that file and paste this:

```python
import sys
import os

# 1. Add your project directory to the sys.path
# Change 'plex_todo_ai' to your actual folder name on PythonAnywhere
path = '/home/yourusername/plex_todo_ai'
if path not in sys.path:
    sys.path.append(path)

# 2. Activate virtualenv (if not handled by Web tab config)
# Usually PythonAnywhere Web tab handles venv if you set "Virtualenv path" there.
# If you used mkvirtualenv, path is usually: /home/yourusername/.virtualenvs/myenv

# 3. Import the WSGI application adapter
from wsgi import application
```

4.  **Save** the file.

### 5. Finalize Web Tab
1.  **Virtualenv**: Enter the path to your virtualenv (e.g., `/home/yourusername/.virtualenvs/myenv`).
2.  **Force HTTPS**: Enable it.
3.  **Reload**: Click the green **Reload** button at the top.

## Troubleshooting

-   **Error Log**: Check the link to the **Error Log** in the Web tab.
-   **Memory Error**: If you see "Killed" or "MemoryError", the model is too big. You must modify `main.py` to use an external API instead of `pipeline()`.

### Code Change for Low RAM (Optional)
If deployment fails due to RAM, change `main.py` to use OpenAI or Hugging Face API:

```python
# Instead of transformers pipeline
import requests

def query_api(prompt):
    API_URL = "https://api-inference.huggingface.co/models/TinyLlama/TinyLlama-1.1B-Chat-v1.0"
    headers = {"Authorization": "Bearer YOUR_HF_TOKEN"}
    response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
    return response.json()
```

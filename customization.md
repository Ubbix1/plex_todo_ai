# Model Customization Guide

This guide explains how to customize the AI model for **Plex ToDo with AI**.

## 1. Prompt Engineering (Easiest)
The most effective way to improve accuracy without changing the model is to edit `prompt.py`.

### How to Edit
Open `prompt.py` and modify `SYSTEM_PROMPT`.
- **Add Examples**: Add more "Input" -> "Output" examples to the `Examples` section.
- **Refine Rules**: If the model ignores a rule (e.g., stops outputting 24-hour time), strictly enforce it in the "Rules" list.

## 2. Changing the Model
The default model is `TinyLlama/TinyLlama-1.1B-Chat-v1.0`. It is small and fast but may lack reasoning capabilities for complex tasks.

### Steps to Switch
1.  Find a model on [Hugging Face](https://huggingface.co/models) (e.g., `microsoft/phi-2`, `meta-llama/Llama-3.3-70B-Instruct`).
2.  Open `main.py`.
3.  Update the `model` argument in the `pipeline` function:

```python
generator = pipeline(
    "text-generation",
    model="meta-llama/Llama-3.3-70B-Instruct:together",  # Change this string
    device_map="auto"
)
```

> **Note**: Larger models require more RAM/VRAM and will run slower on CPUs.

## 3. Fine-Tuning (Advanced)
If prompting isn't enough, you can fine-tune a small model on your specific To-Do data.

1.  **Collect Data**: Create a dataset of 500+ pairs of `(User Input, JSON Output)`.
2.  **Train**: Use libraries like `Unsloth` or `AutoTrain` to fine-tune a Llama-3-8B or Mistral model.
3.  **Export**: Save the model (or LoRA adapter).
4.  **Load**: Point the `model` path in `main.py` to your local folder.

from pathlib import Path
import base64
import ollama
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration

dir_path = Path(__file__).parent
# image_path = dir_path / "drawing-room.jpg"
image_path = dir_path / "latest.jpg"

summary_prompt = """Analyze this image from an academic paper and provide a concise summary in 3-5 sentences.

If this is a data visualization (chart, graph, table, diagram):
- Identify the visualization type and its key components
- Describe the main data represented, including key quantitative values
- Explain the primary trend, comparison, or finding illustrated
- Note any statistical significance or notable outliers

If this is another type of image (photo, micrograph, experimental setup):
- Identify what's depicted and its research context
- Describe key visual features, structures, or components
- Note any visible labels, scale bars, or reference markers
- Explain the scientific relevance or purpose within the research

Use precise, technical language appropriate for academic context. Focus on factual information that would be most relevant for information retrieval."""


def get_base64_image(image_path):
    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read())
    return encoded_image.decode("utf-8")


def summarize_image(image_path):
    # image_base64 = get_base64_image(image_path)
    # image_url = f"data:image/jpeg;base64,{image_base64}"
    response = ollama.chat(
        model="llama3.2-vision",
        messages=[
            {
                "role": "user",
                "content": summary_prompt,
                "images": [image_path],
            }
        ],
    )
    return response["message"]["content"]


if __name__ == "__main__":
    summary = summarize_image(image_path)
    print(summary)

# from unstructured.partition.auto import partition
#
# elements = partition("sample2.pdf")
# print("\n\n".join([str(el) for el in elements]))


from unstructured.partition.pdf import partition_pdf
from pathlib import Path
from pdf_CRUD import get_a_paper, get_url

dir_path = Path(__file__).parent


def chunk_pdf(pdf_path):
    # Reference: https://docs.unstructured.io/open-source/core-functionality/chunking
    chunks = partition_pdf(
        filename=pdf_path,
        chunking_strategy="by_title",  # or 'basic'
        infer_table_structure=True,  # extract tables
        strategy="hi_res",  # mandatory to infer tables
        extract_image_block_types=[
            "Image"
        ],  # Add 'Table' to list to extract image of tables
        extract_image_block_to_payload=True,  # if true, will extract base64 for API usage
        max_characters=10000,  # defaults to 500
        combine_text_under_n_chars=2000,  # defaults to 0
        new_after_n_chars=6000,
    )
    return chunks


if __name__ == "__main__":
    paper = get_a_paper()
    print(paper.title)
    file_path = get_url(paper)
    chunks = partition_pdf(file_path)
    for chunk in chunks:
        if chunk.category == "Image":
            print(chunk)

# SNIPPETS
# Composite elements -- chunk.metadata.orig_elements
# image (i) = chunk[3].metadata.orig_elements[3]
# i.to_dict()['metadata']['image_base64'] <-- the base64 string
#
# with open(image_path, "rb") as image_file:
#        return base64.b64encode(image_file.read()).decode('utf-8')
# response = client.chat.completions.create(
#     model="gpt-4-vision-preview",  # Use the vision-capable model
#     messages=[
#         {
#             "role": "user",
#             "content": [
#                 {"type": "text", "text": "What's in this image?"},
#                 {
#                     "type": "image_url",
#                     "image_url": {
#                         "url": f"data:image/jpeg;base64,{base64_image}"
#                     }
#                 }
#             ]
#         }
#     ],
#     max_tokens=300
# )
# Tables store their data as html in metadata.text_as_html
# Consider DONUT [link](https://github.com/clovaai/donut)
# Summarization of tables, text, and images ("Describe the image in detail. For context, the image is part of a research paper explaining the transformers architecture. Be specific about graphs, such as bar plots.")

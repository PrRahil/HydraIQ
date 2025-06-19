import os
import dotenv
import io
import base64
import tempfile
import fitz
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone
from uuid import uuid4
from langchain_core.documents import Document


dotenv.load_dotenv(".env")

llm = ChatOpenAI(
    model=os.getenv("CHAT_MODEL"),
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key=os.getenv("OPENAI_API_KEY"),
)
embeddings = OpenAIEmbeddings(model=os.getenv("EMBEDDINGS_MODEL"))
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))
vector_store = PineconeVectorStore(index=index, embedding=embeddings)

documents = []

def pdf_page_to_base64(pdf_path: str):
    pdf_document = fitz.open(pdf_path)
    page = pdf_document.load_page(0)
    pix = page.get_pixmap()
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    buffer = io.BytesIO()
    # buffer = os.path.join(os.getenv("OUTPUT_DIR"), f"page_{random.random() + 1}.png")
    img.save(buffer, format="PNG")

    return base64.b64encode(buffer.getvalue()).decode("utf-8")

def process_page_as_pdf(page_pdf):
    print("Processing a virtual PDF of size:", len(page_pdf.getvalue()), "bytes")
    try:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_file.write(page_pdf.getvalue())
            temp_file_path = temp_file.name

        base64_image = pdf_page_to_base64(temp_file_path)

        content=[
            {
              "type": "text",
              "text": "You are a helper who is parsing the content of the PDF. You'll be provided the image of the pages from that PDF. What you have to do is that extract all the information from that image, in a structured way, in markdown format. If there is any image present, you'll provide the description for it. And if there is any table present, you'll extract it in the same format and with the correct data in the markdown format, also provide some description and summary of that table."
            },
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
            },
        ]

        message = HumanMessage(content)

        response = llm.invoke([message])
        document = Document(
            page_content=str(response)
        )
        documents.append(document)
        uuids = [str(uuid4()) for _ in range(len(documents))]
        vector_store.add_documents(documents=documents, ids=uuids)
        documents.clear()

    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

def split_and_process_pdf(input_pdf_path):
    try:
        reader = PdfReader(input_pdf_path)
        total_pages = len(reader.pages)
        # total_pages = 1
        print(f"Total number of pages: {total_pages}")

        for page_num in range(total_pages):
            writer = PdfWriter()
            writer.add_page(reader.pages[page_num])

            virtual_pdf = io.BytesIO()
            writer.write(virtual_pdf)
            virtual_pdf.seek(0)

            process_page_as_pdf(virtual_pdf)

            virtual_pdf.close()

    except Exception as e:
        print(f"An error occurred: {e}")

def get_files():
    folder_path = os.getenv('INPUT_DIR')

    entries = os.listdir(folder_path)

    files = [f for f in entries if os.path.isfile(os.path.join(folder_path, f))]

    return files

def do_the_thing(files):
    for file in files:
        split_and_process_pdf(os.path.join(os.getenv("INPUT_DIR"), file))

files = get_files()
do_the_thing(files)
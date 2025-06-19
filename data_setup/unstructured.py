import os
import dotenv
import io
import tempfile
from PyPDF2 import PdfReader, PdfWriter
from langchain_unstructured import UnstructuredLoader
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone
from uuid import uuid4
from langchain_core.documents import Document

dotenv.load_dotenv(".env")

embeddings = OpenAIEmbeddings(model=os.getenv("EMBEDDINGS_MODEL"))
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))
vector_store = PineconeVectorStore(index=index, embedding=embeddings)

documents = []

def process_page_as_pdf(page_pdf):
    print("Processing a virtual PDF of size:", len(page_pdf.getvalue()), "bytes")
    try:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_file.write(page_pdf.getvalue())
            temp_file_path = temp_file.name

        loader = UnstructuredLoader(
            partition_via_api=True,
            partition_endpoint=os.getenv("UNSTRUCTURED_API_URL"),
            api_key=os.getenv("UNSTRUCTURED_API_KEY"),
            file_path=temp_file_path,
            strategy="hi_res",
            chunking_strategy="by_page",
            max_characters=1000000,
            include_orig_elements=False,
            coordinates=True,
        )

        for document in loader.lazy_load():
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
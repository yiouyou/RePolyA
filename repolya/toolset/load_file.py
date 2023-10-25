from langchain.docstore.document import Document
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.document_loaders import (
    TextLoader,
    BSHTMLLoader,
    PythonLoader,
    PyMuPDFLoader,
    UnstructuredMarkdownLoader,
    UnstructuredWordDocumentLoader,
    UnstructuredPowerPointLoader,
    UnstructuredEmailLoader,
    S3FileLoader,
    S3DirectoryLoader,
)


##### Document
def load_text_to_doc(text: str, metadata: dict = {}):
    doc = Document(
        page_content=text,
        metadata=metadata,
    )
    return doc


##### TextLoader
def load_txt_to_docs(text: str):
    loader = TextLoader(text)
    doc = loader.load()
    return doc


##### PythonLoader
def load_py_to_docs(file_path: str):
    loader = PythonLoader(file_path)
    doc = loader.load()
    return doc


##### PyMuPDFLoader
def load_pdf_to_docs(file_path: str):
    loader = PyMuPDFLoader(file_path)
    doc = loader.load()
    return doc


##### UnstructuredMarkdownLoader
def load_md_to_docs(file_path: str | list[str]):
    loader = UnstructuredMarkdownLoader(file_path)
    docs = loader.load()
    return docs


##### BSHTMLLoader
def load_html_to_docs(file_path: str):
    loader = BSHTMLLoader(file_path)
    doc = loader.load()
    return doc


##### CSVLoader
def load_csv_to_docs(file_path: str, fieldnames: list[str]):
    loader = CSVLoader(
        file_path=file_path,
        csv_args={
            "delimiter": ",",
            "quotechar": '"',
            "fieldnames": fieldnames,
        },
        encoding="utf-8",
    )
    doc = loader.load()
    return doc


##### UnstructuredWordDocumentLoader
def load_docx_to_docs(file_path: str | list[str]):
    loader = UnstructuredWordDocumentLoader(
        file_path=file_path,
        mode="elements",
    )
    docs = loader.load()
    return docs


##### UnstructuredPowerPointLoader
def load_pptx_to_docs(file_path: str | list[str]):
    loader = UnstructuredPowerPointLoader(
        file_path=file_path,
        mode="elements",
    )
    docs = loader.load()
    return docs


##### UnstructuredEmailLoader
def load_eml_to_docs(file_path: str):
    loader = UnstructuredEmailLoader(
        file_path=file_path,
        mode="elements",
        process_attachments=True,
    )
    doc = loader.load()
    return doc


##### S3FileLoader
def load_s3_to_docs(bucket: str, key: str, aws_access_key_id: str, aws_secret_access_key: str):
    loader = S3FileLoader(
        bucket=bucket,
        key=key,
        verify=False,
        aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key,
    )
    docs = loader.load()
    return docs


##### S3DirectoryLoader
def load_s3_dir_to_docs(bucket: str, prefix: str, aws_access_key_id: str, aws_secret_access_key: str):
    loader = S3DirectoryLoader(
        bucket=bucket,
        prefix=prefix,
        verify=False,
        aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key,
    )
    docs = loader.load()
    return docs


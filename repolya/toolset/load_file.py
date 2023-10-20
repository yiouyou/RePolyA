from langchain.docstore.document import Document
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.document_loaders import Docx2txtLoader
from langchain.document_loaders import UnstructuredPowerPointLoader
from langchain.document_loaders import UnstructuredEmailLoader
from langchain.document_loaders import S3FileLoader
from langchain.document_loaders import S3DirectoryLoader


##### Document
def load_text_to_doc(text: str, metadata: dict = {}):
    doc = Document(
        page_content=text,
        metadata=metadata,
    )
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
    docs = loader.load()
    return docs


##### Docx2txtLoader
def load_docx_to_docs(file_path: str):
    loader = Docx2txtLoader(
        file_path=file_path,
    )
    docs = loader.load()
    return docs


##### UnstructuredPowerPointLoader
def load_pptx_to_docs(file_path: str):
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
    docs = loader.load()
    return docs


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


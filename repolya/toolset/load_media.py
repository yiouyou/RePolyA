from langchain.document_loaders import BiliBiliLoader
from langchain.document_loaders import YoutubeLoader
from langchain.document_loaders.generic import GenericLoader
from langchain.document_loaders.parsers import OpenAIWhisperParser, OpenAIWhisperParserLocal
from langchain.document_loaders.blob_loaders.youtube_audio import YoutubeAudioLoader
from langchain.document_loaders import AZLyricsLoader


##### BiliBiliLoader
def load_bilibili_transcript_to_docs(video_urls: str):
    loader = BiliBiliLoader(video_urls)
    docs = loader.load()
    return docs


##### YoutubeLoader
def load_youtube_transcript_to_docs(youtube_url: str):
    loader = YoutubeLoader.from_youtube_url(
        youtube_url=youtube_url,
        add_video_info=True,
        language=["en", "zh"], # Language param : It's a list of language codes in a descending priority, en by default.
        translation="zh", # translation param : It's a translate preference when the youtube does'nt have your select language, en by default.
    )
    docs = loader.load()
    return docs


##### GenericLoader + YoutubeAudioLoader
def load_youtube_audio_to_docs(urls: list[str], save_dir: str):
    loader = GenericLoader(
        YoutubeAudioLoader(urls, save_dir), OpenAIWhisperParser()
    )
    docs = loader.load()
    return docs


##### AZLyricsLoader
def load_azlyrics_to_docs(web_paths: list[str]):
    loader = AZLyricsLoader(
        web_paths=web_paths,
        requests_per_second=2,
    )
    docs = loader.aload()
    return docs


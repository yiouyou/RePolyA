from repolya._const import WORKSPACE_TOOLSET
from repolya._log import logger_toolset

import scrapetube
from youtube_transcript_api import YouTubeTranscriptApi
import os


def save_file(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as outfile:
        outfile.write(content)


def clean_title(title):
    contraband = [':','/','\\','?','"']
    for c in contraband:
        title = title.replace(c,'')
    return title


def download_channel_transcripts(channel_id='UCvKRFNawVcuz4b9ihUTApCg'):
    _out_dp = str(WORKSPACE_TOOLSET / 'youtube_transcripts' / channel_id)
    if not os.path.exists(_out_dp):
        os.makedirs(_out_dp)
    videos = scrapetube.get_channel(channel_id)
    logger_toolset.info(f"videos: {videos}")
    for video in videos:
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video['videoId'])
            text = ['[{} - {}] {}'.format(i['start'], i['start'] + i['duration'], i['text']) for i in transcript]
            block = '\n\n'.join(text)
            title = clean_title(video['title']['runs'][0]['text'])
            logger_toolset.info(title)
            _out_fp = f"{_out_dp}/{title}.txt"
            save_file(_out_fp, block)
        except Exception as oops:
            logger_toolset.error(video['title'], oops)



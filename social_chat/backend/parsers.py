import pandas as pd
import json
import uuid
import os
from datetime import datetime
from bs4 import BeautifulSoup
from typing import Generator
from models import NormalizedDocument

class LinkedInParser:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def parse(self) -> Generator[NormalizedDocument, None, None]:
        
        if not os.path.exists(self.file_path):
            return

        chunksize = 100
        
        try:
            for df_chunk in pd.read_csv(self.file_path, chunksize=chunksize):
                for _, row in df_chunk.iterrows():
                    content = row.get('ShareCommentary', '')
                    if pd.isna(content) or not str(content).strip():
                        continue
                    
                    date_str = row.get('Date', None)
                    created_at = None
                    if not pd.isna(date_str):
                        try:
                            
                            created_at = datetime.fromisoformat(str(date_str).replace(' ', 'T'))
                        except:
                            pass
                            
                    doc = NormalizedDocument(
                        id=str(uuid.uuid4()),
                        platform='linkedin',
                        source_type='post',
                        content=str(content),
                        created_at=created_at,
                        source_file=os.path.basename(self.file_path)
                    )
                    yield doc
        except Exception as e:
            print(f"Error parsing LinkedIn file {self.file_path}: {e}")

class TwitterParser:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def parse(self) -> Generator[NormalizedDocument, None, None]:
        if not os.path.exists(self.file_path):
            return

        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content_str = f.read()
                
                if content_str.startswith('window.YTD'):
                    first_bracket = content_str.find('[')
                    if first_bracket != -1:
                        content_str = content_str[first_bracket:]

                data = json.loads(content_str)
                for item in data:
                    tweet = item.get('tweet', item) 
                    
                    
                    full_text = tweet.get('full_text', tweet.get('text', ''))
                    if full_text.startswith('RT @'):
                        continue
                        
                    date_str = tweet.get('created_at', None)
                    created_at = None
                    if date_str:
                        try:
                            created_at = datetime.strptime(date_str, '%a %b %d %H:%M:%S +0000 %Y')
                        except:
                            pass
                            
                    doc = NormalizedDocument(
                        id=tweet.get('id_str', str(uuid.uuid4())),
                        platform='twitter',
                        source_type='tweet',
                        content=full_text,
                        created_at=created_at,
                        source_file=os.path.basename(self.file_path)
                    )
                    yield doc
        except Exception as e:
            print(f"Error parsing Twitter file {self.file_path}: {e}")

class InstagramParser:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def parse(self) -> Generator[NormalizedDocument, None, None]:
        if not os.path.exists(self.file_path):
            return

        # Instagram can be JSON or HTML
        ext = os.path.splitext(self.file_path)[1].lower()
        if ext == '.json':
            yield from self._parse_json()
        elif ext in ['.html', '.htm']:
            yield from self._parse_html()

    def _parse_json(self):
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                items = data if isinstance(data, list) else data.get('media', [])
                for item in items:
                    title = item.get('title', '')
                    creation_timestamp = item.get('creation_timestamp', None)
                    created_at = datetime.fromtimestamp(creation_timestamp) if creation_timestamp else None
                    
                    if not title.strip():
                        continue
                        
                    doc = NormalizedDocument(
                        id=str(uuid.uuid4()),
                        platform='instagram',
                        source_type='post',
                        content=title,
                        created_at=created_at,
                        source_file=os.path.basename(self.file_path)
                    )
                    yield doc
        except Exception as e:
            print(f"Error parsing Instagram JSON {self.file_path}: {e}")

    def _parse_html(self):
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f, 'html.parser')
                
                
                for div in soup.find_all('div', class_=['_a6-p', '_3-94 _2lem']):
                    content = div.get_text(separator=' ', strip=True)
                    
                    
                    if content and not content.startswith('202'):
                        doc = NormalizedDocument(
                            id=str(uuid.uuid4()),
                            platform='instagram',
                            source_type='post_html',
                            content=content,
                            source_file=os.path.basename(self.file_path)
                        )
                        yield doc
        except Exception as e:
            print(f"Error parsing Instagram HTML {self.file_path}: {e}")

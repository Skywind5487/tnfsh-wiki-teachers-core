from typing import TypeAlias, Dict
from tnfsh_wiki_teachers_core.abc.cache_abc import BaseCacheABC
from tnfsh_wiki_teachers_core.index.crawler import SubjectTeacherMap

class IndexCache(BaseCacheABC):
    

    
    def fetch_from_memory(self, *args, **kwargs):
        return super().fetch_from_memory(*args, **kwargs)
    def save_to_memory(self, data, *args, **kwargs):
        return super().save_to_memory(data, *args, **kwargs)
    def fetch_from_file(self, *args, **kwargs):
        return super().fetch_from_file(*args, **kwargs)
    def save_to_file(self, data, *args, **kwargs):
        return super().save_to_file(data, *args, **kwargs)
    def fetch_from_source(self, *args, **kwargs):
        return super().fetch_from_source(*args, **kwargs)
    def fetch(self, *args, refresh = False, **kwargs):
        return super().fetch(*args, refresh=refresh, **kwargs)

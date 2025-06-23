from __future__ import annotations
from typing import Self, Any, List
from tnfsh_wiki_teachers_core.abc.domain_abc import BaseDomainABC
from pydantic import BaseModel
from tnfsh_wiki_teachers_core.index.crawler import SubjectTeacherMap, SubjectInfo
from tnfsh_wiki_teachers_core.index.cache import ReverseIndexMap, TeacherInfo


class Index(BaseDomainABC, BaseModel):

    index: SubjectTeacherMap | None = None
    reverse_index: ReverseIndexMap | None = None

    @classmethod
    async def fetch(cls, refresh:bool = False, max_concurrency:int = 5, *args: Any, **kwargs:Any) -> Self:
        from tnfsh_wiki_teachers_core.index.cache import IndexCache, ReverseIndexCache
        cache = IndexCache(max_concurrency=max_concurrency)
        reverse_cache = ReverseIndexCache(max_concurrency=max_concurrency)
        index = await cache.fetch(refresh=refresh)
        reverse_index = await reverse_cache.fetch(refresh=refresh)
        instance = cls(index=index, reverse_index=reverse_index)
        return instance
    
    def __getitem__(self, key: str) -> TeacherInfo | SubjectInfo | str:
        """允許使用索引方式存取教師資訊或科目"""
        if self.reverse_index and (result := self.reverse_index.get(key)):
            return result

        if self.index and (result := self.index.get(key)):
            return result

        if self.index:
            # 在index中查找每個老師的url並進行比對
            for _subject, subject_info in self.index.items():
                if key in subject_info.teachers:
                    for teacher, url in subject_info.teachers.items():
                        if key == teacher or key == url:
                            return subject_info.teachers[teacher]
        raise KeyError(f"Item '{key}' not found in index or reverse index.")
    
    def get_all_categories(self) -> List[str]:
        """
        獲取所有教師的分類科目列表
        """
        if self.index is None:
            raise RuntimeError("尚未載入詳細索引資料")
        return list(self.index.keys())
    
    def get_all_teachers(self) -> List[str]:
        """
        獲取所有教師名稱列表
        """
        if self.reverse_index is None:
            raise RuntimeError("尚未載入詳細索引資料")
        return list(self.reverse_index.keys())


if __name__ == "__main__":
    import asyncio
    async def test():
        wiki_index = await Index.fetch()
        index = wiki_index.index
        reverse_index = wiki_index.reverse_index
        import json
        if index:
            print(json.dumps(index.model_dump(), indent=4, ensure_ascii=False))
        print("========")
        if reverse_index:
            print(json.dumps(reverse_index.model_dump(), indent=4, ensure_ascii=False))
    asyncio.run(test())
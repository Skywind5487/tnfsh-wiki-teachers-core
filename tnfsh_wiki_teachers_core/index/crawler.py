from tnfsh_wiki_teachers_core.abc.crawler_abc import BaseCrawlerABC


from abc import ABC
from typing import Any, Dict, List, Tuple, TypeVar, Generic, TypeAlias
from collections import defaultdict
import aiohttp
import asyncio
from aiohttp import ClientSession
from tnfsh_wiki_teachers_core.abc.crawler_abc import BaseCrawlerABC  # 假設你把 BaseCrawlerABC 放在 base.py

T = TypeVar("T")

# Type alias for the final result: {科目: {老師: url}}
SubjectTeacherMap: TypeAlias = Dict[str, Dict[str, str]]

class IndexCrawler(BaseCrawlerABC[SubjectTeacherMap]):
    API = "https://tnfshwiki.tfcis.org/api.php"

    def __init__(self, max_concurrency: int = 5):
        self.semaphore = asyncio.Semaphore(max_concurrency)

    def _get_headers(self) -> Dict[str, str]:
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                           "(KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
            "Accept": "application/json"
        }

    async def _get_subcategories(self, session: ClientSession, cat: str) -> List[str]:
        async with self.semaphore:
            async with session.get(self.API, headers=self._get_headers(), params={
                "action": "query",
                "list": "categorymembers",
                "cmtitle": f"Category:{cat}",
                "cmtype": "subcat",
                "cmlimit": "max",
                "format": "json"
            }) as resp:
                data = await resp.json()
                return [i["title"].split(":", 1)[-1] for i in data.get("query", {}).get("categorymembers", [])]

    async def _get_pages(self, session: ClientSession, cat: str) -> List[str]:
        async with self.semaphore:
            async with session.get(self.API, headers=self._get_headers(), params={
                "action": "query",
                "list": "categorymembers",
                "cmtitle": f"Category:{cat}",
                "cmtype": "page",
                "cmlimit": "max",
                "format": "json"
            }) as resp:
                data = await resp.json()
                return [i["title"] for i in data.get("query", {}).get("categorymembers", [])]

    async def _process_subject(self, session: ClientSession, subject: str) -> Tuple[str, List[str]]:
        subcats = await self._get_subcategories(session, subject)
        if not subcats:
            pages = await self._get_pages(session, subject + "老師")
            return (subject, pages)
        else:
            tasks = [self._get_pages(session, subcat) for subcat in subcats]
            pages_lists = await asyncio.gather(*tasks)
            pages = [page for sublist in pages_lists for page in sublist]
            return (subject, pages)

    async def fetch_raw(self, *args, **kwargs) -> List[Tuple[str, List[str]]]:
        async with aiohttp.ClientSession() as session:
            subjects = await self._get_subcategories(session, "科目")
            all_tasks = [self._process_subject(session, subject) for subject in subjects]
            results = await asyncio.gather(*all_tasks)
            return results

    def parse(self, raw: Any, *args, **kwargs) -> SubjectTeacherMap:
        result: SubjectTeacherMap = defaultdict(dict)
        for subject, teacher_list in raw:
            for teacher in teacher_list:
                result[subject][teacher] = f"/{teacher.replace(' ', '_')}"
        return result

    async def fetch(self, *args, **kwargs) -> SubjectTeacherMap:
        raw = await self.fetch_raw()
        return self.parse(raw)


if __name__ == "__main__":
    async def test():
        crawler = IndexCrawler()
        result = await crawler.fetch()
        return result
    import asyncio
    result = asyncio.run(test())
    import json
    print(json.dumps(result, indent=4, ensure_ascii=False))
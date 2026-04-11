from functools import lru_cache
from rag.retrieve import retrieve_case

@lru_cache(maxsize=100)
def cache_process_query(query):
    print("First time processing query and caching result...")
    return retrieve_case(query)
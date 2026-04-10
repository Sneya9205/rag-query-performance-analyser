from rag.retrieve import retrieve_case

queries = ["Why is SELECT * slow?","How to optimize JSON filtering?","Why memory usage causes slow queries?","Is latency spike abnormal?"]
for query in queries:
    results = retrieve_case(query)

    print("Retrieved Case:\n")

    for r in results:
        print(r)
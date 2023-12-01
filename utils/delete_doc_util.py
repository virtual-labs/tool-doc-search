import json


def delete_document_chunks(urls, qdrant_client, collection_name, record_collection_name, models):
    print("Deleting document chunks")
    qdrant_client.delete(
        collection_name=f"{collection_name}",
        points_selector=models.FilterSelector(
            filter=models.Filter(
                should=[
                    models.FieldCondition(
                        key="base_url",
                        match=models.MatchValue(value=base_url),
                    ) for base_url in urls
                ]
            )
        ),
    )
    print("Documents deleted")
    print("Deleting records")
    delete_entry(urls, models, qdrant_client, record_collection_name)
    print("Records deleted")
    resultObj = {
        "message": f"Document{'s' if len(urls) > 1 else ''} deleted successfully", "result": urls}
    print(json.dumps(resultObj, indent=4))
    return resultObj


def delete_entry(docs, models, qdrant_client, record_collection_name):
    print("Deleting entries in Record DB")
    try:
        if len(docs):
            qdrant_client.delete(
                collection_name=f"{record_collection_name}",
                points_selector=models.FilterSelector(
                    filter=models.Filter(
                        should=[
                            models.FieldCondition(
                                key="base_url",
                                match=models.MatchValue(
                                    value=doc),
                            ) for doc in docs
                        ]
                    )
                ),
            )
            print("Records")
            print(json.dumps(
                docs, indent=4))
            print("Deleted records")
            return "success"
        else:
            raise Exception("No valid document.")
    except Exception as e:
        raise e

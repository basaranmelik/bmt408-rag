from fastapi import APIRouter, Query
from services.query_service import list_collections, get_collection_stats, query_collection,delete_collection

router = APIRouter()

@router.get("/collections")
def collections(): 
    return list_collections()

@router.get("/collection/{collection_name}/stats")
def collection_stats(collection_name: str):
    return get_collection_stats(collection_name)

@router.get("/query")
def query(
    collection_name: str = Query(...),
    query_text: str = Query(...),
    top_k: int = Query(3)
):
    return query_collection(collection_name, query_text, top_k)

@router.delete("/collections/{collection_name}")
def delete_vector_collection(collection_name: str):
    return delete_collection(collection_name)
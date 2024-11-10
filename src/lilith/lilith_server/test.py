# from fastapi import FastAPI, HTTPException
# from neo4j import AsyncGraphDatabase
# import os

# app = FastAPI()

# NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
# NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
# NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

# driver = AsyncGraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


# @app.on_event("shutdown")
# async def shutdown_event():
#     await driver.close()


# @app.get("/neo4j/test")
# async def test_neo4j():
#     try:
#         async with driver.session() as session:
#             result = await session.run(
#                 "RETURN 'Neo4j Connection Successful!' AS message"
#             )
#             record = await result.single()
#             return {"message": record["message"]}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))



# def query(q: LiteralString) -> LiteralString:
#     # this is a safe transform:
#     # no way for cypher injection by trimming whitespace
#     # hence, we can safely cast to LiteralString
#     return cast(LiteralString, dedent(q).strip())


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     driver = AsyncGraphDatabase.driver(url, auth=(username, password))
#     shared_context["driver"] = driver
#     yield
#     await driver.close()


# def get_driver() -> neo4j.AsyncDriver:
#     return shared_context["driver"]


# app = FastAPI(lifespan=lifespan)


# @app.get("/")
# async def get_index():
#     return FileResponse(os.path.join(PATH, "static", "index.html"))


# def serialize_movie(movie):
#     return {
#         "id": movie["id"],
#         "title": movie["title"],
#         "summary": movie["summary"],
#         "released": movie["released"],
#         "duration": movie["duration"],
#         "rated": movie["rated"],
#         "tagline": movie["tagline"],
#         "votes": movie.get("votes", 0)
#     }


# def serialize_cast(cast):
#     return {
#         "name": cast[0],
#         "job": cast[1],
#         "role": cast[2]
#     }


# @app.get("/graph")
# async def get_graph(limit: int = 100):
#     records, _, _ = await get_driver().execute_query(
#         query("""
#             MATCH (m:Movie)<-[:ACTED_IN]-(a:Person)
#             RETURN m.title AS movie, collect(a.name) AS cast
#             LIMIT $limit
#         """),
#         database_=database,
#         routing_="r",
#         limit=limit,
#     )
#     nodes = []
#     rels = []
#     i = 0
#     for record in records:
#         nodes.append({"title": record["movie"], "label": "movie"})
#         target = i
#         i += 1
#         for name in record["cast"]:
#             actor = {"title": name, "label": "actor"}
#             try:
#                 source = nodes.index(actor)
#             except ValueError:
#                 nodes.append(actor)
#                 source = i
#                 i += 1
#             rels.append({"source": source, "target": target})
#     return {"nodes": nodes, "links": rels}


# @app.get("/search")
# async def get_search(q: Optional[str] = None):
#     if q is None:
#         return []
#     records, _, _ = await get_driver().execute_query(
#         query("""
#             MATCH (movie:Movie)
#             WHERE toLower(movie.title) CONTAINS toLower($title)
#             RETURN movie
#         """),
#         title=q,
#         database_=database,
#         routing_="r",
#     )
#     return [serialize_movie(record["movie"]) for record in records]


# @app.get("/movie/{title}")
# async def get_movie(title: str):
#     result = await get_driver().execute_query(
#         query("""
#             MATCH (movie:Movie {title:$title})
#             OPTIONAL MATCH (movie)<-[r]-(person:Person)
#             RETURN movie.title as title,
#             COLLECT(
#                 [person.name, HEAD(SPLIT(TOLOWER(TYPE(r)), '_')), r.roles]
#             ) AS cast
#             LIMIT 1
#         """),
#         title=title,
#         database_=database,
#         routing_="r",
#         result_transformer_=neo4j.AsyncResult.single,
#     )
#     if result is None:
#         raise HTTPException(status_code=404, detail="Movie not found")

#     return {"title": result["title"],
#             "cast": [serialize_cast(member)
#                      for member in result["cast"]]}


# @app.post("/movie/{title}/vote")
# async def vote_in_movie(title: str):
#     summary = await get_driver().execute_query(
#         query("""
#             MATCH (m:Movie {title: $title})
#             SET m.votes = coalesce(m.votes, 0) + 1;
#         """),
#         database_=database,
#         title=title,
#         result_transformer_=neo4j.AsyncResult.consume,
#     )
#     updates = summary.counters.properties_set

#     return {"updates": updates}


# if __name__ == "__main__":
#     import uvicorn

#     logging.root.setLevel(logging.INFO)
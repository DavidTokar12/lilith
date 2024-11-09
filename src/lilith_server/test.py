from fastapi import FastAPI, HTTPException
from neo4j import AsyncGraphDatabase
import os

app = FastAPI()

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://host.docker.internal:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

driver = AsyncGraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


@app.on_event("shutdown")
async def shutdown_event():
    await driver.close()


@app.get("/neo4j/test")
async def test_neo4j():
    try:
        async with driver.session() as session:
            result = await session.run(
                "RETURN 'Neo4j Connection Successful!' AS message"
            )
            record = await result.single()
            return {"message": record["message"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

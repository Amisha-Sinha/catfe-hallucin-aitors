from pymongo import MongoClient
from langchain.tools import StructuredTool
from pydantic import BaseModel, Field
from sentence_transformers import SentenceTransformer
import numpy as np
import datetime
import os
from bson import ObjectId 


# ------------------
# Configuration Schema
# ------------------
class DatabaseConfig(BaseModel):
    payments_uri: str = Field(default=os.getenv("MONGO_A_URI"), 
                            description="MongoDB URI for payments backend")
    memories_uri: str = Field(default=os.getenv("MONGO_B_URI"), 
                            description="MongoDB URI for memory storage")

# ------------------
# Core Implementation
# ------------------
class MemoryTools:
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.embedder = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
        self._init_clients()
    
    def _init_clients(self):
        """Initialize MongoDB connections with pooling"""
        self.payments_client = MongoClient(
            self.config.payments_uri,
            maxPoolSize=10,
            serverSelectionTimeoutMS=5000
        )
        self.memories_client = MongoClient(
            self.config.memories_uri,
            maxPoolSize=10,
            serverSelectionTimeoutMS=5000
        )
        
        # Verify connections
        try:
            self.payments_client.list_database_names()
            self.memories_client.list_database_names()
        except Exception as e:
            raise ConnectionError(f"MongoDB connection failed: {e}")

    # ------------------
    # Tool Schemas
    # ------------------
    class NoInputSchema(BaseModel):
        pass

    class RecordMemorySchema(BaseModel):
        input_str: str = Field(..., description="The information to remember")

    class RecallMemorySchema(BaseModel):
        query_str: str = Field(..., description="The query to search memories")
        top_k: int = Field(3, description="Number of results to return")
        
    class UpdateMemorySchema(BaseModel):
        memory_id: str = Field(..., description="The ID of the memory to update")
        input_str: str = Field(..., description="The new information to replace the existing memory")


    # ------------------
    # Core Operations
    # ------------------
    def fetch_all(self) -> list:
        """Fetch all records from payments database"""
        try:
            db = self.payments_client["payments-backend"]
            return list(db.accounts.find({}))
        except Exception as e:
            print(f"Fetch error: {e}")
            return []

    def record_memory(self, input_str: str) -> str:
        """Store memory with embedding"""
        try:
            db = self.memories_client["smart_stubs_db"]
            collection = db.memories
            
            embedding = self.embedder.encode(input_str).tolist()
            doc = {
                "text": input_str,
                "embedding": embedding,
                "timestamp": datetime.datetime.utcnow()
            }
            
            return str(collection.insert_one(doc).inserted_id)
        except Exception as e:
            print(f"Record error: {e}")
            return ""

    def recall_memory(self, query_str: str, top_k: int = 3) -> list:
        """Find relevant memories using cosine similarity"""
        try:
            db = self.memories_client["smart_stubs_db"]
            collection = db.memories
            
            query_embedding = self.embedder.encode(query_str)
            all_memories = list(collection.find({}))
            
            similarities = []
            for memory in all_memories:
                mem_embedding = np.array(memory["embedding"])
                similarity = np.dot(query_embedding, mem_embedding)
                similarities.append((memory["text"], similarity, memory["_id"]))
            
            sorted_memories = sorted(similarities, key=lambda x: x[1], reverse=True)
            return [{"text": text, "id": str(mem_id)} for text, _, mem_id in sorted_memories[:top_k]]
        except Exception as e:
            print(f"Recall error: {e}")
            return []

    def update_memory(self, memory_id: str, input_str: str) -> bool:
        """Update existing memory with new content and embedding"""
        try:
            db = self.memories_client["smart_stubs_db"]
            collection = db.memories

            new_embedding = self.embedder.encode(input_str).tolist()
            
            result = collection.update_one(
                {"_id": ObjectId(memory_id)},
                {
                    "$set": {
                        "text": input_str,
                        "embedding": new_embedding,
                        "timestamp": datetime.datetime.utcnow()
                    }
                }
            )
            return result.modified_count == 1
        except Exception as e:
            print(f"Update error: {e}")
            return False

    # ------------------
    # Tool Generation
    # ------------------
    def generate_tools(self):
        return [
            StructuredTool.from_function(
                self.fetch_all,
                name="FetchAllAccounts",
                description="Fetches all records from payments-backend.accounts collection",
                args_schema=self.NoInputSchema
            ),
            StructuredTool.from_function(
                self.record_memory,
                name="RecordMemory",
                description="EXCLUSIVELY USE THIS TO STORE NEW INFORMATION. Input format: exact text to remember and the context around it so that you can recall it later",
                args_schema=self.RecordMemorySchema
            ),
            StructuredTool.from_function(
                self.recall_memory,
                name="RecallMemory",
                description="MUST USE FIRST FOR ANY QUESTION. This tool retrieves stored memories that match the provided query, ensuring relevant information is surfaced efficiently.",
                args_schema=self.RecallMemorySchema
            ),
            StructuredTool.from_function(
                self.update_memory,
                name="UpdateMemory",
                description="Updates an existing memory by providing the memory ID to be retrieved fromRecallMemory and the new content.",
                args_schema=self.UpdateMemorySchema
            )
        ]

    def _del_(self):
        """Cleanup connections"""
        self.payments_client.close()
        self.memories_client.close()

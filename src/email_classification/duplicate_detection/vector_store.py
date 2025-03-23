"""Vector storage and similarity search for emails."""

from typing import Dict, List, Tuple, Optional, Any
import logging
import os
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import json
import pickle

logger = logging.getLogger(__name__)

class EmailVectorStore:
    """Vector storage and similarity search for emails."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the vector store.
        
        Args:
            model_name: Name of the sentence transformer model to use
        """
        self.model = SentenceTransformer(model_name)
        self.vector_dimension = self.model.get_sentence_embedding_dimension()
        self.index = None
        self.email_ids = []
        self.email_contents = {}
        self.store_path = "./vector_store"
        self._init_store()
    
    def _init_store(self) -> None:
        """Initialize the vector store from disk or create a new one."""
        os.makedirs(self.store_path, exist_ok=True)
        index_path = os.path.join(self.store_path, "faiss_index.bin")
        metadata_path = os.path.join(self.store_path, "email_metadata.pkl")
        
        if os.path.exists(index_path) and os.path.exists(metadata_path):
            try:
                self.index = faiss.read_index(index_path)
                with open(metadata_path, 'rb') as f:
                    metadata = pickle.load(f)
                    self.email_ids = metadata.get('email_ids', [])
                    self.email_contents = metadata.get('email_contents', {})
                logger.info(f"Loaded vector store with {len(self.email_ids)} emails")
            except Exception as e:
                logger.error(f"Error loading vector store: {str(e)}")
                self._create_new_index()
        else:
            self._create_new_index()
    
    def _create_new_index(self) -> None:
        """Create a new FAISS index."""
        self.index = faiss.IndexFlatL2(self.vector_dimension)
        self.email_ids = []
        self.email_contents = {}
        logger.info("Created new vector store")
    
    def add_email(self, email, request_type: str, extracted_fields: Dict[str, Any]) -> None:
        """
        Add an email to the vector store.
        
        Args:
            email: EmailContent object
            request_type: Classified request type
            extracted_fields: Dictionary of extracted fields
        """
        # Generate a unique ID for the email
        email_id = f"{len(self.email_ids) + 1}_{email.subject.replace(' ', '_')[:30]}"
        
        if email_id in self.email_ids:
            logger.warning(f"Email {email_id} already exists in vector store")
            return
        
        # Extract the text for embedding
        text_for_embedding = self._prepare_text_for_embedding(email)
        
        # Generate embedding
        embedding = self.model.encode([text_for_embedding])[0]
        embedding_array = np.array([embedding]).astype('float32')
        
        # Add to index
        self.index.add(embedding_array)
        self.email_ids.append(email_id)
        
        # Store content for later comparison
        self.email_contents[email_id] = {
            'subject': email.subject,
            'from_address': email.from_address,
            'date': email.date,
            'plain_text': email.plain_text,
            'request_type': request_type,
            'extracted_fields': extracted_fields
        }
        
        logger.info(f"Added email {email_id} to vector store")
    
    def _prepare_text_for_embedding(self, email) -> str:
        """Prepare email text for embedding."""
        text_parts = []
        
        text_parts.append(f"Subject: {email.subject}")
        text_parts.append(f"From: {email.from_address}")
        text_parts.append(f"Date: {email.date}")
        
        # Add the email body
        text_parts.append(email.plain_text)
        
        return "\n".join(text_parts)
    
    def find_similar_emails(
        self, 
        email,
        top_k: int = 5,
        threshold: float = 0.9
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        Find similar emails in the vector store.
        
        Args:
            email: EmailContent object to compare
            top_k: Number of similar emails to return
            threshold: Similarity threshold (0-1)
            
        Returns:
            List of tuples with similar emails and scores
        """
        if not self.index or self.index.ntotal == 0:
            logger.warning("Vector store is empty")
            return []
        
        # Extract the text for embedding
        text_for_embedding = self._prepare_text_for_embedding(email)
        
        # Generate embedding
        embedding = self.model.encode([text_for_embedding])[0]
        embedding_array = np.array([embedding]).astype('float32')
        
        # Search in the index
        k = min(top_k, len(self.email_ids))
        if k == 0:
            return []
            
        distances, indices = self.index.search(embedding_array, k)
        
        # Process results
        results = []
        for i in range(len(indices[0])):
            idx = indices[0][i]
            distance = distances[0][i]
            
            # Convert distance to similarity score (0-1)
            # FAISS L2 distance is smaller for more similar items,
            # so we convert it to a similarity score
            similarity = 1.0 - min(distance / 100.0, 1.0)
            
            if similarity >= threshold:
                email_id = self.email_ids[idx]
                results.append((self.email_contents[email_id], similarity))
        
        return results
    
    def save(self) -> None:
        """Save the vector store to disk."""
        try:
            os.makedirs(self.store_path, exist_ok=True)
            index_path = os.path.join(self.store_path, "faiss_index.bin")
            metadata_path = os.path.join(self.store_path, "email_metadata.pkl")
            
            # Save FAISS index
            faiss.write_index(self.index, index_path)
            
            # Save metadata
            metadata = {
                'email_ids': self.email_ids,
                'email_contents': self.email_contents
            }
            with open(metadata_path, 'wb') as f:
                pickle.dump(metadata, f)
            
            logger.info(f"Saved vector store with {len(self.email_ids)} emails")
        except Exception as e:
            logger.error(f"Error saving vector store: {str(e)}")
    
    def clear(self) -> None:
        """Clear the vector store."""
        self._create_new_index()
        self.save()
        logger.info("Cleared vector store")
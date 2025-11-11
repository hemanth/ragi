"""Retrieval and answer generation using OpenAI-compatible APIs."""

import os
from typing import List, Optional

from openai import OpenAI

from .types import Answer, Citation


class Retriever:
    """Generate answers from retrieved chunks using OpenAI-compatible LLM APIs."""

    def __init__(
        self,
        model: str = "llama3.2",
        api_key: str | None = None,
        base_url: str | None = None,
    ) -> None:
        """
        Initialize the retriever.

        Args:
            model: Model name to use (default: llama3.2 for Ollama)
            api_key: API key (optional for local models like Ollama)
            base_url: Base URL for OpenAI-compatible API (e.g., http://localhost:11434/v1 for Ollama)
        """
        self.model = model

        # Default to Ollama if no base_url provided
        if base_url is None:
            base_url = os.getenv("LLM_BASE_URL", "http://localhost:11434/v1")

        # API key is optional for local models
        if api_key is None:
            api_key = os.getenv("LLM_API_KEY", "not-needed")

        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
        )

    def generate_answer(
        self,
        query: str,
        citations: List[Citation],
        system_prompt: Optional[str] = None,
    ) -> Answer:
        """
        Generate an answer from retrieved citations.

        Args:
            query: User's question
            citations: Retrieved citations
            system_prompt: Optional custom system prompt

        Returns:
            Answer with citations
        """
        if not citations:
            return Answer(
                text="I couldn't find any relevant information to answer your question.",
                citations=[],
                query=query,
            )

        # Build context from citations
        context = self._build_context(citations)

        # Generate answer
        answer_text = self._generate_with_llm(query, context, system_prompt)

        return Answer(
            text=answer_text,
            citations=citations,
            query=query,
        )

    def _build_context(self, citations: List[Citation]) -> str:
        """Build context string from citations."""
        context_parts = []

        for i, citation in enumerate(citations, 1):
            source_info = f"Source {i} ({citation.source}):"
            context_parts.append(f"{source_info}\n{citation.chunk}\n")

        return "\n".join(context_parts)

    def _generate_with_llm(
        self,
        query: str,
        context: str,
        system_prompt: Optional[str] = None,
    ) -> str:
        """Generate answer using OpenAI-compatible API."""
        if system_prompt is None:
            system_prompt = (
                "You are a helpful assistant that answers questions based on the provided context. "
                "Always cite your sources by mentioning which source number you're referring to. "
                "If the context doesn't contain enough information to answer the question, say so. "
                "Be concise and accurate."
            )

        user_prompt = f"""Context from documents:

{context}

Question: {query}

Please answer the question based on the context provided above. Cite your sources."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,
            )

            return response.choices[0].message.content or ""

        except Exception as e:
            raise RuntimeError(f"Failed to generate answer: {e}")

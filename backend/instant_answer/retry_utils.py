"""
Retry utilities for Instant Answer Recall System.

This module provides retry logic and timeout handling for ChromaDB operations
and other async operations that may fail transiently.

Requirements: 8.2, 8.4
"""

import logging
import asyncio
from typing import TypeVar, Callable, Any
from functools import wraps

logger = logging.getLogger(__name__)

T = TypeVar('T')


async def retry_with_backoff(
    func: Callable[..., T],
    *args,
    max_retries: int = 1,
    initial_delay: float = 0.5,
    operation_name: str = "operation",
    **kwargs
) -> T:
    """
    Retry an async function with exponential backoff.
    
    This utility implements retry logic for operations that may fail transiently,
    such as ChromaDB queries or API calls.
    
    Args:
        func: The async function to retry
        *args: Positional arguments to pass to func
        max_retries: Maximum number of retries (default: 1 for ChromaDB)
        initial_delay: Initial delay in seconds (default: 0.5)
        operation_name: Name of operation for logging
        **kwargs: Keyword arguments to pass to func
    
    Returns:
        Result from successful function call
    
    Raises:
        Exception: The last exception if all retries fail
    
    Requirements: 8.2
    """
    last_error = None
    
    for attempt in range(max_retries + 1):
        try:
            result = await func(*args, **kwargs)
            
            if attempt > 0:
                logger.info(
                    f"{operation_name} succeeded on attempt {attempt + 1}/{max_retries + 1}"
                )
            
            return result
        
        except Exception as e:
            last_error = e
            logger.warning(
                f"{operation_name} failed on attempt {attempt + 1}/{max_retries + 1}: {e}"
            )
            
            # Check if we should retry
            if attempt < max_retries:
                # Exponential backoff
                delay = initial_delay * (2 ** attempt)
                logger.info(f"Retrying {operation_name} in {delay}s...")
                await asyncio.sleep(delay)
            else:
                # Final attempt failed
                logger.error(
                    f"{operation_name} failed after {max_retries + 1} attempts: {last_error}"
                )
                raise last_error


async def with_timeout(
    func: Callable[..., T],
    *args,
    timeout: float,
    operation_name: str = "operation",
    **kwargs
) -> T:
    """
    Execute an async function with a timeout.
    
    Args:
        func: The async function to execute
        *args: Positional arguments to pass to func
        timeout: Timeout in seconds
        operation_name: Name of operation for logging
        **kwargs: Keyword arguments to pass to func
    
    Returns:
        Result from successful function call
    
    Raises:
        asyncio.TimeoutError: If operation exceeds timeout
    
    Requirements: 8.4
    """
    try:
        result = await asyncio.wait_for(func(*args, **kwargs), timeout=timeout)
        return result
    
    except asyncio.TimeoutError:
        logger.error(f"{operation_name} timed out after {timeout}s")
        raise


def chromadb_retry(max_retries: int = 1, initial_delay: float = 0.5):
    """
    Decorator for ChromaDB operations with retry logic.
    
    This decorator wraps ChromaDB operations to automatically retry on failure
    with exponential backoff. ChromaDB operations get 1 retry by default.
    
    Args:
        max_retries: Maximum number of retries (default: 1)
        initial_delay: Initial delay in seconds (default: 0.5)
    
    Returns:
        Decorated function with retry logic
    
    Requirements: 8.2
    
    Example:
        @chromadb_retry(max_retries=1)
        async def query_chromadb(self, query_embedding):
            return self.collection.query(query_embeddings=[query_embedding])
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await retry_with_backoff(
                func,
                *args,
                max_retries=max_retries,
                initial_delay=initial_delay,
                operation_name=func.__name__,
                **kwargs
            )
        return wrapper
    return decorator


def gemini_retry(max_retries: int = 2, initial_delay: float = 1.0):
    """
    Decorator for Gemini API operations with retry logic.
    
    This decorator wraps Gemini API calls to automatically retry on failure
    with exponential backoff. Gemini operations get 2 retries by default.
    
    Args:
        max_retries: Maximum number of retries (default: 2)
        initial_delay: Initial delay in seconds (default: 1.0)
    
    Returns:
        Decorated function with retry logic
    
    Requirements: 8.1
    
    Example:
        @gemini_retry(max_retries=2)
        async def classify_message(self, message):
            return await self.gemini_service.generate_content(prompt)
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await retry_with_backoff(
                func,
                *args,
                max_retries=max_retries,
                initial_delay=initial_delay,
                operation_name=func.__name__,
                **kwargs
            )
        return wrapper
    return decorator

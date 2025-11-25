"""
Utility functions for parallel processing and common operations.
"""
import concurrent.futures
from typing import Callable, List, Any


def run_in_parallel(task_func: Callable, items: List[Any], max_workers: int = 10) -> List[Any]:
    """
    Execute a function in parallel across multiple items.
    
    Args:
        task_func: The function to execute for each item
        items: List of items to process
        max_workers: Maximum number of parallel workers (default: 10)
    
    Returns:
        List of results from successful executions
    """
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_item = {executor.submit(task_func, item): item for item in items}
        for future in concurrent.futures.as_completed(future_to_item):
            try:
                result = future.result()
                if result:
                    results.append(result)
            except Exception as e:
                item = future_to_item[future]
                print(f"Error processing item {item}: {e}")
    return results

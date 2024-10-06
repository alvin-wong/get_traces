import asyncio
import aiohttp
import time
from datetime import datetime

# Configuration
API_URL = "https://jsonplaceholder.typicode.com/posts/1"
TOTAL_REQUESTS = 10  # Increased to demonstrate concurrency control
INTERVAL_SECONDS = 1
MAX_CONCURRENT_REQUESTS = 5

async def fetch(session, url, request_id):
    async with session.get(url) as response:
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = await response.json()
        await asyncio.sleep(10)
        print(f"Request {request_id}: Success")
        return data

async def limited_task_runner():
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
    async with aiohttp.ClientSession() as session:
        tasks = []

        # Limit the creation of tasks directly by using the semaphore
        for i in range(1, TOTAL_REQUESTS + 1):
            # Wait for a slot to be available
            await semaphore.acquire()
            
            # Define a wrapper to release the semaphore after task completion
            async def sem_task(i):
                try:
                    return await fetch(session, API_URL, i)
                finally:
                    semaphore.release()

            # Schedule the task
            print(f"Scheduled request {i}")
            tasks.append(asyncio.create_task(sem_task(i)))

            await asyncio.sleep(INTERVAL_SECONDS)

        print("DONE scheduling tasks")
        responses = await asyncio.gather(*tasks)

        # Process the responses as needed
        successful_responses = [resp for resp in responses if resp is not None]
        print(f"Total successful responses: {len(successful_responses)}")

if __name__ == "__main__":
    print(f"Starting the asynchronous API calls...")
    asyncio.run(limited_task_runner())
    print(f"All tasks completed")

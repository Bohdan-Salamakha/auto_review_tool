# **AutoReviewTool**

AutoReviewTool is a library for code review using FastAPI.

It includes the ability to launch a server to handle requests.

## **Environment variables**

For AutoReviewTool to work, you need to set up environment variables:

Create an `.env` file in the root of the project, similar to .env.sample
and put your environment variables there:

1. GITHUB_TOKEN
* Description: Token for authentication in the GitHub API.
* What it is used for: Used to access the contents of GitHub repositories.
* Example value:
`GITHUB_TOKEN=ghp_your_github_token`

2. OPENAI_API_KEY
* Description: API key to access the OpenAI GPT API.
* What it does: Used to analyze code and generate reports.
* Example value:
`OPENAI_API_KEY=sk-your_openai_key`

3. REDIS_URL (optional)
* Description: URL to connect to Redis.
* What it does: Used to cache requests to the GitHub and OpenAI API, which reduces the load on the API and improves performance.
* Example value:
`REDIS_URL=redis://localhost:6379/0`
* If REDIS_URL is not specified or the connection fails, the application will continue to run without Redis, but caching will be disabled.

## **Starting the server using a Docker (Option 1)**

1. Make sure you have Docker and Docker Compose installed.
2. Open a terminal and navigate to the project folder.
3. Run Docker Compose:

`docker compose up`

4. Access the application:

`http://localhost:8000`

## **Starting the server using virtual environment (Option 2)**

Make sure Python version 3.13 or higher is installed on your system.

Install required libs into your virtual environment 
(it's better to use poetry)

1. Install poetry if it's not installed

`pip install poetry`

2. Install required libs

`poetry install`

After installing libs, you can start the FastAPI server with the command:

```poetry run uvicorn auto_review_tool.main:app --reload```

to run server in the development mode

or

```poetry run uvicorn auto_review_tool.main:app --host 0.0.0.0 --port 8000 --workers 4```

to run server in the production mode

The server will be launched by default at http://0.0.0.0:8000.

#### **Available options**

You can configure the server startup by passing the following parameters:
* `--host`

Description: Specify the host on which the server will be started.

Default: 0.0.0.0

Example:

`auto-review-tool runprod --host 127.0.0.1`

* `--port`

Description: Specify the port on which the server will run.

Default: 8000

Example:

`auto-review-tool runprod --port 8080`

* `--workers`

Description: Number of workers (parallel processes) to handle requests.

Default: 4

Example:

`auto-review-tool runprod --workers 2`

* `--reload`

Description: Automatically restarts the server when code changes (recommended for development only).

Default: False

Example:

`auto-review-tool runprod --reload`

## **API Documentation**

Once the server is running, you can open the API documentation in your browser at:

`http://<host>:<port>/docs`

Example for default settings:

`http://0.0.0.0:8000/docs`

# **Part 2 — What If**

## 1. *Large repositories with 100+ files in them?*

GitHub will not allow us to get more than 1000 files in one request, and if there are more in the repository, we will have to deal with pagination.

It is better to use asynchronous requests. 

They will allow you to download data faster, without waiting for each request to complete.

Another difficulty is downloading a large number of files.

If we start downloading them sequentially, the time to process the repository will increase many times.

Therefore, it is important to set up parallel downloading.

The asyncio library comes in handy here, which allows you to limit the number of simultaneously sent requests so that we do not block ourselves according to GitHub limits.

Another problem that can be encountered is large files.

There are situations when the repository contains files several megabytes in size.

If we send them to the OpenAI API as is, we will simply exceed the limits on the number of tokens.

To avoid this, you can do preliminary filtering. For example, do not process files larger than 1 MB unless they are clearly critical.

And if the file is still important, it can be split into parts and processed in parts.

This approach helps to neatly bypass OpenAI's limitations while maintaining the usefulness of the analysis.

As for storing results and optimization, Redis is a great help here.

For example, you can cache the contents of files or analysis results so as not to repeat the same work.

This is especially useful if the repository is being analyzed more than once, or when we are working with large volumes of requests.

When there are a lot of repositories or requests, processing them all at once begins to take too much time.

Task queues can help here.

Imagine that there is a service that receives a request to analyze a repository, but instead of immediately starting processing, it adds a task to a queue.

Then, individual Celery-based workers take tasks from this queue and execute them.

This approach allows you to distribute the load and process repositories in parallel.

When it comes to infrastructure scaling, Kubernetes is a great choice.

For example, you can set up autoscaling so that additional service instances are automatically created when the load increases.

And to monitor the entire system, you can use a combination of Prometheus and Grafana to track request processing time and the state of task queues.

## 2. *100+ new review requests per minute?*

The first thing to consider is the limit on simultaneous connections.

If many clients start sending requests at the same time, the server may simply not be able to cope.

This is where rate limiters come in.

For example, you can set it so that one client can send no more than 10 requests per minute.

However, rate limiting alone is not enough.

Even with such restrictions, too many requests still come to the server.

Then they need to be processed, but in a way that does not overload the resources.

Task queues, such as Celery or Redis Queue, are well suited for this.

When a request comes to the server, its processing does not begin immediately — it is added to the queue.

The workers working in parallel take tasks from this queue and execute them.

This approach allows the server to respond to the client quickly, even if the actual processing of the request takes time.

Another useful practice is scaling.

If the server starts to overload, you need to add more resources.

Autoscaling can be set up in cloud platforms.

If the same request is received multiple times, its result can be cached.

Redis is great for this.

This way, you can respond to the client instantly, even if the request requires complex processing.

This is especially useful for code analysis: if the same repository is checked several times, the analysis results can be temporarily stored so as not to repeat the work.

When the volume of requests increases, it is also important to monitor the health of the system.

Monitoring tools such as Prometheus and Grafana come in handy for this.

With their help, you can track how many requests are processed, how loaded the servers are, and how many tasks are in the queue.

This will help you detect and fix problems in time if something goes wrong.

As for the API, it is worth considering error handling.

For example, if the OpenAI service is temporarily unavailable, the server should not crash.

Instead, it can return a message to the client that the request could not be processed and try again later.

An important point is also the design of the architecture itself.

It is worth dividing the server into microservices, if possible.

One microservice can handle requests, another — only work with OpenAI, the third — with the GitHub API.

This will not only simplify the support of the system, but also allow each part to be scaled independently.

# How the project evaluated itself ?

## Downsides/Comments:
1. **Code Structure and Modularity:**
- The code is well-structured into different modules and packages, which enhances maintainability and scalability. 
- Each component (GitHub client, OpenAI client, API endpoints) is separated, which is good practice.
2. **Configuration and Environment Management:**
- The use of `.env` for managing environment variables is commendable. 
- However, ensure that sensitive keys are not accidentally pushed to version control.
3. **Error Handling:**
- Comprehensive error handling is implemented, especially in the API interactions. 
- This is crucial for a robust system. 
- However, more specific error messages could be beneficial for easier debugging and user feedback.
4. **Logging:**
- The project utilizes logging, which is essential for debugging and monitoring.
- It might be beneficial to include more detailed logging in some parts, especially within the core functionalities like file fetching and analysis.
5. **Testing and Coverage:**
- The project aims for a good level of test coverage. 
- However, ensure that edge cases and failure paths are also thoroughly tested to avoid potential runtime errors.
6. **API Rate Limiting:**
- Handling of GitHub's API rate limit is noted, but the implementation details are not visible in the provided code. 
- Ensure that there's a robust mechanism to handle these limits to avoid service disruption.
7. **Caching Strategy:**
- Redis is used for caching, which is a good strategy for performance optimization. 
- Ensure that cache invalidation and expiration policies are well-defined to avoid stale data issues.
8. **Security:**
- Always ensure that any dependencies used in the project are kept up-to-date to avoid security vulnerabilities. 
- Regularly check for updates and potential security patches.
9. **Documentation:**
- The project includes basic documentation, but it could be expanded to cover more details about the architecture, API endpoints, and examples of requests and responses. 
- This would make the tool more accessible to new developers and users.
## Rating: 4
- The project demonstrates a high standard of code quality and organization. 
- It effectively integrates external APIs and provides a foundation for robust error handling and logging.
## Conclusion:
- The "AutoReviewTool" is well-crafted with attention to clean code practices, modularity, and robustness. 
- While there are areas for enhancement, such as more detailed documentation and expanded test coverage, the project sets a strong foundation. 
- With further development and attention to the outlined improvements, it can evolve into an even more reliable and user-friendly tool for automated code reviews.

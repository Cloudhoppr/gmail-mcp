from fastmcp.server import FastMCP
from fastmcp.server.middleware.rate_limiting import SlidingWindowRateLimitingMiddleware

# Import from the new root-level directories
from tools import email_tools

# --- Configuration ---
# The maximum number of requests allowed from a single IP.
RATE_LIMIT_PER_MINUTE = 30
# The time window in seconds to track requests.
TIME_WINDOW_MINUTES = 1


# Initialize an instance of the FastMCP class
gmail_mcp = FastMCP(
    name="Gmail MCP Server",
    instructions="An MCP server to send emails using the Gmail API.",
    version="0.1.0",
)

# Add the rate-limiting middleware to the server.
gmail_mcp.add_middleware(SlidingWindowRateLimitingMiddleware(
    max_requests=RATE_LIMIT_PER_MINUTE,
    window_minutes=TIME_WINDOW_MINUTES
))

# Register the tools with the server instance
gmail_mcp.add_tool(email_tools.send_multiple_emails)
gmail_mcp.add_tool(email_tools.send_single_email)
gmail_mcp.add_tool(email_tools.get_email_quota_status)


if __name__ == "__main__":
    # Use uvicorn to run the FastMCP application instance
    gmail_mcp.run(
        host="127.0.0.1",
        port=0
    )
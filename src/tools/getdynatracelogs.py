import time
from utils.httpclient import HttpClient
from utils.config import Config

http_client = HttpClient(
    Config.dynatrace_api_endpoint,
    headers={
        "Authorization": f"Api-Token {Config.dynatrace_api_key}",
        "Content-Type": "application/json"
    }
)

async def get_dynatrace_logs(
    problem_id: str,
    entity_id: str,
    start_time: int,
    end_time: int = None
):
    try:
        if not end_time or end_time == -1:
            end_time = start_time + 600_000

        start_iso = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(start_time / 1000))
        end_iso = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(end_time / 1000))

        query_params = {
            "from": start_iso,
            "to": end_iso,
            "query": f'entityId="{entity_id}"',
            "pageSize": 100
        }

        response = await http_client.send_request(
            method="GET",
            path="/v2/logs/query",
            params=query_params
        )

        return response

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

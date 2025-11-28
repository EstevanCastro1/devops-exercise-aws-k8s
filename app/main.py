from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field

API_KEY_HEADER = "X-Parse-REST-API-Key"
API_KEY = "2f5ae96c-b558-4c7b-a590-a501ae1c3f6c"

app = FastAPI()


class DevOpsRequest(BaseModel):
    message: str
    to: str
    from_: str = Field(alias="from")
    timeToLifeSec: int


@app.post("/DevOps")
async def devops_endpoint(
    payload: DevOpsRequest,
    x_parse_rest_api_key: str = Header(alias=API_KEY_HEADER),
    x_jwt_kwy: str = Header(alias="X-JWT-KWY"),
):
    if x_parse_rest_api_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key",
        )

    if not x_jwt_kwy:
        raise HTTPException(
            status_code=400,
            detail="Missing JWT token",
        )

    text = f"Hello {payload.to} your message will be send"
    return {"message": text}


@app.get("/DevOps", response_class=PlainTextResponse)
@app.put("/DevOps", response_class=PlainTextResponse)
@app.delete("/DevOps", response_class=PlainTextResponse)
@app.patch("/DevOps", response_class=PlainTextResponse)
async def devops_invalid_method():
    return "ERROR"

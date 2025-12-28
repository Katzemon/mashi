import asyncio
from io import BytesIO
from statistics import median

from fastapi import FastAPI, Response, status, Request, HTTPException
from starlette.responses import StreamingResponse

from bot.bot import MashiBot
from config.config import DISCORD_TOKEN, NOTIFY_API_ROUTE
from data.repos.mashi_repo import MashiRepo
from utils.io.test_data_io import save_test_mashi_data

app = FastAPI()


@app.on_event("startup")
async def startup():
    bot = MashiBot()
    asyncio.create_task(bot.start(DISCORD_TOKEN))


@app.post(NOTIFY_API_ROUTE)
async def release_notify(request: Request, response: Response):
    try:
        data = await request.json()
        if len(data) == 0:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"message": "Invalid request"}

        await asyncio.gather(*[MashiBot.instance().release_notify(data)])
        response.status_code = status.HTTP_200_OK
        return {"message": "Data received"}

    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": e}


@app.post("/api/test_mashi")
async def test_mashi(request: Request, response: Response):
    try:
        data = await request.json()
        save_test_mashi_data(data)

        response.status_code = status.HTTP_200_OK
        return {"message": "Data saved"}

    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": e}


@app.get("/api/get_mashup/{wallet}")
async def get_mashup(wallet: str, is_static: bool = True):
    if is_static:
        img_type = 0
        media_type = "image/png"
    else:
        img_type = 1
        media_type = "image/gif"

    data = await MashiRepo.instance().get_composite(wallet, img_type=img_type)

    if not data or not isinstance(data, bytes):
        raise HTTPException(status_code=404, detail="No mashup found for this wallet")

    buffer = BytesIO(data)
    buffer.seek(0)
    return StreamingResponse(buffer, media_type=media_type)

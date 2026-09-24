import asyncio
from contextlib import asynccontextmanager
from typing import Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.v1 import api_router
from core.config import settings

UDP_PORT = 8888
DISCOVERY_MSG = b"DISCOVER_STUDY_APP_SERVER"
RESPONSE_MSG = b"STUDY_APP_SERVER_HERE"


class DiscoveryServerProtocol(asyncio.DatagramProtocol):
    def __init__(self) -> None:
        self.transport: Optional[asyncio.DatagramTransport] = None

    def connection_made(self, transport: asyncio.BaseTransport) -> None:
        # Сохраняем ссылку на транспорт при установке соединения
        self.transport = transport  # type: ignore[assignment]

    def datagram_received(self, data: bytes, addr: tuple[str, int]) -> None:
        if data == DISCOVERY_MSG and self.transport is not None:
            # Отвечаем клиенту (Flutter-приложению)
            self.transport.sendto(RESPONSE_MSG, addr)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: запускаем UDP-listener на 0.0.0.0:8888
    loop = asyncio.get_running_loop()
    transport, _ = await loop.create_datagram_endpoint(
        lambda: DiscoveryServerProtocol(),
        local_addr=("0.0.0.0", UDP_PORT)
    )
    print(f"UDP Discovery Server listening on port {UDP_PORT}")

    yield

    # Shutdown: закрываем сокет при остановке FastAPI
    transport.close()


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url="/api/v1/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение основного роутера API
app.include_router(api_router, prefix="/api")


@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "message": f"Welcome to {settings.PROJECT_NAME}"}
Взят за основу fastapi - расширение фрейморка Starlette, позволяющее удобно делать REST API сервисы, поддерживающее JWT, OAuth2 для удбной авторизации и прочее. 
![image](https://user-images.githubusercontent.com/63580342/174488383-2561527f-2a4c-426f-908f-76e30ae9c1ce.png)

За приведение данных к определённому виду и соответствию определённому набору правил и ограничений, то есть за валидацию, отвечает Pydantic:
![image](https://user-images.githubusercontent.com/63580342/174495866-9515cd22-e1ed-41d4-b392-be10d70271dc.png)

```
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from schemas.chat_type import ChatType


class ChatModel(BaseModel):
    creator_user_id: int
    title: str
    description: Optional[str] = None
    chat_type: ChatType


class Chat(ChatModel):
    id: int
    created: datetime
    updated: datetime
    users: list

    class Config:
        orm_mode = True
```

```
class ChatResponse(BaseModel):
    chat: Chat
    messages: list[Message]
    members: list[User]
```

```
class MessageModel(BaseModel):
    user_id: int
    chat_id: int
    text: str


class Message(MessageModel):
    id: int
    created: datetime
    updated: datetime

    class Config:
        orm_mode = True
```

```
class UserModel(BaseModel):
    login: str
    password: str
    name: str


class User(UserModel):
    id: int
    status: UserStatus
    updated: datetime = None
    created: datetime
    chats: list

    class Config:
        orm_mode = True
```

```
```

```
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from schemas.chat_type import ChatType


class ChatModel(BaseModel):
    creator_user_id: int
    title: str
    description: Optional[str] = None
    chat_type: ChatType


class Chat(ChatModel):
    id: int
    created: datetime
    updated: datetime
    users: list

    class Config:
        orm_mode = True
```

Alembic — это инструмент для миграции базы данных, используемый в SQLAlchemy (библиотека для работы с реляционными СУБД с применением технологии ORM (типа виртуальная объектная БД))
![image](https://user-images.githubusercontent.com/63580342/174490873-587b2990-19e6-481f-b307-232f279612af.png)
- Миграции alembic:

```
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

from core.db.models import Base
from core.db.session import db_url, engine

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline():
    context.configure(
        url=db_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    with engine.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```


В качестве брокера сообщений у нас используется redis

```
from os import getenv

from redis import asyncio as aioredis


redis = aioredis.from_url(f"redis://redis:{getenv('REDIS_PORT', 6379)}")
```

JSON Web Tokens (JWT) - создаём токены, которые будем использовать при авторизации пользователей
![image](https://user-images.githubusercontent.com/63580342/174494220-4c578b85-f313-4a97-83eb-85e1be4e2125.png)


```
def get_user_from_jwt(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
    except JWTError:
        return None

    return user_id
```

```
async def get_current_user(token: str = Depends(oauth2_scheme)):
    user_id = get_user_from_jwt(token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный токен",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user_id
```

Вебсокет - нужен для оперативного отображения сообщений без необходимости постоянно обновлять страницу. Подписываемся на очередь сообщений пользователей, которая у нас в redis
![image](https://user-images.githubusercontent.com/63580342/174493912-67aae6b4-1ef9-4ebe-b327-dd3980ffe30d.png) ![image](https://user-images.githubusercontent.com/63580342/174494170-bf1699ce-628b-429f-bd9b-d61f147c5867.png)


```
async def consumer_handler(websocket: WebSocketClientProtocol) -> None:
    async for message in websocket:
        log_message(message)

async def consume(hostname: str, port: int) -> None:
    websocket_resource_url = f"ws://{hostname}:{port}"
    async with websocets.connect(websocket_resource_url) as websocket:
        await consumer_handler(websocket)

def log_message(message:str) -> None:
    logging.info(f"Message : {message}")
```

```
@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    if user_id is None:
        return

    await websocket.accept()
    pubsub = redis.pubsub()
    await pubsub.subscribe(f"user-{user_id}")

    while True:
        message = await pubsub.get_message(ignore_subscribe_messages=True)

        if message:
            await websocket.send_text(message["data"].decode())
```

- Реализация круд методов для чатов:

```
class ChatRepository(Crud):
    def __init__(self):
        super().__init__(Chat)

    def create(self, db: Session, **model_params):
        chat_db = Chat(**model_params)
        chat_db.users = [user_repository.find_by_id(model_params['creator_user_id'], db=db)]
        db.add(chat_db)
        db.commit()
        return chat_db

    def add_user_to_chat(self, chat_id: int, user_id: int, db: Session):
        chat = self.find_by_id(id=chat_id, db=db)
        user = user_repository.find_by_id(id=user_id, db=db)
        chat.users += [user]
        db.commit()
        return chat
```

```
class MessageRepository(Crud):
    def __init__(self):
        super().__init__(Message)

    def get_last_messages(self, chat_id: int, db: Session, offset: int = 0, limit: int = 20):
        messages = db.query(Message) .filter_by(chat_id=chat_id).order_by(desc(Message.created)).offset(offset).limit(limit).all()
        return messages
```


Celery - ассинхронная очередь заданий
![image](https://user-images.githubusercontent.com/63580342/174494095-ff59c454-c3bf-47c2-8d24-a3a4bf3ea6d1.png)

- Запуск celery:

```
router = APIRouter(prefix="/utils")

@router.post("/send_celery_task")
def send_celery_task(begin_datetime: datetime):
    """Запускает выполнение задачи queue.test
    
    Args:
        begin_datetime: datetime, когда запустить задачу
    """
    timezone = pytz.timezone(getenv("TZ"))
    dt_with_timezone = timezone.localize(begin_datetime)

    celery.send_task("queue.test", eta=dt_with_timezone)
```
- Воркер и конфигурация

```
celery_app = Celery("worker") 
celery_app.config_from_object("core.broker.celeryconfig")
```
```
broker_url = getenv("AMQP_URI")
task_ignore_result = True
task_store_errors_even_if_ignored = True
worker_concurrency = int(getenv("WORKER_CONCURRENCY", "4"))

task_routes = {
    "queue.*": "queue",
}
```

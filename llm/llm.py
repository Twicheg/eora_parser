import logging
import re
from langchain_gigachat.chat_models.gigachat import GigaChat
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from config import LLM_TOKEN, URLS_LIST_FILE_NAME, MAX_TOKENS, MODEL
from httpx import ConnectError
from gigachat.exceptions import ResponseError
from langchain.schema.messages import AIMessage
from langgraph.errors import GraphRecursionError
from functools import wraps

logger = logging.getLogger(__name__)

class LLM:
    model: GigaChat = None
    prompt: ChatPromptTemplate = None
    instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.model:
            cls.model = GigaChat(model=MODEL,
                                 credentials=LLM_TOKEN,
                                 verify_ssl_certs=False,
                                 profanity_check=False,
                                 streaming=False,
                                 max_tokens=int(MAX_TOKENS),
                                 timeout=60)
        if not cls.prompt:
            cls.prompt = ChatPromptTemplate.from_messages(
                [("system", "Твоя задача - отвечать на вопросы. Получи ссылки из функции get_links."
                            "Ответ должен быть результатом парсинга списка предоставленных тебе страниц."
                            "Ответы составляй ТОЛЬКО с предоставленных тебе станиц."
                            "В конце каждого ответа добавляй ссылку из списка, на основе информации которой ты отвечал."
                            ""),
                 ("placeholder", "{messages}"), ])
        if not cls.instance:
            cls.instance = super().__new__(cls)
        return cls.instance

    @staticmethod
    @tool
    def get_links() -> str:
        """Получает список ссылок, которые нужно использовать."""
        try:
            with open(URLS_LIST_FILE_NAME, 'r', encoding='utf-8') as f:
                return ''.join(f.readlines())
        except FileNotFoundError as e:
            logger.error("file not found, llm.llm.get_links()", exc_info=e)
            return ""

    @staticmethod
    def html_form(disable=False):
        """Transform to html"""

        def wrapper(f):
            @wraps(f)
            async def wrapped(*args, **kwargs):
                if disable:
                    return await f(*args, **kwargs)

                result = await f(*args, **kwargs)
                for i in re.findall(r"https://\S+", result):
                    result = result.replace(i, f"<a href={i}>{i}</a>")
                result = result.replace("\n", "<br>")
                return result

            return wrapped

        return wrapper

    @html_form(disable=False)
    async def llm_request(self, request: str) -> str:
        """Запрос/Ответ Gigachat"""
        try:
            agent = create_react_agent(model=self.model, tools=[self.get_links], prompt=self.prompt)
            answer = await agent.ainvoke(input={"messages": [{"role": "user", "content": request}]})
            for chunk in answer.get("messages"):
                if isinstance(chunk, AIMessage) and chunk.content:
                    return chunk.content
            else:
                raise ResponseError("Нет ответа")
        except (ResponseError, ConnectError) as e:
            logger.error("something went wrong, llm.llm.llm_request()", exc_info=e)
            return "Что-то пошло не так, попробуйте позже."
        except TypeError as e: # если вернется None
            logger.error("404 model not found, llm.llm.llm_request()", exc_info=e)
            return "LLModel not found"
        except GraphRecursionError as e:
            logger.error("Recursion limit of 25 reached without hitting a stop condition", exc_info=e)
            return "Я не могу ответить на этот вопрос."

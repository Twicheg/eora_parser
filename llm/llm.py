import logging
import os.path
from langchain_gigachat.chat_models.gigachat import GigaChat
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from config import LLM_TOKEN, URLS_LIST_FILE_NAME, MAX_TOKENS, MODEL, PROJECT_PATH, PROMPT_FILE
from httpx import ConnectError
from gigachat.exceptions import ResponseError
from langchain.schema.messages import AIMessage
from langgraph.errors import GraphRecursionError
from langgraph.graph.state import CompiledStateGraph
from web_api.services import HtmlSupport

logger = logging.getLogger(__name__)


class LLM:
    model: GigaChat = None
    prompt: ChatPromptTemplate = None
    agent: CompiledStateGraph = None
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
                [("system", cls.get_prompt()),
                 ("placeholder", "{messages}"), ])
        if not cls.instance:
            cls.instance = super().__new__(cls)
        if not cls.agent:
            cls.agent = create_react_agent(model=cls.model, tools=[cls.get_links], prompt=cls.prompt)
        return cls.instance

    @staticmethod
    def get_prompt() -> str:
        """Get base prompt"""
        try:
            with open(os.path.join(PROJECT_PATH, PROMPT_FILE), 'r', encoding='utf-8') as f:
                return ' '.join([i.rstrip() for i in f.readlines()])
        except FileNotFoundError as e:
            logger.error("file not found, llm.llm.get_prompt", exc_info=e)
            return ""

    @staticmethod
    @tool
    def get_links() -> str:
        """Получает список ссылок, которые нужно использовать."""
        try:
            with open(os.path.join(PROJECT_PATH, URLS_LIST_FILE_NAME), 'r', encoding='utf-8') as f:
                return ' '.join([i.rstrip() for i in f.readlines()])
        except FileNotFoundError as e:
            logger.error("file not found, llm.llm.get_links()", exc_info=e)
            return ""

    @HtmlSupport.replace_n()
    @HtmlSupport.set_links()
    async def llm_request(self, request: str) -> str:
        """Запрос/Ответ Gigachat"""
        try:
            answer = await self.agent.ainvoke(input={"messages": [{"role": "user", "content": request}]})
            for chunk in answer.get("messages"):
                if isinstance(chunk, AIMessage) and chunk.content:
                    return chunk.content
            else:
                raise ResponseError("Нет ответа")
        except (ResponseError, ConnectError) as e:
            logger.error("something went wrong, llm.llm.llm_request()", exc_info=e)
            return "Что-то пошло не так, попробуйте позже."
        except TypeError as e:  # если вернется None
            logger.error("404 model not found, llm.llm.llm_request()", exc_info=e)
            return "LLModel not found"
        except GraphRecursionError as e:
            logger.error("Recursion limit of 25 reached without hitting a stop condition", exc_info=e)
            return "Я не могу ответить на этот вопрос."

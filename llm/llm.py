import logging
import re
import html
from langchain_gigachat.chat_models.gigachat import GigaChat
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from config import LLM_TOKEN, URLS_LIST_FILE_NAME, MAX_TOKENS, MODEL
from httpx import ConnectError
from gigachat.exceptions import ResponseError
from langchain.schema.messages import AIMessage
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
                [("system", "Используй только ссылки, которые я тебе дал и ответь на вопрос."
                            "Во время каждого ответа приводи ссылку из списка откуда взял информацию."
                            "Если ссылка не требуется - не пиши её."),
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
    def html_form(content):
        content = html.escape(content)
        while "\n" in content:
            content = content.replace("\n", "<br>")
        res = re.findall("https://\S+",content)
        for i in res:
            content = content.replace(i,f"<a href={i}>{i}</a>")
        return content

    async def llm_request(self, request: str) -> str:
        """Запрос/Ответ Gigachat"""
        try:
            agent = create_react_agent(model=self.model, tools=[self.get_links], prompt=self.prompt)
            answer = await agent.ainvoke(input={"messages": [{"role": "user", "content": request}]})
            for chunk in answer.get("messages"):
                if isinstance(chunk,AIMessage) and chunk.content:
                    return self.html_form(chunk.content)
        except (ResponseError, ConnectError) as e:
            logger.error("something went wrong, llm.llm.llm_request()", exc_info=e)

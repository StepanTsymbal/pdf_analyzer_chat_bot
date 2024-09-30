from pydantic import BaseModel


class QuestionAnswer(BaseModel):
    Question: str
    Answer: str


class Chat(BaseModel):
    DocId: int
    Question: str
    History: list[QuestionAnswer]

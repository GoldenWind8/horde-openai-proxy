from pydantic import BaseModel, Field
from typing import List, Optional


class OpenAIChatMessage(BaseModel):
    role: str
    content: str


class OpenAIChatRequest(BaseModel):
    model: str
    messages: List[OpenAIChatMessage]

#Start here
class OpenAICompletionRequest(BaseModel):
    model: str
    prompt: str
    max_tokens: int
    temperature: float
    top_p: float
    n: int
    stream: bool
    logprobs: Optional[int]
    stop: Optional[List[str]]


class OpenAIChatChoice(BaseModel):
    index: int
    message: OpenAIChatMessage
    finish_reason: str


class OpenAIUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class OpenAIChatResponse(BaseModel):
    id: str
    object: str
    created: int
    choices: List[OpenAIChatChoice]
    usage: OpenAIUsage


class OpenAICompletionChoice(BaseModel):
    text: str
    index: int
    logprobs: Optional[int]
    finish_reason: str


class OpenAICompletionResponse(BaseModel):
    id: str
    object: str
    created: int
    model: str
    choices: List[OpenAICompletionChoice]
    usage: OpenAIUsage


class Params(BaseModel):
    max_context_length: int
    max_length: int

#end
class KoboldAIRequest(BaseModel):
    prompt: str
    models: List[str]
    trusted_workers: bool
    params: Params


class Generation(BaseModel):
    worker_id: str
    worker_name: str
    model: str
    state: str
    text: str
    seed: int


class KoboldAIPollResponse(BaseModel):
    finished: int
    processing: int
    restarted: int
    waiting: int
    done: bool
    faulted: bool
    wait_time: int
    queue_position: int
    kudos: float
    is_possible: bool
    generations: List[Generation]


class KoboldAIAsyncResponse(BaseModel):
    id: str
    message: str

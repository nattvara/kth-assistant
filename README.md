# KTH Assistant

A repository for the code used in my master's thesis

# Design notes

How the llm service will be used

```py
# in some api handler

user_input = "some user input"

llm = LLMService()

prompt_handle = llm.dispatch_prompt(
    prompt=user_input,
    stream=True,
    model=MISTRAL_7B,
    config=SomeParams()
)
# prompt handle properties (these are stored in the database)
# - id
# - response
# - websocket_url
# - websocket_is_open (boolean)
# - priority
# - state (finished, waiting, in_progress, failed)
# - queue_position
# - number_of_tokens
# - config

# the caller is expected to listen to the websocket
return prompt_handle
```

```py
# in some internal api such as generating user query

prompt = "Generate a query from this chat history: ... some chat history ..."

llm = LLMService()

prompt_handle = llm.dispatch_prompt(
    prompt=user_input,
    stream=False,
    model=MISTRAL_7B,
    config=SomeParams()
)

try:
    response = llm.wait_for_response(prompt_handle, timeout_after_seconds=60)
except:
    # handle error
```

## Response issue

1. `llama2-13b-chat` failed to response in json format in most times, which is explicitly required in system prompt.

```
# system prompt
You can only use one function at a time. You must respond in this json format: {"name": "function_name", "arguments": {"arg1": "val1", "arg2": "val2"}}

# model response
"VWTurn(angle=10, ang_speed=50)"
```


debug attempts:
 - Trying to remove `chat_format="chatml-function-calling"` specified in the llm initialisation phase.



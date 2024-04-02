import json
from typing import Optional, Any

import requests
from jinja2 import Environment


def default_pt(messages):
    return " ".join(message["content"] for message in messages)

def hf_chat_template(model: str, messages: list, chat_template: Optional[Any] = None):
    ## get the tokenizer config from huggingface
    bos_token = ""
    eos_token = ""
    if chat_template is None:

        def _get_tokenizer_config(hf_model_name):
            url = (
                f"https://huggingface.co/{hf_model_name}/raw/main/tokenizer_config.json"
            )
            # Make a GET request to fetch the JSON data
            response = requests.get(url)
            if response.status_code == 200:
                # Parse the JSON data
                tokenizer_config = json.loads(response.content)
                return {"status": "success", "tokenizer": tokenizer_config}
            else:
                return {"status": "failure"}

        tokenizer_config = _get_tokenizer_config(model)
        if (
                tokenizer_config["status"] == "failure"
        ):
            raise Exception("No chat template found")

        ## read the bos token, eos token and chat template from the json
        tokenizer_config = tokenizer_config["tokenizer"]
        bos_token = tokenizer_config["bos_token"]
        eos_token = tokenizer_config["eos_token"]
        if "chat_template" in tokenizer_config:
            chat_template = tokenizer_config["chat_template"]
        else:
            chat_template = default_chat_template()

    def raise_exception(message):
        raise Exception(f"Error message - {message}")

    # Create a template object from the template text
    env = Environment()
    env.globals["raise_exception"] = raise_exception
    try:
        template = env.from_string(chat_template)
    except Exception as e:
        raise e

    def _is_system_in_template():
        try:
            # Try rendering the template with a system message
            response = template.render(
                messages=[{"role": "system", "content": "test"}],
                eos_token="<eos>",
                bos_token="<bos>",
            )
            return True

        # This will be raised if Jinja attempts to render the system message and it can't
        except:
            return False

    try:
        # Render the template with the provided values
        if _is_system_in_template():
            rendered_text = template.render(
                bos_token=bos_token, eos_token=eos_token, messages=messages
            )
        else:
            # treat a system message as a user message, if system not in template
            try:
                reformatted_messages = []
                for message in messages:
                    if message["role"] == "system":
                        reformatted_messages.append(
                            {"role": "user", "content": message["content"]}
                        )
                    else:
                        reformatted_messages.append(message)
                rendered_text = template.render(
                    bos_token=bos_token,
                    eos_token=eos_token,
                    messages=reformatted_messages,
                )
            except Exception as e:
                if "Conversation roles must alternate user/assistant" in str(e):
                    # reformat messages to ensure user/assistant are alternating, if there's either 2 consecutive 'user' messages or 2 consecutive 'assistant' message, add a blank 'user' or 'assistant' message to ensure compatibility
                    new_messages = []
                    for i in range(len(reformatted_messages) - 1):
                        new_messages.append(reformatted_messages[i])
                        if (
                                reformatted_messages[i]["role"]
                                == reformatted_messages[i + 1]["role"]
                        ):
                            if reformatted_messages[i]["role"] == "user":
                                new_messages.append(
                                    {"role": "assistant", "content": ""}
                                )
                            else:
                                new_messages.append({"role": "user", "content": ""})
                    new_messages.append(reformatted_messages[-1])
                    rendered_text = template.render(
                        bos_token=bos_token, eos_token=eos_token, messages=new_messages
                    )
        return rendered_text
    except Exception as e:
        raise Exception(f"Error rendering template - {str(e)}")




# Function call template
def function_call_prompt(messages: list, functions: list):
    function_prompt = """Produce JSON OUTPUT ONLY! Adhere to this format {"name": "function_name", "arguments":{"argument_name": "argument_value"}} The following functions are available to you:"""
    for function in functions:
        function_prompt += f"""\n{function}\n"""

    function_added_to_prompt = False
    for message in messages:
        if "system" in message["role"]:
            message["content"] += f""" {function_prompt}"""
            function_added_to_prompt = True

    if function_added_to_prompt == False:
        messages.append({"role": "system", "content": f"""{function_prompt}"""})

    return messages

def default_chat_template():
    """
    This template formats inputs in the standard ChatML format. See
    https://github.com/openai/openai-python/blob/main/chatml.md
    """
    return (
        "{% for message in messages %}"
        "{{'<|im_start|>' + message['role'] + '\n' + message['content'] + '<|im_end|>' + '\n'}}"
        "{% endfor %}"
        "{% if add_generation_prompt %}"
        "{{ '<|im_start|>assistant\n' }}"
        "{% endif %}"
    )


def hf2(chat_template):
    # These are the cases when the model has a single template
    # priority: `chat_template` argument > `tokenizer.chat_template` > `tokenizer.default_chat_template
    if chat_template is not None:
        chat_template = chat_template
    else:
        chat_template = default_chat_template()

    # Compilation function uses a cache to avoid recompiling the same template


    compiled_template = self._compile_jinja_template(chat_template)

    template_kwargs = {**self.special_tokens_map, **kwargs}  # kwargs overwrite special tokens if both are present
    rendered = compiled_template.render(
        messages=conversation, add_generation_prompt=add_generation_prompt, **template_kwargs
    )
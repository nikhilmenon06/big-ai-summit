import openai

def get_initial_message():
    messages=[
            #{"role": "system", "content": "You are a helpful Car AI. Who anwers brief questions about BMW based on the given paragraph."},
            #{"role": "user", "content": "I want to learn about BMW"},
            #{"role": "assistant", "content": "Thats awesome, what do you want to know about BMW"}
        ]
    return messages

def get_chatgpt_response(messages, model="gpt-3.5-turbo"):
    print("model: ", model)
    response = openai.ChatCompletion.create(
    model=model,
    messages=messages
    )
    return  response['choices'][0]['message']['content']

def update_chat(messages, role, content):
    messages.append({"role": role, "content": content})
    return messages
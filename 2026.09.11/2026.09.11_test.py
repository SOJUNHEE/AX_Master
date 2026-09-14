from openai import OpenAI

# client = OpenAI(api_key = 'your_api_key')
# response = client.chat.completions.create(
#     model = 'gpt-4o-mini',
#     messages=[
#         {'role':'system', 'content': 'You are a helpful assistant.'},
#     ]
# )
# print(response.choices[0].message.content)


# from openai import OpenAI

# def ask_llm(api_key, model, question):
#     client = OpenAI(api_key=api_key)
#     response = client.chat.completions.create(
#         model=model,
#         messages=[
#             {'role': 'system', 'content': '친절한 도우미'},
#             {'role': 'user', 'content': question}
#         ]
#     )
#     return response.choices[0].message.content, response.usage

# my_api_key = 'your_api_key'
# answer, usage = ask_llm(my_api_key, 'gpt-4o-mini', '안녕하세요. 오늘 날씨가 어떤가요?')

# print('Answer:', answer)
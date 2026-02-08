from openai import OpenAI

client = OpenAI(
  base_url="https://api.featherless.ai/v1",
  api_key="rc_1a7d0cd0e86e32cff8605e3cae24b7a881964d6ff409c611dcf89bfc88e10cba",
)

prompt = "Write a haiku about cows."

response = client.chat.completions.create(
  model='Qwen/Qwen2.5-7B-Instruct',
  messages=[
    {"role": "system", "content": prompt},
    {"role": "user", "content": "Do not write a haiku about cows."},
  ],
)
print(response.choices[0].message.content)
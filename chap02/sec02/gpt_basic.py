from openai import OpenAI


client = OpenAI(api_key=api_key)

# ② 
response = client.chat.completions.create(
  model="gpt-4o",
  temperature=0.1,  # ③
  messages=[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "25년도 대한민국 대통령은?"},
  ]		# ④
)

print(response)

print('----')	# ⑤
print(response.choices[0].message.content) 

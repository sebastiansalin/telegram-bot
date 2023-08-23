import os
import openai
openai.organization = "org-cJGpH3A9G3Hgc3zRdQ33kclG"
openai.api_key = "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"

completion = openai.ChatCompletion.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello!"}
  ]
)

print(completion.choices[0].message)
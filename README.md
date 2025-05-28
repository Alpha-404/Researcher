![image](https://github.com/user-attachments/assets/7c7a7823-3a8a-4b6a-8389-18f9183ccf1e)
![image](https://github.com/user-attachments/assets/18d572ca-1fce-447b-9d1a-3a8b920591d5)

Config.json explanation:
```
{
  "links": 5, <- This is how many links are going to be opened by the bot and put into the llm
  "model": "mistral-7b-instruct-v0.1.Q5_K_M.gguf", <- This is the path to the model, it doesent have to be an absolute path aslong as the model is in the same dir
  "model-tokens": 8192, <- This is how many tokens the model is allowed to use, For summarising long, complex topics a higher number is recccommended
  "max-chunks": 400, <- This is how many chunks the bot is allowed to break the extracted text into
  "max-tokens": 300, <- This is how many tokens its allowed to break each chunk into
  "summarization-temp": 0.7, <- This is how creative the bot will be in summarization, higher values means it is more likely to go off course, lower values means its going to be closer to the text
  "gpu-layers": -1, <- How many layers to run on the gpu, -1 means all layers, 0 means all layers will be on the cpu and 100 means 100 layers will run on the gpu and so on
  "ignore-sites": ["www.reddit.com", "www.youtube.com", "old.reddit.com", "search.brave.com"] <- These are the sites to be ignored by the bot when searching for links
}
```

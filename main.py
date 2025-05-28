import random, urllib.parse, json, time, textwrap, subprocess
from playwright.sync_api import sync_playwright
from llama_cpp import Llama

#Load useragents
global userAgents
userAgents = []
for i in json.load(open("useragentlist.json", "r")):
    userAgents.append(i.get("ua"))

#Load settings
global settings
settings = json.load(open("config.json", "r"))

#load summarizer model from huggingface
#summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

#Load llm
llm = Llama(
    model_path=settings.get("model"),
    n_gpu_layers=settings.get("gpu-layers"),  # load everything on GPU
    n_ctx=settings.get("model-tokens"),
    verbose=False
)

#Functions
def search(query):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True,
                                       executable_path="/home/rajaa/.cache/ms-playwright/chromium_headless_shell-1161/chrome-linux/headless_shell")
        global userAgents
        browser.new_context(user_agent=random.choice(userAgents))
        page = browser.new_page()
        parsedQuery = urllib.parse.quote(query) #make url safe
        page.goto(f"https://search.brave.com/search?q={parsedQuery}&source=web")
        page.wait_for_selector("#results a")
        links = page.eval_on_selector_all(
            "#results a",
            """els => els
                .map(el => el.href)
                .filter(href => href && href.startsWith("http"))"""
        )
        #with open("test.html", "w") as f:
        #    f.writelines(page.content())
        browser.close()
        parsedLinks = []
        for i in links:
            if "#" in i:
                i = i.split("#", 1)[0] #remove #
            if i not in parsedLinks and urllib.parse.urlparse(i).netloc not in settings.get("ignore-sites") : # Stop Duplicates and filter out non scrape friendly sites
                parsedLinks.append(i)

        return parsedLinks[:settings.get("links")]

def extractContent(link):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True,
                                       executable_path="/home/rajaa/.cache/ms-playwright/chromium_headless_shell-1161/chrome-linux/headless_shell")
        global userAgents
        browser.new_context(user_agent=random.choice(userAgents))
        page = browser.new_page()
        page.goto(link)
        content = ""
        if ".wikipedia.org/" in link: #Special wikipedia parser
            content = page.eval_on_selector_all(
                "#mw-content-text p",
                "els => els.map(el => el.innerText).filter(Boolean).join('\\n')"
            )
        else:
            # Generic fallback: get visible text from body
            try:
                page.wait_for_selector("body", timeout=15000) #15 seconds
                content = page.eval_on_selector(
                    "body",
                    "el => el.innerText"
                )
            except:
                content = "Failed to parse this site, try adding to to the exceptions in config.json"

        #with open("test.html", "w") as f:
        #    f.writelines(page.content())

        browser.close()
        return content

def llamaSummarize(prompt):
    output = llm(
        prompt,
        max_tokens=settings.get("max-tokens"),
        temperature=settings.get("summarization-temp"),
        stop=["</s>"]
    )
    return output["choices"][0]["text"].strip()

def summarizeContent(content):
    #return summarizer(content[:8192])[0]["summary_text"]
    maxChunks = settings.get("max-chunks")
    chunks = textwrap.wrap(content, maxChunks)

    summaries = []
    start = time.time()
    for i, chunk in enumerate(chunks):
        print(f"\rSummarizing chunk {i + 1}/{len(chunks)} ({round(time.time() - start, 2)}s)...", end="", flush=True)
        prompt = f"[INST] Summarize the following text:\n\n{chunk} [/INST]"
        summary = llamaSummarize(prompt)
        summaries.append(summary)

    if len(summaries) == 1:
        return summaries[0]

    merged = "\n".join(summaries)
    print("\rGenerating final summary...", end="", flush=True)
    finalPrompt = f"[INST] Combine the following summaries into a brief paragraph:\n\n{merged} [/INST]"
    try:
        return llamaSummarize(finalPrompt)
    except ValueError:
        return f"The following text hasnt been properly condensed due to llm constraints:\n{merged}"

query = input("What would you like to research?: ")

totalTimeStart = time.time()
links = search(query) # get links to search
linkToContent = {}

for i in links:
    print(f"Extracting content for {i}...", end="", flush=True)
    start = time.time()
    content = extractContent(i)
    print(f"\rExtracting content for {i}... (took {round(time.time() - start, 2)}s)")
    print(f"Summarizing content for {i}...", end="", flush=True)
    start = time.time()
    linkToContent[i] = summarizeContent(content)
    print(f"\rSummarizing content for {i}... (took {round(time.time() - start, 2)}s)")

with open("output.txt", "w") as f:
    for i in linkToContent:
        f.writelines(f"{i}:\n")
        f.writelines(f"{linkToContent.get(i)}\n\n")

print(f"Finished in {round(time.time() - totalTimeStart, 2)}s")
print("Saved to output.txt")

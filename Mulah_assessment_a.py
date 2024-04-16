import requests
from bs4 import BeautifulSoup
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse


def extract_headlines():
    headline_list = []
    headlines = soup.find_all('h2', class_= 'font-polysans text-20 font-bold leading-100 tracking-1 md:text-24 lg:text-20')

    for headline in headlines:
        title = headline.text.strip()
        hyperlink = base_url + (headline.find('a')['href'])

        hyperlink_response = requests.get(hyperlink)
        hyperlink_soup = BeautifulSoup(hyperlink_response.content, 'html.parser')
        date_time_element = hyperlink_soup.find("meta", property="article:published_time")
        if date_time_element and date_time_element.has_attr("content"):
            datetime_str = date_time_element["content"]
            try:
                date_time_obj = datetime.fromisoformat(datetime_str)
                formatted_date_time = date_time_obj.strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                return "Invalid datetime format"
        else:
            return "Datetime not found in meta tag"
        headline_list.append({'title':title, 'hyperlink':hyperlink, 'date':formatted_date_time})

    return headline_list

def filter_sort_headlines(headlines):
    filtered_headlines = []
    for headline in headlines:
        if headline['date'] >= "2022-01-01 00:00:00":
            filtered_headlines.append(headline)

    sorted_headlines = sorted(headlines, key=lambda x: x["date"], reverse=True)
    return sorted_headlines


base_url = 'https://www.theverge.com'
response = requests.get(base_url)
soup = BeautifulSoup(response.content, 'html.parser')

app = FastAPI()
templates = Jinja2Templates(directory="")

@app.get("/")
def index(request: Request):
    headlines = extract_headlines()
    sorted_headlines = filter_sort_headlines(headlines)
    print(sorted_headlines)
    with open("index.html", "r") as html_file:
        html_content = html_file.read()
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

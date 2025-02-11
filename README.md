# <p align="center">job scraper</p>
Fullstack application for scraping job portals (currently theprotocol.it and justjoin.it). It can handle multiple scraping processes and flask server at the same time. All you need to do is provide offer list URL(s) and watch it update the database while you look for a dream job.

## full description coming soon

<p align="center">
  <img src="https://github.com/user-attachments/assets/9484d58b-04c1-4704-990d-fb589a5910ff" width=60%>
</p>

## <p align="center"> HOW TO USE ON WINDOWS </p>
#### requirements
- **browser:** I used chrome, currently version 132.0 (check in chrome://settings/help)
- **matching browser driver:** https://googlechromelabs.github.io/chrome-for-testing/ (same version as browser needed. Check if chromedriver.exe from the main project's directory matches)
- **packages:** *pip install -r requirements.txt* (executed in the folder where requirements.txt file is). I suggest installing in a virtual environment as there are quite a lot of them

#### Once you have a browser, a driver and the packages installed:
- run **main.py**
- visit **http://localhost:5000** in your browser of choice and start scraping

## <p align="center"> HOW TO USE WITH DOCKER </p>
- download an image

```
docker pull letmedockerize/job_scraper:latest
```

- run container

```
docker run -p 5000:5000 letmedockerize/job_scraper
```

- visit **http://localhost:5000** in your browser of choice and start scraping

    <!--*docker version works in selenium headless mode (invisible scraping browser window)*-->
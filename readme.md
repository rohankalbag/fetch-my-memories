# Fetch my Memories

## Automatically generate your yearbook with ease!

This open-source project leverages your yearbook's web portal's API endpoints to fetch your metadata and dynamically generate a printable yearbook for you.

<img width="847" alt="Screenshot 2024-11-22 at 6 36 40 PM" src="https://github.com/user-attachments/assets/c57f2fe5-e41d-4223-bcb5-275cf3ebe295">


## Getting Started

### Running on Local Python 

You'll need `python3` for this and an internet connection, also make sure to get the email address (of the form `xxxxx@iitb.ac.in`) and password for your yearbook account if you have forgotten it.

```bash
git clone https://github.com/rohankalbag/fetch-my-memories
cd fetch-my-memories
pip install -r requirements.txt
python3 generateYearBook.py YOUR_EMAIL_ID YOUR_PASSWORD
```

You can find your yearbook ready as `yearbook.pdf` and a printable version of it as `yearbook_printable.pdf`, ready your printers!

### Running on Google Colab

<a href="https://colab.research.google.com/drive/1CBSxdaOnImaiUhoKPtAaxAJ9Gp1CBzp7?usp=sharing"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>

### Running Docker Container

To use the containerized app image, first start your docker desktop and then run

```bash
docker compose up -d
```

Then run open a browser and enter the url `localhost:8000` to run the app with the trivial frontend

```bash
docker compose down
```

## Contributing

Check github issues for possible bugs, feature proposals

Raise issues for bugs, suggesting additional features and assign yourself to it, create a fork with your changes and raise a MR to the main branch

## License

Open Source Software - Apache License Version 2.0

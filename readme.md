Fixes:

Update Username: Please use the user's email ID as their username. It seems people are getting confused when trying to download, so this small change will help a lot.

CSS Improvements: Seniors have shared feedback about the formatting, and honestly, they have a point. The text is overlapping, the background feels unthemed, and the flow of the yearbook isn't as structured as it could be. Feed messages of any size are randomly appearing in the PDF, which is a bit chaotic.

While there might be a delay in delivery of yearbook, but imagine the happiness seniors would feel lifelong if their yearbook was beautifully designed with a theme-based flow, a gallery, and a "khazana of memories" instead of something that feels rushed and making feel shy on sharing with someone. The API part iwas straightforward no big deal with it, but creating something that truly captures their memories is what makes this special.

But yes as you said "It is a rudimentary, work in progress " so go ahead. Kudos and GG!!


# Fetch my Memories

## Automatically generate your yearbook with ease!

This open-source project leverages your "**restrictive exclusive subscription**" yearbook's web portal's API endpoints to fetch your metadata and dynamically generate a printable yearbook for you.

<img width="847" alt="Screenshot 2024-11-22 at 6 36 40 PM" src="https://github.com/user-attachments/assets/c57f2fe5-e41d-4223-bcb5-275cf3ebe295">


## Getting Started

You'll need `python3` for this and an internet connection, also make sure to get the username (of the form `xxxxx@iitb.ac.in`) and password for your yearbook account if you have forgotten it.

```bash
git clone https://github.com/rohankalbag/fetch-my-memories
cd fetch-my-memories
pip install -r requirements.txt
python3 generateYearBook.py YOUR_USERNAME YOUR_PASSWORD
```

You can find your yearbook ready as `yearbook.pdf`, ready your printers!

Or you could just use Google Colab


<a href="https://colab.research.google.com/drive/1CBSxdaOnImaiUhoKPtAaxAJ9Gp1CBzp7?usp=sharing"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>

## Contributing

Check github issues for possible bugs, feature proposals

Raise issues for bugs, suggesting additional features and assign yourself to it, create a fork with your changes and raise a MR to the main branch

## License

Open Source Software - Apache License Version 2.0

Made with ❤️ by those 'frugal' or 'cheap' for those 'frugal' or 'cheap'




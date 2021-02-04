# Gradescope-Deadline-Tracker

The project captures the upcoming deadlines on gradescope. deadline_tracker.py will scan through all courses and find things that are due in the next 7 days and sends a wechat message to the designated account. If you don't need that feature, you can just save the returned variable msg wherever you want.

11.exe is a software I bought elsewhere. It reads txt files and sends it to selected wechat friends. A more reliable version will be published in a day or two.

This project a crappy tool I wrote for myself, feel free to use it if you need. Please contact me if you need to use it for commercial purposes.

Note: Make sure you substitute "your_email_here" with your email and "your_password_here" with your password. I'm also calculating the time based on Beijing time and my gradescope time as US West Coast time. 

My environment: A server running windows but the tool works on both windows and mac platforms.
Dependencies: If any issue occurs,
  pip install lxml
  pip install pyOpenSSL


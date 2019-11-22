# Project 1

Web Programming with Python and JavaScript

## My book review website
The function of this website is to provide its members a platform which they can search for books, write reviews for individual books and see other users' reviews.

In order to use this website users have to register and log in. Also there's an API for querying book details. No registration is required for accessing this API.

## Navigation bar (includes/navbar.html)
In every page a navigation bar is shown at the top of the page. On the navigation bar there are links for homepage, API access page, logging in, signing up and logging out if the user is already logged in. 

##  Homepage (/)
In this page (index.html) a brief introduction about this website is presented. If a user is logged in, book search page (search.html) is shown instead.

## API Access Information Page (/api)
This page (api.html) shows some information about using the API. An example output is also shown.

## Registration Page (/signup)
A registration form is shown in this page (signup.html). Users should provide a username and a password (at least 8 characters long) to sign up. If the username is already taken an error message is shown for users to choose another username. If the password is shorter than 8 characters an error message is displayed. Also if any of the fields are not filled in by the user an error message is displayed.

After successful registration user is automatically logged in and redirected to the book search page.

## Log in Page (/login)
A login form is displayed in this page (login.html). If the user enters his/her username or password incorrectly an error message is showed to inform the user.

After successful log in user is redirected to the book search page.

## Logging out (/logout)
When a user is logged in a link for logging out is displayed in the navigation bar instead of log in and sign up links. When the user clicks this link he/she logs out and is redirected to the homepage.

## Book Search Page (/search)
If the user is logged in the book search page (search.html) is displayed. If not he/she is redirected to the log in page.

There's a form for users to search for books in this page. Users can search by ISBN, the title of a book or the author of a book. If this page is requested by 'GET' method, only this form is displayed.

After the users submit the search form a table of books matching the search criteria is displayed. The user is informed if there are no matches. In this table the user can click on the title of a book to go to the book details page.

## Book Details Page (/book/<book_id>)
Before accessing this page the user is checked whether he/she is logged in or not. If the user is not logged in, he/she is redirected to the log in page.

This page is divided into 3 parts. At the top book details are displayed. Also average rating and number of ratings are shown from the goodreads website. If the user clicks on the goodreads logo, the goodreads page of the book is opened in a new tab.

In the middle of the page user reviews are displayed. Most recent review is shown at the top.

At the bottom there's a form for users to submit their ratings and reviews about the book. Users can only submit one review for the same book. When a user submits a review for a book, his/her old review is overwritten if exists.

---

## import.py
This is an utility program that reads the book data in the csv file and imports them to the PostgreSQL database hosted in Heroku.

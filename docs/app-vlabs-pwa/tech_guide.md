# Tech Guide : Virtual Labs PWA

# Table of Contents:

- [Introduction](#bookmark=id.nrp0zh4gwqtz)
- [Overview](#bookmark=id.60x16qgj1r2y)
- [Target Audience](#bookmark=id.4hzrlc3w6co2)
- [Technology Used](#bookmark=id.nfbll5hlre6q)
- [Code Explanation](#bookmark=id.h3g6h3w9ygj5)
  - [Frontend](#bookmark=id.jsqvzq1st0co)
  - [Backend](#bookmark=id.25itayhto8r1)
- [Source File](#bookmark=id.uu5e9u3xb3hn)
- [Deployment/ Usage](#bookmark=id.7dc7s43kp7xu)
- [Deployment and the Building of the APK](#bookmark=id.vclekrjmgweq)
- [Future Scope](#bookmark=id.vz7msukfof53)
- [Troubleshooting](#bookmark=id.c7yz9ih8zl5v)

# Introduction:

- This is a technical document which is useful for all the developers who will work on this app so that they can understand the functioning of this application better and can easily troubleshoot the issues that they may face. It explains the different features of the application along with the functions of different files.

# Overview:

- This app displays all the experiments hosted under the virtual labs site. This app is fully responsive with any device that the user has. It has also been converted to an apk and has been hosted on the android play store for higher availability to the users.
- It has been deployed on [https://virtual-labs.github.io/app-vlabs-pwa/](https://virtual-labs.github.io/app-vlabs-pwa/).

# Target Audience:

- The target audience for this document are the developers working on this application.

# Technology Used:

- This app is based using ReactJS and NodeJS. For styling BULMA CSS framework has been used.
- The app requests its data from an AWS route that connects to a DynamoDB table and supplies the application with its data.
- The data is being collected in a google sheet and is pushed to DynamoDB using app script.
- The cards are being rendered using a component that has been hosted on npm. The name of the component is ‘BulmaComponent’ and can be installed using command ‘npm install yatharth-super-lemon’.

# Code Explanation:

- Frontend

  - App.js

          This file makes the API call for the data and saves it in a state. It is also responsible for setting up the basic framework for the website and contains the code for ‘Search Bar’ the ‘Filter’ button for toggle and handles the pagination.

  - ExperimentLoader.js

          This file is responsible for loading the Experiment Cards and also helps in filtering the experiments. It also enables the functionality wherein a user can save certain filters. It also implements the 4 tabs in the app i.e Popular, Recents, All Experiments, Starred Experiments.

  - Navbar.js

          In case of mobile and tablet the buttons for tabs are replaced with a Navbar which has a hamburger for the 4 tabs and helps switch between them.

  - The data such as the saved experiments, saved filters and recent experiments visited have been stored in local storage.

- Backend
  _ `pwa.gs \
`This is a google app script that pushes data to the DynamoDB table. It only pushes those records that have the image, description and column fields as non-empty. It pushes the records via a post request
  _ `PWA_Get.py \
`This lambda function is executed when a GET request is made to the DynamoDB table. It returns all the items in the table
  _ `PWA_Post.py \
`This lambda function is executed when a POST request is made to the DynamoDB table. It uses the `BatchWrite` function to write all the items provided in the body of the request to the DynamoDB table.
  _ `PWA_Delete.py \
`This lambda function is executed when the DELETE request is made to the DynamoDB table. It deletes a particular item in the DynamoDB table based on the `id` parameter based in the URL \* `PWA_Post_Authorizer \
`This lambda function checks the header of the POST request and only passes on the request, if the credentials provided are correct

# Source File:

- The data for all the experiments is contained in this [Google Spreadsheet](https://docs.google.com/spreadsheets/u/0/d/1x12nhpp0QvnsA6x-O1sV4IA9SAbfVsq_wiexWkutOmU/edit) inside the sheet named ‘Experiment-Database’. A trigger has been set for the app script ‘pwa.gs’ which fills the data into database tables once every 24 hours.

# Deployment/Usage:

- Frontend
  - To create the static website, simply run `npm run build` inside the node folder. Static website is then hosted on the backend, other steps taken to run the app are mentioned below.
- Backend
  - Google App Script
    - Upon running this script, all the eligible records in the google sheet will be pushed to the DynamoDB table. Currently the credentials being used is an environment variable named `pwa_auth`. In order to change the value or to add more variables, go to the `Project Settings` of the App Scripts page of the Google sheet and make the necessary changes.
  - AWS
    - The AWS backend needs no deployment as it has already been set up.
    - For any changes to be made, the following is a roadmap of functionality of the AWS backend.
    - The `API Gateway` page is the place where the API routes to different AWS services are configured.
    - Here the PWA_API is the api configured for this project.
    - This page is where the various routes, integrations, authorizations and CORS are configured.
    - The `AWS Lambda` page is where all the lambda functions are hosted and can be modified.
    - The names of the Lambda functions are as follows:
      - PWA_Delete
      - PWA_Post
      - PWA_Get
      - PWA_Post_Authorizer
    - The DynamoDB table that has been created is named `PWA_EXP`
    - All these have been configured in the `ap-southeast-2(Sydney)` region.

# Deployment and the Building of the APK

The easiest way to package the application for the Google Play Store is to use the [PWABuilder](https://www.pwabuilder.com/) tool.

- Once the pwa is hosted on a url, go to the [PWABuilder](https://www.pwabuilder.com/) site and provide the url of the application.
- After that, you will be taken to a page where certain performance metrics of the PWA will be shown, and ways to improve the PWA.
- There will be an option to "Package for Stores" and choose the Google play store option.
- The result will be downloadable zip file that contains the apk file, the aab file, the assetlinks.json file, and the signin keys
- Now, after this add the assetlinks.json file to the server where the application is hosted at the location `.well-known/assetlinks.json`. The assetlinks.json file indicates the Android apps that are associated with the website and verify the app's URL intents. This removes the home bar from the android app's UI.
- Now finally, you have all the required files in order to deploy the app to the playstore

# Future Scope:

- Filling in the metadata for more experiments so that more experiments are available on this page.
- Implementing the feature to rate the experiments. Whenever the rating feature is implemented, the developer does not need to change anything in the codebase. The rating will automatically be displayed on the cards. A feature has been added to the cards rendered through the BulmaComponent that if the rating is zero it won’t be displayed (also 0 is default rating if rating for that experiment is not present).

# Troubleshooting:

- If the App script fails and the set trigger doesn’t update data into the database:
  - Go to the data sheet and then to Extensions -> App scripts. Therein you will find the pwa.gs file . Try running the file and logging the data being sent to verify that the sheet that has been selected by the code is correct and if the data being sent to the server is correct.
  - Now if the data is correct, and still the error remains, go to the AWS server where the lambda functions are hosted and check the error logs for the PWA_POST lambda function. For eg. One problem previously faced was that the request was getting timed out as the default time is 3 seconds before the request is timed out. Now it has been increased to 3 minutes.
- Pagination not working:
  - If the pagination is not working on switching the tabs or on setting some filters or searches , go to the ‘ExperimentLoader.js’ file. In this file the page numbers are being set everytime a tab is changed or a new filter is applied.

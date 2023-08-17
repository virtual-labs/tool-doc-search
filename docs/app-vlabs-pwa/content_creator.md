# Content Creator Guide: Virtual Labs PWA

## Table of Contents:

- [Introduction](#bookmark=id.wko2qzbs0yx0)
- [How to add your experiment to the PWA?](#bookmark=id.pjdlw68s8zuz)
- [Instructions for collection of metadata](#bookmark=id.iac3sazf81zo)

## Introduction:

- This document is intended for the virtual lab developers who are creating experiments for the virtual labs and want to display their experiments on the PWA. This document is a complete guide to add the experiment to the PWA.

## How to add your experiment to the PWA?

- To add an experiment, the prerequisites are:-
  - It should be hosted on the Virtual Labs website and should be working properly.
  - After you ensure that the experiment is working, you need to now collect the metadata for the experiment. This metadata will include an image for the experiment, a description and the tags which act as keywords while searching for experiments. For instructions refer to [this.](#bookmark=id.iac3sazf81zo)
- Once all this data has been collected, mail the following details at ‘**[ravi.kiran@vlabs.ac.in](mailto:ravi.kiran@vlabs.ac.in)’ :-**
  - Hosted Experiment URL
  - Lab Name
  - Experiment Name
  - Repository Link for the experiment
  - Image URL
  - Description
  - Tags

## Instructions for collection of Metadata:

- **Description**:
  To provide a concise description for each experiment, kindly write a brief summary in the designated sheet itself under the column titled "Description." The description should ideally be between **10 to 20 words** in length. You may refer to online sources such as ChatGPT for assistance in crafting the descriptions.
- **Image**
  - To select an appropriate image that aligns with the experiment's description or aim, please adhere to the following guidelines:
  - Ensure that the chosen image does not violate any copyright laws. It should either be freely available for download, have a public domain licence, or be licensed under Creative Commons for non-commercial use (CC-BY-NC).
  - You can explore the following online sources as examples:
    - [Category:Images - Wikimedia Commons](https://commons.wikimedia.org/wiki/Category:Images)
    - [Pngtree](https://pngtree.com/)
    - [Pixabay](https://pixabay.com/)
    - [Unsplash](https://unsplash.com/)
  - If you have access, you can also utilise DALL-E for generating the required images.
  - Specifications for the image - \
     Resolution : greater than or equal to 640 X 480 \
     Dimensions : Approximately 4 X 3 image \
     File size: should not exceed 50 KB
    - Image should be coloured.
    - Example image: [Depth First Search](https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQjOsQbQfN89fxRlSzJ9JOCLu6uAyrW5xsUjA&usqp=CAU)
    - Double check the licence agreement terms for any image you upload.
    - If you come across any other online sources that meet the copyright requirements, kindly share the link on Slack for the benefit of everyone involved.
    - Now after selecting the appropriate image take the following steps to upload this image:
      - Step 1 : Go to the repository of the experiment from
      - Step 2 : Make sure you are in the **dev** branch of the repository.
      - Step 3 : Add the image file to the repo and name it experiment-image.png/jpg
      - Step 4 : Go to the **testing** branch. Pull the **dev** branch changes into the testing branch
      - Step 5 : Go to the **main** branch. Pull the image from the **testing** branch into the main branch.
- **Tags** \
  Refer the experiment name, aim, theory and online sources and list relevant tags. Enter the tags as a comma separated list in the Tags column in the sheet. list out at least 5 tags for each experiment. The tags must be comma separated. Each tag can have space separated words, or have hyphens “-”. Use of any other characters are not permitted. The tags should be strictly relevant to the experiment. Do not include the experiment name, lab name, institute name and discipline name as tags.

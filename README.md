# Virtual Labs Document Search - Running Documentation

This document serves as a comprehensive guide to the Virtual Labs Document Search Tool, offering insights into its functionality, supported document types, processing procedures, and user interaction. It is designed to provide a clear understanding of the tool's usage for document searchers and managers while explaining the technical aspects.

## Table of Contents

- [Introduction](#introduction)
- [Problem Statement](#problem-statement)
- [Supported Document Types](#supported-document-types)
- [Document Processing](#document-processing-and-indexing)
- [Search Process](#search-process)
- [Search Result Filtering](#search-result-filtering)
- [User Interaction](#user-interaction)
  - [Writing Searchable Documents](#writing-searchable-documents)
  - [Crafting Effective Search Queries](#crafting-effective-search-queries)
- [How the Document Search Tool Works](#how-the-document-search-tool-works)
  - [Latency Numbers](#latency-numbers)
- [Document Insertion into Qdrant Vector Database](#document-insertion-into-qdrant-vector-database)
- [Determining Document Accessibility](#determining-document-accessibility)
  - [Permissions and Scopes](#permissions-and-scopes)
  - [Process of Accessibility Determination](#process-of-accessibility-determination)
- [Technology Stack](#technology-stack)
- [Deployment](#deployment)
- [Future Updates and Features](#future-updates-and-features)

## Introduction

The Document Search Tool for Virtual Labs is designed to alleviate the challenges associated with navigating vast collections of documents within the virtual labs environment. This tool serves as a powerful solution to efficiently retrieve relevant sections from a plethora of documents, ensuring that users can access the information they need promptly. This document serves as running documentation to help users understand the functionality and usage of the tool.

## Problem Statement

In a dynamic virtual labs ecosystem, the extensive volume of documents poses a significant challenge for users seeking specific information. Traditional manual search methods can be time-consuming and often result in information overload or missing relevant sections. The Document Search Tool addresses this issue by providing a seamless way to find and access precise sections within the documents.

## Supported Document Types

Following document formats are supported in Document Search tool.
| Serial No | Document Type | Format | URL Template | Accessibility |
| --------- | ------------- | ------ | ------------ | -------------- |
| 1 | Github Markdown | md | https://github.com/<\_ORGANISATION_NAME>/<\_REPO_NAME>/blob/<\_BRANCH>/PATH/TO/DOCUMENT.md <br/> https://github.com/virtual-labs/app-exp-create-web/blob/master/docs/user-doc.md | public/private |
| 2 | Google Document | gdoc | https://docs.google.com/document/d/<\_DOC_ID> <br/> https://docs.google.com/document/d/1ye4X5LcUlicv4Q-VE7pxYrjW8yj0Uep6EO3gZpR4SDw | public/private |
| 3 | Google Spreadsheet | xlsx | https://docs.google.com/spreadsheets/d/<\_DOC_ID> <br> https://docs.google.com/spreadsheets/d/1SUOs97mV0MUgad0shGq2Kfpl24RHyvSjtbzR4VrrRjM | public/private |
| 4 | Google Drive PDF | pdf | https://drive.google.com/file/d/<\_DOC_ID> <br/> https://drive.google.com/file/d/1kuPsaiC_3oDOrR8TWc4OGGzaapKaw1Qw | public/private |
| 5 | Github ORG mode | org | https://github.com/<\_ORGANISATION_NAME>/<\_REPO_NAME>/blob/<\_BRANCH>/PATH/TO/DOCUMENT.org <br/> https://github.com/virtual-labs/ph3-lab-mgmt/blob/master/docs/lab-build-process.org | public/private |
| 6 | Github File | - | https://github.com/<\_ORGANISATION_NAME>/<\_REPO_NAME>/blob/<\_BRANCH>/PATH/TO/file.extension <br/> https://github.com/virtual-labs/app-exp-create-web/blob/master/docs/user-doc.md | public/private |
| 7* | Drive File | - | https://drive.google.com/file/d/<\_DOC_ID> <br/> https://drive.google.com/file/d/1kuPsaiC_3oDOrR8TWc4OGGzaapKaw1Qw | public/private |
| 8* | Link | - | Any URL | - |

Context of public and private is explained in [this](#determining-document-accessibility) section. It's important to note that documents should follow specific formatting guidelines to ensure accurate segregation of relevant sections and effective searchability.

\* - These document/links are not supported in current version of Document Search tool. They will be stored as Page title and URL provided by user.

## Document Processing and Indexing

The process of adding documents to the database involves several key steps to ensure accurate indexing and efficient searching:
Document Insertion and Update
Document Selection: When a new document is to be added or an existing one is updated, the tool processes it to extract sections for indexing.

- **Section Extraction**: The document is broken down into sections based on headings. Each section is composed of a heading and the corresponding content beneath it. This ensures that every searchable section is well-defined and distinct.
- **Content Refinement**: To improve search quality and relevance, non-essential elements such as images and code snippets are removed from each section. This ensures that the embedded data primarily captures the textual context of the section.
- **Embedding and Upserting**: The refined sections are embedded using the all-MiniLM-L6-v2 model. These embeddings are stored in the Qdrant vector database alongside associated metadata, including the page title, heading, URL, and document type.
- **Database Maintenance**: When a document is inserted or updated, the tool automatically identifies all existing entries with the same page title and removes them from the database. This ensures that the most current version of the document's sections is consistently represented in the database.

## Search Process

When a user submits a query, the tool performs the following steps:
The user query is embedded using the sentence-transformer/all-MiniLM-L6-v2 model.
The database is searched for embeddings that closely match the query's embedding.
Results with the minimum distance to the query are returned, accompanied by associated metadata such as page title, heading, and URL.

## Search Result Filtering

Users can filter search results based on the document type, allowing for streamlined access to the desired content. Clear and refined queries contribute to more accurate search results.

## User Interaction

The effectiveness of the Document Search Tool relies not only on its advanced search capabilities but also on how documents are authored and how users formulate their search queries. Adhering to best practices ensures that the search results are relevant and accurate.

## Writing Searchable Documents

To ensure that subsections within your documents are effectively searchable, it's essential to adhere to a specific format that aligns with the capabilities of the Document Search Tool. The following guidelines outline the necessary criteria for creating searchable subsections:

- **Clear and Meaningful Headings**: Every subsection intended to be searchable must be accompanied by a clear and meaningful heading. It's important to note that simply increasing the font size of regular text in applications like Google Docs does not suffice to create a heading. Utilize the built-in heading formatting options provided by the document editor to designate a section as a proper heading. This ensures that the tool can accurately break down the content into distinct segments for indexing.
- **Section Introduction**: Enhance the search accuracy by including a brief introductory segment at the beginning of each subsection. These introductory lines should concisely summarize the content of the section. This contextual information aids the search algorithm in establishing accurate matches between user queries and section content.
- **User-Relatable Language**: Craft your document using language that resonates with potential user search queries. Aim to incorporate terms, phrases, and keywords that are likely to be used by users seeking the information contained in your document. This approach increases the relevance of search results and enhances the overall search experience.
- **Sample documents** :- [Sample Google Document](https://docs.google.com/document/d/1IeLZ3aZP_6k0CvqxuqkFn_TielGw6VVbZRQHPgNIUq4/) [Sample Markdown Document](https://github.com/virtual-labs/tool-doc-search/blob/dev/docs/sample_md.md)

## Crafting Effective Search Queries

Crafting well-defined search queries significantly impacts the quality of search results:

- **Specificity**: Be as specific as possible in your query. Include keywords related to the topic you're searching for within the document.
- **Contextual Information**: If applicable, include context in your query. Mention any relevant headings, topics, or keywords to narrow down your search.
- **Phrasing**: Phrase your query in a way that mirrors how you would naturally ask a question. This helps the tool understand your intent more accurately.
- **Filters**: Utilize document type filters if you're looking specifically for content within Google Docs or Markdown files.
- **Experimentation**: If you're not getting desired results, consider rephrasing your query or trying different keywords to improve search accuracy.
  By adhering to these guidelines when creating documents and crafting search queries, users can enhance the search experience and access the most relevant sections quickly.

## How the Document Search Tool Works

The Virtual Labs Document Search Tool offers functionality for two types of users:

**User Type 1: Document Searcher**

This user utilizes the search facility to find document sections. Here's how it works:

- The user accesses a user-friendly search interface provided by the frontend.
- The search facility offers a public API, making it accessible to anyone who needs to utilize this utility.
- Users can input their search queries to retrieve specific document sections.

**User Type 2: Document Manager**

The second type of user is responsible for adding documents to the database. This user must log in with their Google credentials to access the Flask application. Here's the workflow for this user:

1. **Login**: After successful login, the user gains access to a dedicated page within the Flask application.

2. **Document Management Table**: On this page, the user encounters a table displaying all documents (Page Titles) currently in the database. Each document is accompanied by a checkbox.

3. **Document Operations**:

   - **Update Selected Documents**: The user can select multiple documents by checking the corresponding checkboxes. Clicking the "Update selected documents" button will update all selected documents with their current content.
   - **Delete Selected Documents**: Similarly, by selecting multiple documents and clicking the "Delete selected documents" button, the user can delete those documents from the database.

4. **Document Title Search**: The page also features a search bar, which enables the user to search for document Page Titles with a case-insensitive sub-word search. This feature streamlines the process of locating specific documents.

5. **Upsert Documents**: Users can insert new documents via the "Upsert documents" button. This action opens a modal pane that contains a select box. Users can choose the number of documents they wish to insert from the available options (1 to 10). For each selected number, a corresponding number of URL input boxes is generated. Users should paste the URLs of the documents they want to add and click the submit button.

### Latency Numbers

The Document Search Tool processes the insertion of documents with varying latencies. For 8 documents, it approximately takes around 25-30 seconds to complete the upsert operation. This may vary with content size for different batches of documents. For delete operation it is 2-3 seconds.

## Document Insertion into Qdrant Vector Database

When a batch of documents is received, the Document Search Tool follows a meticulous process to insert these documents into the Qdrant vector database. This process varies depending on whether the document is in Markdown (md) or Google Docs (gdoc) format:

**Markdown File**

For Markdown files, the following steps are undertaken:

1. **Fetching and Parsing Markdown Code**: The tool fetches the Markdown code and parses it.

2. **Document Chunk Formation**: The tool creates document chunks by breaking down the document into sections. This segmentation is based on heading identifiers (e.g., #, ##, ...) and includes all the text below each heading until the next heading is encountered.

3. **Section Link Generation**: A unique section link is generated for each heading. The first heading in the document is assigned as the Page Title for the document.

4. **Vector Encoding**: For each document chunk, the tool creates a vector by encoding the content using the selected embedding model. This vector captures the semantic meaning of the content.

5. **Payload Information**: Each document chunk is associated with a payload containing the following information:

   - "page_title": Page title for the document, which corresponds to the first heading.
   - "heading": The section heading.
   - "text": The content inside that section.
   - "url": The URL for that section.
   - "src": Document source i.e Drive, GitHub or Web.
   - "accessibility": Indicates whether the document is public or private (for Markdown files, it is typically public as only public documents are allowed for Markdown).
   - "type": Indicates whether it's a Markdown document (md) or a Google Document (gdoc).
   - "base_url": The URL of the entire document.
   - "inserted_by": The name of the person who inserted that document.

6. **Document URL as Identifier**: The document URL serves as the identifier for that particular document. All delete and upsert operations filter chunks based on the URL. Therefore, it's crucial to retain the URL unchanged.

7. **Inserting points in VectorDB**: Points i.e vectors along with their corresponding payload are inserted into the Qdrant vector database.

**Google Document File**

For Google Document files (both [public and private](#determining-document-accessibility)), the following steps are executed:

1. **Fetching as HTML**: Google Documents are fetched as HTML files.

2. **HTML Content Parsing**: The content is parsed by converting all headings (e.g., h1, h2, ...) into Markdown format (#, ##, ...). The content inside `<p>` tags is added as text for that heading.

3. **Markdown Content Generation**: In this manner, a Markdown content is generated.

4. **Follow Markdown File Procedure**: The same procedure is applied to this generated Markdown content as outlined in the "Markdown File" section above.

This process ensures that documents, whether in Markdown or Google Docs format, are effectively segmented, encoded, and stored in the Qdrant vector database for efficient and accurate retrieval.

**Google Sheets**

For Google Sheets (both [public and private](#determining-document-accessibility)), the following steps are executed:

1. **Fetching**: Google Sheets are fetched using python library `gspread`.

2. **Document Chunk Formation**: Each worksheet is treated as a section. Each section will contain upto first 10 rows X 26 columns of that particular worksheet.

3. **Follow Markdown File Procedure**: The same procedure is applied to this generated content as outlined in the "Markdown File" section Pt. 3 above.

**ORG mode**

For GitHub ORG mode (both [public and private](#determining-document-accessibility)), the following steps are executed:

1. **Fetching and Parsing ORG Code**: The tool fetches the ORG mode code and parses it.

2. **Document Chunk Formation**: The tool creates document chunks by breaking down the document into sections. This segmentation is based on heading identifiers (e.g., \*, \*\*, ...) and includes all the text below each heading until the next heading is encountered.

3. **Follow Markdown File Procedure**: The same procedure is applied to this generated content as outlined in the "Markdown File" section Pt. 3 above.

**Google Drive PDF**

For Google Drive PDF (both [public and private](#determining-document-accessibility)), the following steps are executed:

1. **Fetching**: PDF file from google drive are fetched. PDF file is downloaded on local disk.

2. **Document Chunk Formation**: Document chunks are formed using [llmsherpa](https://github.com/nlmatics/llmsherpa) library.

3. **Follow Markdown File Procedure**: The same procedure is applied to this generated content as outlined in the "Markdown File" section Pt. 3 above.

### Determining Document Accessibility

The Document Search Tool employs a mechanism to distinguish between public and private Documents. This determination is made through a systematic process using the Google/Github credentials of the Virtual Labs credentials stored in backend, along with specific permissions and scopes.

- **Github** - The tool first tries to fetch github document without any Personal Access token, If the file is successfully retrieved, it is considered as "public" and if not the tool utilizes the Github Personal Access Token of the Virtual Labs account to fetch the GitHub file from the Github repository. If the file is successfully retrieved, it is considered as "private" else 404 error.

- **Google Drive/Doc/Sheet** - ......

### Permissions and Scopes

The tool utilizes Google credentials with the following required permissions/scopes:

- https://www.googleapis.com/auth/drive.readonly
- https://www.googleapis.com/auth/userinfo.profile
- https://www.googleapis.com/auth/userinfo.email
- openid

### Process of Accessibility Determination

The tool follows the steps below to ascertain the accessibility of a Google Document:

1. **Fetching Without Access Token (Public Check)**: Initially, the tool attempts to fetch the Google Document without using the access token of the user. If this request is successful and the document is retrieved, it is considered as "public." This signifies that the document is accessible to users without specific access restrictions.

2. **Fetching With Access Token (Private Check)**: Following the public check, the tool proceeds to fetch the Google Document with the access token of the logged-in user. If this request is successful and the document is retrieved, it is considered as "private." This indicates that the document has access restrictions and can only be viewed by authorized users.

3. **Exception Handling**: In cases where the fetching operation fails, the tool returns an exception to the user, accompanied by an appropriate error message. This typically occurs when there are access restrictions that prevent successful retrieval.

By implementing this process, the Document Search Tool effectively distinguishes between public and private Google Documents, ensuring accurate categorization of document accessibility for users.

## Technology Stack

- **Frontend**: Developed in ReactJS with TailwindCSS for styling.
- **Server**: A Flask application developed in Python (all dependency modules can be found in requirements.txt).
- **Database**: Vector database Qdrant.
- **Embedding Model**: Utilizes the sentence-transformer/all-MiniLM-L6-v2 model for text embedding.

## Deployment

- The Flask App will be deployed on Google App Engine.
- The React App will be deployed on Netlify as per the proposed deployment model.

## Future Updates and Features

- Current implementation of Page Title search is sub-word based. It can be improved by using a same semantic search model as used for section search.

- Optimize search query by Binary Quantization https://qdrant.tech/articles/binary-quantization/

- Modify embedding template for better semantic by placing all subheadings ahead of text.

- Add theme feature to search and insert page.

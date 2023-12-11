# Developer Document - Virtual Labs Document Search Tool

This document serves as a comprehensive technical guide to the Virtual Labs Document Search Tool, offering insights into its functionality, supported document types, processing procedures. It is designed to provide a clear understanding of the tool's technical aspects.

## Table of Contents

- [Introduction](#introduction)
- [How Document Search Tool Works](#how-document-search-tool-works)
- [Design Decisions](#design-decisions)
- [Project Directory Structure](#project-directory-structure)
- [Code Modules](#code-modules)
- [Supported Document Types](#supported-document-types)
- [Document Processing](#document-processing-and-indexing)
- [Search Process](#search-process)
- [Latency Numbers](#latency-numbers)
- [Document Insertion into Qdrant Vector Database](#document-insertion-into-qdrant-vector-database)
- [Determining Document Accessibility](#determining-document-accessibility)
- [Permissions and Scopes](#permissions-and-scopes)
- [Technology Stack](#technology-stack)
- [Deployment](#deployment)
- [Future Updates and Features](#future-updates-and-features)

## Introduction

The Virtual Labs Document Search Tool is designed with two distinct user interface components: the publicly accessible Search Page developed in ReactJS with TailwindCSS, and the authenticated Insert/Update Page using HTML, CSS, and VanillaJS. Authentication is managed through Google OAuth for users associated with the Virtual Labs organization. The backend server is a Python Flask application responsible for handling requests, document processing, and managing the Qdrant Vector Database. The database is a vector database that stores document embeddings and is queried using the user's search query embedding.

## How Document Search Tool Works

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
   - **Remove Selected Documents**: Similarly, by selecting multiple documents and clicking the "Delete selected documents" button, the user can remove those documents from the database.

4. **Document Title Search**: The page also features a search bar, which enables the user to search for document Page Titles with a case-insensitive sub-word search. This feature streamlines the process of locating specific documents.

5. **Insert/Update Drive Folder**: Users can insert google drive via the "Insert/Update Drive Folder" button. This action opens a modal pane that contains a form. Users should paste the URL of the folder they want to add and click the submit button.

6. **Insert/Update Documents**: Users can insert new documents via the "Insert/Update Documents" button. This action opens a modal pane that contains a select box. Users can choose the number of documents they wish to insert from the available options (1 to 10). For each selected number, a corresponding number of URL input boxes is generated. Users should paste the URLs of the documents they want to add and click the submit button.

## Design Decisions

The design of the Virtual Labs Document Search Tool is driven by several key technical decisions to ensure efficiency, scalability, and maintainability. Below are the significant design decisions made during the development process:

### **Qdrant for Vector Similarity Search**

The choice of using Qdrant, a vector similarity search engine, for storing and querying document vectors is a fundamental design decision. Qdrant provides efficient similarity searches, enabling fast and accurate document retrieval based on vector representations. This decision ensures optimal performance for search queries across a large collection of documents.

### **String match scoring for better results**

The Search page employs a string match scoring mechanism to improve the relevance of search results. Results from the Qdrant vector database are ranked based on the number of occurrences of the search query in the document. This scoring mechanism is implemented in the following ways:

```javascript
// search-page-react/src/utils/utils.js

const countToWeightFunction = (cnt) => {
  return 5 * Math.log2(1 + 0.1 * cnt);
};

const getRankedResult = (results, search_query) => {
  search_query = search_query.trim().toLowerCase();
  if (!search_query) return results;

  const searchWords = getSubWords(search_query);
  const rankedResults = [];

  for (let result of results) {
    const lowerCaseResult = result?.text?.toLowerCase();
    const lowerCaseHeading = result.heading.toLowerCase();

    let score = 0;
    for (let word of searchWords) {
      const resultCnt = countSubstringOccurrences(
        lowerCaseResult,
        word.sentence
      );
      const headingCnt = countSubstringOccurrences(
        lowerCaseHeading,
        word.sentence
      );
      score +=
        word.score *
        (result.type === "xlsx"
          ? !resultCnt
            ? 0
            : countToWeightFunction(1)
          : countToWeightFunction(resultCnt));
      score +=
        word.score *
        countToWeightFunction(headingCnt) *
        countToWeightFunction(10);
    }

    rankedResults.push({
      ...result,
      rank: score + result.score * 100,
      ascore: score,
    });
  }

  rankedResults.sort((a, b) => b.rank - a.rank);
  // console.log(rankedResults);
  return rankedResults;
};
```

### **Google OAuth for Authentication**

To secure access to the Insert/Update Page, the Document Search Tool integrates Google OAuth for authentication. This decision leverages the robust authentication mechanisms provided by Google, ensuring that only authorized users from the Virtual Labs organization can interact with the authenticated components of the tool.

### **Multi-Format Support**

The tool is designed to support documents in various formats. Every document is boiled down into chunks with same properties irrespective of its format type.

```python
# chunk structure
chunk = {
    "text": f"{heading} of {page_title} :: {page_title} :: {text_of_the_section}",
    "payload": {
        "page_title": "Sample Page Title",
        "heading": "Sample Section",
        "url": "https://sampleurl.com#sample-section",
        "src": "web",
        "accessibility": "public",
        "type": "md",
        "base_url": "https://sampleurl.com",
        "inserted_by": "unknown",
        "text": f"{text_of_the_section}"
    }
}
```

The integration of the Sentence Transformers library allows the tool to encode and process text, enhancing its versatility and usability across diverse document types. `chunk["text"]` is used for encoding and `chunk["payload"]` is used for storing payload along with encoding vector in qdrant.

### **Batch Processing for Document Insertion/Updation**

The DocumentSearch class includes batch processing capabilities for efficient document insertion. The upsert_batchs method optimally handles the insertion of document batches into the Qdrant collection, improving overall performance and reducing processing time for large sets of documents.

### **Payload Indexing for Enhanced Search**

Payload indexing is employed to index specific fields (e.g., type, page_title) within documents, enhancing the filter search capabilities of the tool.

### **Public/Private Accessibility Design**

The Document Search Tool incorporates both public and private documents. The design of the tool ensures that public documents are accessible to all users, while private documents are only accessible to authorized users. This design decision is implemented in the following ways:

- **Public Documents**: Public documents are accessible to all users, including those outside the Virtual Labs organization. The search interface displays the page title, URL, and content of public documents in the search results. This ensures that the search functionality is available to all users, while the content of public documents is accessible to all users.

- **Private Documents**: Private documents are only accessible to authorized users. The search interface displays the page title and URL of private documents in the search results. This ensures that the search functionality is available to all users, while the content of private documents remains inaccessible. By clicking on the URL, users can request access to the document. Also, payload for private documents is not storing the content of the document. Content of private documents is used only for encoding.

### **Google Documents Accessibility**

The accessibility of Google Documents is determined by the permissions associated with the document. If the document is accessible (viewer/editor) to anyone with the link, it is considered public. Otherwise, it is considered private. Permissions are fetched using the Google service account of the Virtual Labs organization through the Google Drive Permission API.

```python
# document_parser.py

def fetch_metadata_gdrive(doc_id):

    SCOPES = ['https://www.googleapis.com/auth/drive']
    SERVICE_ACCOUNT_FILE = os.path.join(
        pathlib.Path(__file__).parent, "../secrets/service-account-secret.json")
    credentials = None
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    service = build('drive', 'v3', credentials=credentials)

    file_metadata = service.files().get(fileId=doc_id).execute()

    # deciding accessibility
    try:
        permissions = service.permissions().get(
            fileId=doc_id, permissionId="anyoneWithLink").execute()

        if permissions.get("role") in ["reader", "writer", "editor", "viewer"]:
            file_metadata["accessibility"] = "public"
        else:
            file_metadata["accessibility"] = "private"

    except Exception as e:
        file_metadata["accessibility"] = "private"

    return file_metadata

```

### **Github Documents Accessibility**

The accessibility of Github Documents is determined by simply requesting content by requests library. If the document is accessible, it is considered public. Otherwise, The Github Personal Access Token of the Virtual Labs organization is used to access private documents.

```python
# document_parser.py

def get_github_accessibility_with_content(raw_url):
    access_token = os.getenv("GITHUB_ACCESS_TOKEN")
    headers = {'Authorization': f'token {access_token}'}

    response = requests.get(raw_url)

    if response.status_code == 200:
        return "public", response.text

    elif response.status_code == 404:
        response = requests.get(raw_url, headers=headers)
        if response.status_code == 200:
            return "private", response.text
        else:
            raise NotFoundException(
                "Document not found. Invalid document link")
    else:
        raise Exception("Error occurred while fetching document")
```

### Public Search Page

- The Search Page, developed using ReactJS and TailwindCSS, is designed to be publicly accessible. This means that users, including those outside the Virtual Labs organization, can search Virtual Labs documents without authentication. The decision to make the search interface public enhances usability and allows a broader audience to benefit from the tool's core feature.
- For `private` documents, only the page title and URL are displayed in the search results. This ensures that the search functionality is available to all users, while the content of private documents remains inaccessible. By clicking on the URL, users can request access to the document.

### Authenticated Insert/Update Page

Conversely, the Insert/Update Page is restricted to authenticated users within the Virtual Labs organization. Authentication is achieved through Google OAuth, adding a layer of security to prevent unauthorized access. This decision ensures that only authorized personnel can insert or update documents in the system, maintaining control over the content and integrity of the document repository.

By implementing this public/private accessibility design, the Document Search Tool provides an inclusive search experience for the public while safeguarding sensitive operations and data within the authenticated domain of the Virtual Labs organization.

These design decisions collectively contribute to the effectiveness, extensibility, and robustness of the Virtual Labs Document Search Tool, providing users with a powerful and user-friendly document search experience.

## Project Directory Structure

The directory structure of the Virtual Labs Document Search Tool project is as follows:

```
utils
├── delete_doc_util.py
├── doc_info.py
├── doc_instances.py
├── doc_record.py
├── doc_search.py
├── document_parser.py
├── insert_doc_util.py

static
├── css
│   ├── insert_doc.css
│   └── main.css
├── img
└── js
    ├── add_url.js
    ├── document_type.js
    ├── insert_folder.js
    ├── insert_pane.js
    ├── logout.js
    └── main.js

blueprints
├── insert_doc.py
└── search_doc.py

error
└── CustomException.py

templates
└── update_document_page.html

pdf_downloads

secrets
├── client_secret.json
└── service-account-secret.json

search-page-react
├── package.json
├── package-lock.json
├── public
├── src
│   ├── App.js
│   ├── components
│   │   ├── GoogleSheetStyleTable.js
│   │   ├── HighlightedText.js
│   │   ├── index.js
│   │   ├── NavBar.js
│   │   ├── ResultViewBox.js
│   │   ├── search-box-component
│   │   │   ├── index.js
│   │   │   ├── QueryBox.js
│   │   │   ├── ResultBox.js
│   │   │   └── ResultPane.js
│   │   └── SearchBox.js
│   ├── css
│   │   ├── App.css
│   │   └── index.css
│   ├── index.js
│   ├── media
│   └── utils
│       ├── config_data.js
│       └── utils.js
└── tailwind.config.js

.env
.gitignore
requirements.txt
server.py
LICENSE
README.md
```

The directory structure provides a logical organization of the project's files and modules. Each directory contains files specific to its corresponding module or functionality.

## Code Modules

#### .env

This file contains the environment variables required for the project. It contains the following variables:

```
QDRANT_API= [Qdrant API Key]
QDRANT_URL= [Qdrant end point]
QDRANT_COLLECTION= [Qdrant document chunk collection name]
QDRANT_RECORD_COLLECTION= [Qdrant document record collection name]
QDRANT_FOLDER_COLLECTION= [Qdrant folder collection name]
GOOGLE_CLIENT_ID= [Google Client ID for OAuth App]
CALLBACK_URL= [Callback URL for OAuth App]
GITHUB_ACCESS_TOKEN= [Github Personal Access Token used to access private documents]
```

#### requirements.txt

This file contains all python dependencies required for the Flask App. Run following command to install all dependencies.

```
pip install -r requirements.txt
```

#### server.py

This file contains the Flask App. It uses flask blueprints to separate the search and insert into different modules.

#### blueprints/insert_doc.py

This file contains the insert blueprint. It handles all insert/update/delete related requests which are authorized by Google OAuth. It also handles the requests for inserting/updating google drive folder.

- It uses `utils/insert_doc_util.py` and `utils/delete_doc_util.py` for inserting/updating and removing document/folder respectively.
- It is routed to `/insert_doc` endpoint. Login page is routed to `/insert_doc/login` endpoint. `/insert_doc/callback` endpoint is used for Google OAuth callback.
- `/insert_doc/protected_area` endpoint is used for Insert Page after successful login. It has both GET and POST methods. GET method is used to render the Insert Page and POST method is used to handle the requests for inserting/updating/deleting documents/folders.

  - Its POST method takes two arguments `action` and `data`.
  - `action` is ENUM which can be
    - `insert`, `update`, `delete` - for documents
    - `folder-insert`, `folder-update`, `folder-delete` - for g-drive folder.
  - `data` is a JSON object which contains the data for the corresponding action.

- `/insert_doc/get_docs` endpoint is used for fetching all documents records from Qdrant Vector Database Record collection to display on document management table. It is a `GET` method which takes two arguments `page` and `search_query`.

- `/insert_doc/logout` endpoint is used for logging out the user.

#### blueprints/search_doc.py

This file contains the search blueprint. It handles all search related requests for Search Page.

- It contains only one endpoint `/api/search` which is used for searching documents in Qdrant Vector Database.

- This endpoint is a `POST` method which accepts following parameters in request body:

  - `search_query`: Search query (STRING)
  - `limit`: Limit of results (INTEGER)
  - `thresh`: Thresh hold for similarity score (FLOAT 0.0-1.0)
  - `doc_filter`: Document type filter (STRING)
  - `src_filter`: Document source filter (ENUM {web, drive, github, Any})
  - `acc_filter`: Document accessibility filter (ENUM {public, private, Any})
  - `page_title_filter`: Page title filter (STRING)

#### utils/doc_search.py

This file contains the `DocumentSearch` class. It initializes connection to Qdrant document chunks collection. is It contains the following functions:

- insert_doc_batch(self, docs, credentials, user="unknown", operation="insert"):
- insert_drive_folder(self, folderUrl, credentials, user="unknown", operation="insert"):
- get_search_result(self, search_query,
  limit=10,
  thresh=0.0,
  doc_filter="Any",
  src_filter="Any",
  acc_filter="Any",
  page_title_filter=""):
- delete_doc(self, urls, user="unknown"):

#### utils/doc_record.py

This file contains the `DocumentRecord` class. It initializes connection to Qdrant document record collection. is It contains the following functions:

- insert_entry(self, docs, operation="insert"):
- insert_folder_entry(self, docs, operation="insert"):
- get_docs(self, search_query, page):
- delete_folder(self, folderUrl, user="unknown"):

#### utils/doc_instances.py

This file initialises and exports instances of `DocumentSearch` and `DocumentRecord` classes.

#### utils/document_parser.py

This file contains all utility functions for parsing documents of different types. It contains the following function:

- get_chunks_batch(docs, credentials, user):
  - docs - List of document URLs with type
  - credentials - Google credentials
  - user - Name of the user who is inserting/updating the documents

#### utils/document_parser.py

This file contains all utility functions for parsing documents of different types. It contains the following function:

- get_chunks_batch(docs, credentials, user):
  - docs - List of document URLs with type
  - credentials - Google credentials
  - user - Name of the user who is inserting/updating the documents

#### templates

This directory contains the HTML template for Insert Page.

#### static

This directory contains all static files for Insert Page.

#### static/js

This directory contains all javascript files for Insert Page. It contains the following files:

- `main.js` - It contains all the functions for Insert Page.
- `insert_pane.js` - It contains all the functions for Insert modal which appears after clicking `Insert/Update documents with URL` button on main page.
- `insert_folder.js` - It contains all the functions for Insert Folder Pane.
- `add_url.js` - It contains all the utility functions for adding URL input boxes dynamically in Insert modal through select box.
- `document_type.js` - It contains all functions for validating document url with document type through regex and pattern.
- `logout.js` - Contains utility functions for logout.

#### secrets

- `client_secret.json` - Google OAuth client secret file.
- `service-account-secret.json` - Google service account secret file.

#### search-page-react

This directory contains the React App for Search Page.

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
- **Embedding and Upserting**: The refined sections are embedded using the `all-MiniLM-L6-v2` model. These embeddings are stored in the Qdrant vector database alongside associated metadata, including the page title, heading, URL, and document type.
  - "page_title": Page title for the document, which corresponds to the first heading.
  - "heading": The section heading.
  - "text": The content inside that section.
  - "url": The URL for that section.
  - "src": Document source i.e Drive, GitHub or Web.
  - "accessibility": Indicates whether the document is public or private.
  - "type": format type.
  - "base_url": The URL of the entire document.
  - "inserted_by": The name of the person who inserted that document.

```python

# payload structure
    def get_payload(page_title, heading, text, url, type, base_url, user, src="web"):
    return {
        "page_title": page_title.strip(),
        "heading": heading.strip(),
        "text": text.strip(),
        "url": url.strip(),
        "type": type.strip(),
        "base_url": base_url.strip(),
        "src": src.strip()
    }
# document_parser.py
# accessibility of document is determined later in the process
```

- **Database Maintenance**: When a document is inserted or updated, the tool automatically identifies all existing entries with the same page title and removes them from the database. This ensures that the most current version of the document's sections is consistently represented in the database.

## Search Process

When a user submits a query, the tool performs the following steps:
The user query is embedded using the `sentence-transformer/all-MiniLM-L6-v2` model.
The database is searched for embeddings that closely match the query's embedding.
Results with the minimum distance to the query are returned, accompanied by associated metadata such as page title, heading, and URL.

## Latency Numbers

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
   - "accessibility": Indicates whether the document is public or private.
   - "type": document format type.
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

## Determining Document Accessibility

The Document Search Tool employs a mechanism to distinguish between public and private Documents. This determination is made through a systematic process using the Google/Github credentials of the Virtual Labs credentials stored in backend, along with specific permissions and scopes.

- **Github** - The tool first tries to fetch github document without any Personal Access token, If the file is successfully retrieved, it is considered as "public" and if not the tool utilizes the Github Personal Access Token of the Virtual Labs (`GITHUB_ACCESS_TOKEN .env`) account to fetch the GitHub file from the Github repository. If the file is successfully retrieved, it is considered as "private" else 404 (Not Found) error.

- **Google Drive/Doc/Sheet** - The tool employs a google service account of virtual labs (doc-metadata-retrieval@document-search-398511.iam.gserviceaccount.com) to fetch metadata and permissions `(with permission id = 'anyoneWithLink')` for any google document which has editor access to this a/c, if permissions contains anyoneWithLink with role writer or reader, it is considered as "public" else "private".

- **link** - They are considered as `public` by default.

## Permissions and Scopes

The tool utilizes Google credentials with the following required permissions/scopes:

```python
scopes=[
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/userinfo.email",
        'https://www.googleapis.com/auth/spreadsheets.readonly',
        "https://www.googleapis.com/auth/drive.metadata.readonly",
        "openid"]
```

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

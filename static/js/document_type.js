function validate_gdoc(url) {
  let pref = "https://docs.google.com/document/d/";
  url = url.trim();
  return url.startsWith(pref) && url.length > pref.length;
}

function validate_md(url) {
  let pref = "https://github.com/";
  url = url.trim();
  let tokens = url.slice(8).split("/");
  return url.startsWith(pref) && tokens[3] === "blob" && url.endsWith(".md");
}

function validate_org(url) {
  let pref = "https://github.com/";
  url = url.trim();
  let tokens = url.slice(8).split("/");
  return url.startsWith(pref) && tokens[3] === "blob" && url.endsWith(".org");
}

function validate_pdf(url) {
  let pref = "https://github.com/";
  url = url.trim();
  let tokens = url.slice(8).split("/");
  return url.startsWith(pref) && tokens[3] === "blob" && url.endsWith(".md");
}

function validate_github(url) {
  let pref = "https://github.com/";
  url = url.trim();
  let tokens = url.slice(8).split("/");
  return url.startsWith(pref) && tokens[3] === "blob";
}

function validate_url(url) {
  return /^(?:(?:(?:https?|ftp):)?\/\/)(?:\S+(?::\S*)?@)?(?:(?!(?:10|127)(?:\.\d{1,3}){3})(?!(?:169\.254|192\.168)(?:\.\d{1,3}){2})(?!172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2})(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))|(?:(?:[a-z\u00a1-\uffff0-9]-*)*[a-z\u00a1-\uffff0-9]+)(?:\.(?:[a-z\u00a1-\uffff0-9]-*)*[a-z\u00a1-\uffff0-9]+)*(?:\.(?:[a-z\u00a1-\uffff]{2,})))(?::\d{2,5})?(?:[/?#]\S*)?$/i.test(
    url
  );
}

const documentTypeIdentifiers = {
  md: {
    page_title_req: false,
    validate: validate_md,
    fetch_content: true,
  },
  gdoc: {
    page_title_req: false,
    validate: validate_gdoc,
    fetch_content: true,
  },
  org: {
    page_title_req: false,
    validate: validate_org,
    fetch_content: true,
  },
  github: {
    page_title_req: true,
    validate: validate_github,
    fetch_content: false,
  },
  unknown: {
    page_title_req: true,
    validate: validate_url,
    fetch_content: false,
  },
};

function identifyDocumentType(url) {
  for (const type in documentTypeIdentifiers) {
    const identifier = documentTypeIdentifiers[type].validate;
    const result = identifier(url);
    if (result) {
      return type;
    }
  }
  return "";
}

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

const documentTypeIdentifiers = {
  md: { page_title_req: false, validate: validate_md },
  gdoc: { page_title_req: false, validate: validate_gdoc },
  github: {
    page_title_req: true,
    validate: validate_github,
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

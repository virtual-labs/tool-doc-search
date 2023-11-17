const DEFAULT_SECTION = {
  accessibility: "public",
  document: "Page title",
  heading: "Section Heading",
  text: "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse varius enim in eros elementum tristique. Duis cursus, mi quis viverra ornare, eros dolor interdum nulla, ut commodo diam libero vitae erat. Aenean faucibus nibh et justo cursus id rutrum lorem imperdiet. Nunc ut sem vitae risus tristique posuere.",
  type: "link",
  url: "#",
  base_url: "#",
};

const DEFAULT_QUERY = {
  search_query: "",
  limit: 10,
  thresh: 0.15,
  doc_filter: "Any",
  src_filter: "Any",
  acc_filter: "Any",
  page_title_filter: "",
};

const DOCUMENT_TYPES = [
  { type: "Any", title: "" },
  { type: "md", title: "Markdown Github" },
  { type: "org", title: "ORG mode File" },
  { type: "gdoc", title: "Google Document" },
  { type: "xlsx", title: "Google Sheet" },
  { type: "github", title: "Github File" },
  // { type: "drive", title: "Google Drive File" },
  { type: "link", title: "Link" },
  { type: "pdf", title: "PDF file" },
];

const ACCESSIBILITY_TYPES = [
  { type: "Any", title: "" },
  { type: "private" },
  { type: "public" },
];

const SRC_TYPES = [
  { type: "Any", title: "" },
  { type: "github", title: "Github File" },
  { type: "drive", title: "Google Drive File" },
  { type: "web", title: "Web" },
];

const INSERT_DOC_URL = "http://127.0.0.1:5000/insert_doc/login";
const SEARCH_API = "http://127.0.0.1:5000/api/search";

export {
  DEFAULT_SECTION,
  DOCUMENT_TYPES,
  INSERT_DOC_URL,
  DEFAULT_QUERY,
  SEARCH_API,
  ACCESSIBILITY_TYPES,
  SRC_TYPES,
};

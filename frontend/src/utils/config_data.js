const default_section = {
  accessibility: "public",
  document: "Page title",
  heading: "Section Heading",
  text: "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse varius enim in eros elementum tristique. Duis cursus, mi quis viverra ornare, eros dolor interdum nulla, ut commodo diam libero vitae erat. Aenean faucibus nibh et justo cursus id rutrum lorem imperdiet. Nunc ut sem vitae risus tristique posuere.",
  type: "Github / Google Document",
  url: "#",
};

const DOCUMENT_TYPES = [
  { type: "Any" },
  { type: "md" },
  { type: "org" },
  { type: "gdoc" },
  { type: "xlsx" },
  { type: "github" },
  { type: "drive" },
  { type: "unknown" },
];

const INSERT_DOC_URL = "http://127.0.0.1:5000/insert_doc/login";

export { default_section, DOCUMENT_TYPES, INSERT_DOC_URL };

import { useState } from "react";
import "./css/index.css";
import "./css/App.css";
import NavImg from "./media/download.png";
import LoadingImg from "./media/loading-73.gif";
import GoogleSheetStyleTable from "./components/GoogleSheetStyleTable";
import {
  default_section,
  DOCUMENT_TYPES,
  INSERT_DOC_URL,
} from "./utils/config_data";
import React from "react";

const getResultText = (accessibility, text, type, present = false) => {
  if (type === "xlsx" && present) {
    let data = JSON.parse(text);
    return <GoogleSheetStyleTable data={data} />;
  }
  if (accessibility === "private") {
    return "This is a private document.";
  }
  if (!present) {
    if (text.length > 200) return text.slice(0, 200) + "...";
    else return text;
  }
  const lines = String(text)?.split("\n");
  const textWithLineBreaks = lines.map((line, index) => (
    <React.Fragment key={index}>
      {line.split("\t").map((part, i) => (
        <React.Fragment key={i}>
          {i > 0 && <span>&nbsp;&nbsp;&nbsp;&nbsp;</span>} {part}
        </React.Fragment>
      ))}
      {index !== lines.length - 1 && <br />}
    </React.Fragment>
  ));
  return textWithLineBreaks;
};

function App() {
  const [query, setQuery] = useState({
    search_query: "",
    limit: 10,
    thresh: 0.15,
    doc_filter: "Any",
    page_title_filter: "",
  });

  const [results, setResults] = useState([]);

  const [loader, setLoading] = useState(false);

  const [present, setPresent] = useState(default_section);

  const getResults = async (e) => {
    e.preventDefault();
    if (loader) return;
    if (
      query.search_query.trim() === "" &&
      query.page_title_filter.trim() === ""
    ) {
      return;
    }

    const url = "http://127.0.0.1:5000/api/search";
    try {
      const config = {
        method: "POST",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
          "Access-Control-Allow-Origin": "*",
          Connection: "keep-alive",
        },
        body: JSON.stringify(query),
      };
      console.log(config);
      setLoading(true);
      setPresent(default_section);
      let response = await fetch(url, config);
      response = await response.json();
      setResults(response.result);
    } catch (error) {
      console.log(error);
    } finally {
      setLoading(false);
    }
  };

  const setQueryText = (e) => {
    setQuery({ ...query, search_query: e.target.value });
  };

  const setQueryDocFilter = (e) => {
    setQuery({ ...query, doc_filter: e.target.value });
  };

  const setQueryPageFilter = (e) => {
    setQuery({ ...query, page_title_filter: e.target.value });
  };

  const isDrivePDF = (doc) => {
    let slices = present.url.split("#");
    return (
      present.type === "drive" && slices[slices.length - 1]?.startsWith("page=")
    );
  };

  const getPageSpan = (doc) => {
    let slices = present.url.split("#");
    let page_comp = slices[slices.length - 1];
    let page_num = Number(page_comp.slice(5, page_comp.length));
    return <span className="drive-pdf-pagenum">Page {page_num}</span>;
  };

  const getHeading = (url, type) => {
    if (url === "#") return "Github / Google Document";
    if (type === "md") return "Markdown Github";
    if (type === "gdoc") return "Google Document";
    if (type === "xlsx") return "Google Sheet";
    if (type === "org") return "ORG mode File";
    if (type === "github") return "Github File";
    if (type === "unknown") return "Unknown Type";
    return "Not Supported";
  };

  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden">
      <div className="flex">
        <div className="navbar-no-shadow-container w-nav">
          <div className="navbar-wrapper">
            <img
              src={NavImg}
              loading="lazy"
              width="80"
              af-el="nav-img"
              alt=""
            />
            <div af-el="nav-title" className="text-block">
              Document Search
            </div>
            <div style={{ float: "right", marginLeft: "auto" }}>
              <button
                className="insert-doc-button"
                onClick={() => window.open(INSERT_DOC_URL, "_blank")}
              >
                Insert Document
              </button>
            </div>
          </div>
        </div>
      </div>
      <div className="flex flex-1 flex-row flex-block overflow-hidden">
        <div className="flex flex-col w-2/5 overflow-hidden">
          <div className="flex w-full">
            <form
              id="email-form"
              name="email-form"
              data-name="Email Form"
              method="get"
              className="form w-full"
            >
              <input
                type="text"
                className="search-query w-input"
                maxLength="256"
                name="name"
                data-name="Name"
                placeholder="Enter search query..."
                value={query.search_query}
                id="name"
                onChange={setQueryText}
              />
              <input
                type="submit"
                value="Search"
                data-wait="Please wait..."
                className="submit-button w-button"
                onClick={getResults}
              />
              <input
                type="text"
                className="page-title-filter"
                maxLength="256"
                name="field"
                data-name="Field"
                placeholder="Add page title filter...."
                value={query.page_title_filter}
                id="field"
                onChange={setQueryPageFilter}
              />
              <select
                id="select-doctype"
                name="select-doctype"
                data-name="select-doctype"
                className="select-doc-type"
                value={query.doc_filter}
                onChange={setQueryDocFilter}
              >
                {DOCUMENT_TYPES.map((doc, i) => {
                  return <option value={doc.type}>{doc.type}</option>;
                })}
              </select>
            </form>
          </div>
          <div className="flex m-2 mb-1">
            {results?.length === 0
              ? "No results"
              : results?.length +
                (results?.length === 1 ? " result" : " results")}
          </div>
          {loader && (
            <img
              src={LoadingImg}
              alt="loading-img"
              height={100}
              width={100}
              style={{ margin: "auto", display: "block", marginTop: "10%" }}
            ></img>
          )}
          {!loader && (
            <div className="flex flex-1 flex-col overflow-auto">
              {results?.map((result) => {
                return <ResultBox result={result} setPresent={setPresent} />;
              })}
            </div>
          )}
        </div>
        <div className="flex flex-col w-3/5 overflow-hidden">
          <div className="container-header flex flex-row p-4 h-18">
            <a
              href={present.url}
              target="_blank"
              rel="noreferrer"
              className="section-link"
            >
              Visit Section
            </a>
            <div className="section-type">
              {getHeading(present.url, present.type)}
            </div>
            <div
              className={
                present.accessibility === "public"
                  ? "accessibility-public"
                  : "accessibility-private"
              }
            >
              {present.accessibility}
            </div>
          </div>
          <div className="flex-1 flex flex-col p-0 overflow-auto">
            <h1 className="page-title">{present.document}</h1>
            <h3 className="section-heading">
              {present.heading}
              {isDrivePDF(present) && getPageSpan(present)}
            </h3>
            <p className="section-content">
              {getResultText(
                present.accessibility,
                present.text,
                present.type,
                true
              )}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

const ResultBox = ({ result, setPresent }) => {
  const showChange = (result) => {
    setPresent(result);
    // console.log(result);
  };
  console.log(result);
  return (
    <div className="result-box" onClick={() => showChange(result)}>
      <div className="result-heading">
        <h3 className="heading">{result.heading}</h3>

        <div className={`file-type-${result.type}`}>{result.type}</div>
        <div
          className={
            result.accessibility === "public"
              ? "accessibility-2-public"
              : "accessibility-2-private"
          }
        >
          {result.accessibility}
        </div>
      </div>
      <div className="result-page-title">{result.document}</div>
      <div className="result-page-url">{result.url}</div>
      <p className="paragraph">
        {getResultText(result.accessibility, result.text, result.type)}
      </p>
    </div>
  );
};

export default App;

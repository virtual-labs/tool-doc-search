import React from "react";
import { useState } from "react";
import {
  DOCUMENT_TYPES,
  DEFAULT_QUERY,
  DEFAULT_SECTION,
} from "../utils/config_data";
import { getResultText } from "../utils/utils";
import LoadingImg from "../media/loading-73.gif";

const SearchBox = ({ setPresent }) => {
  const [query, setQuery] = useState(DEFAULT_QUERY);
  const [results, setResults] = useState([]);
  const [loader, setLoading] = useState(false);

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
      // console.log(config);
      setLoading(true);
      setPresent(DEFAULT_SECTION);
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

  return (
    <>
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
            className="submit-button w-button"
            onClick={getResults}
          />
          <input
            type="text"
            className="page-title-filter"
            placeholder="Add page title filter...."
            value={query.page_title_filter}
            id="field"
            onChange={setQueryPageFilter}
          />
          <select
            id="select-doctype"
            className="select-doc-type"
            value={query.doc_filter}
            onChange={setQueryDocFilter}
          >
            {DOCUMENT_TYPES.map((doc, i) => {
              return (
                <option key={i} value={doc.type}>
                  {doc.type}
                </option>
              );
            })}
          </select>
        </form>
      </div>
      <div className="flex m-2 mb-1">
        {results?.length === 0
          ? "No results"
          : results?.length + (results?.length === 1 ? " result" : " results")}
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
          {results?.map((result, i) => {
            return (
              <ResultBox key={i} result={result} setPresent={setPresent} />
            );
          })}
        </div>
      )}
    </>
  );
};

const ResultBox = ({ result, setPresent }) => {
  const showResult = (result) => {
    setPresent(result);
  };
  return (
    <div className="result-box" onClick={() => showResult(result)}>
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
        {getResultText(
          result.url,
          result.accessibility,
          result.text,
          result.type
        )}
      </p>
    </div>
  );
};

export default SearchBox;

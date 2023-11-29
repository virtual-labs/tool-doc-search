import React from "react";
import {
  DOCUMENT_TYPES,
  DEFAULT_SECTION,
  SEARCH_API,
  ACCESSIBILITY_TYPES,
  SRC_TYPES,
} from "../../utils/config_data";

const QueryBox = ({
  setQuery,
  loader,
  query,
  setLoading,
  setPresent,
  setResults,
  highlight,
  setHighlight,
  results,
}) => {
  const getResults = async (e) => {
    e.preventDefault();
    if (loader) return;
    if (
      query.search_query.trim() === "" &&
      query.page_title_filter.trim() === ""
    ) {
      return;
    }

    const url = SEARCH_API;
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

  const setQuerySrcFilter = (e) => {
    setQuery({ ...query, src_filter: e.target.value });
  };

  const setQueryAccessibilityFilter = (e) => {
    setQuery({ ...query, acc_filter: e.target.value });
  };

  const setQueryPageFilter = (e) => {
    setQuery({ ...query, page_title_filter: e.target.value });
  };
  return (
    <>
      <div className="flex w-full pt-0">
        <form
          id="email-form"
          name="email-form"
          data-name="Email Form"
          method="get"
          className="form w-full flex flex-col"
        >
          <div className="flex flex-row w-full">
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
              className="submit-button w-button w-32"
              onClick={getResults}
            />
          </div>
          <div className="flex flex-row w-full">
            <input
              type="text"
              className="page-title-filter flex-1"
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
              title="Select document type"
            >
              {DOCUMENT_TYPES.map((doc, i) => {
                return (
                  <option key={i} value={doc.type}>
                    {doc.type}
                  </option>
                );
              })}
            </select>
            <select
              id="select-doctype"
              className="select-doc-type"
              value={query.src_filter}
              onChange={setQuerySrcFilter}
              title="Select source type"
            >
              {SRC_TYPES.map((doc, i) => {
                return (
                  <option key={i} value={doc.type}>
                    {doc.type}
                  </option>
                );
              })}
            </select>
            <select
              id="select-doctype"
              className="select-doc-type"
              value={query.acc_filter}
              onChange={setQueryAccessibilityFilter}
              title="Select accessibility type"
            >
              {ACCESSIBILITY_TYPES.map((doc, i) => {
                return (
                  <option key={i} value={doc.type}>
                    {doc.type}
                  </option>
                );
              })}
            </select>
          </div>
          <div className="flex flex-row pt-2">
            <input
              type="checkbox"
              checked={highlight}
              onChange={(e) => {
                setHighlight(!highlight);
              }}
            />
            <span
              className="ml-1 cursor-default"
              onClick={() => setHighlight(!highlight)}
            >
              Highlight search text
            </span>
          </div>
        </form>
      </div>
      <div className="flex m-2 mb-1">
        {results?.length === 0
          ? "No results"
          : results?.length + (results?.length === 1 ? " result" : " results")}
      </div>
    </>
  );
};

export default QueryBox;

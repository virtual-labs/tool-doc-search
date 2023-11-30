import React, { useRef } from "react";
import { useState } from "react";
import { DEFAULT_QUERY } from "../utils/config_data";
import { QueryBox, ResultPane } from "./search-box-component";

const SearchBox = ({ setPresent, highlight, setHighlight }) => {
  const [query, setQuery] = useState(DEFAULT_QUERY);
  const [results, setResults] = useState([]);
  const [loader, setLoading] = useState(false);
  const inpRef = useRef();

  return (
    <>
      <QueryBox
        setQuery={setQuery}
        loader={loader}
        query={query}
        setLoading={setLoading}
        setPresent={setPresent}
        setResults={setResults}
        highlight={highlight}
        setHighlight={setHighlight}
        results={results}
        inpRef={inpRef}
      />
      <ResultPane
        loader={loader}
        results={results}
        setPresent={setPresent}
        query={query}
        highlight={highlight}
      />
    </>
  );
};

export default SearchBox;

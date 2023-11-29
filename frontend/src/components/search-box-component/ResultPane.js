import React from "react";
import LoadingImg from "../../media/loading-73.gif";
import ResultBox from "./ResultBox";
import { getRankedResult } from "../../utils/utils";

const ResultPane = ({ loader, results, setPresent, query, highlight }) => {
  const rankedResult = getRankedResult(results, query.search_query);
  console.log(rankedResult);
  return (
    <>
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
          {rankedResult?.map((result, i) => {
            return (
              <ResultBox
                key={i}
                result={result}
                setPresent={setPresent}
                searchQuery={query.search_query}
                highlight={highlight}
              />
            );
          })}
        </div>
      )}
    </>
  );
};

export default ResultPane;

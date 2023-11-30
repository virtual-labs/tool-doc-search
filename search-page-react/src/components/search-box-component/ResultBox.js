import React from "react";
import { getResultText } from "../../utils/utils";
import HighlightedText from "../HighlightedText";

const ResultBox = ({ result, setPresent, searchQuery, highlight }) => {
  const showResult = (result) => {
    setPresent({ ...result, search_query: searchQuery });
  };

  const text = getResultText(
    result.url,
    result.accessibility,
    result.text,
    result.type
  );

  return (
    <div className="result-box" onClick={() => showResult(result)}>
      <div className="result-heading flex flex-row">
        <h3 className="heading flex-1">
          {
            <HighlightedText
              text={result.heading}
              searchQuery={highlight ? searchQuery : ""}
              markStyle={{ backgroundColor: "#ffcc00" }}
            />
          }
        </h3>
        <div className="flex flex-row result-box-tag-container">
          <div className={`file-type ${result.type}`}>{result.type}</div>
          <div className={`file-type ${result.src}`}>{result.src}</div>
          <div
            className={
              result.accessibility === "public"
                ? "accessibility-2 public"
                : "accessibility-2 private"
            }
          >
            {result.accessibility}
          </div>
        </div>
      </div>
      <div className="result-page-title">
        {
          <HighlightedText
            text={result.document}
            searchQuery={highlight ? searchQuery : ""}
            markStyle={{ backgroundColor: "#ffcc00" }}
          />
        }
      </div>
      <div className="result-page-url">{result.url}</div>
      <p className="paragraph">
        {
          <HighlightedText
            text={text}
            searchQuery={highlight ? searchQuery : ""}
            markStyle={{ backgroundColor: "#ffcc00", color: "#343434" }}
          />
        }
      </p>
    </div>
  );
};

export default ResultBox;

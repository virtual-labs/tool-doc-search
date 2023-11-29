import React from "react";

import GoogleSheetStyleTable from "../components/GoogleSheetStyleTable";
import { DOCUMENT_TYPES } from "./config_data";
import HighlightedText from "../components/HighlightedText";
import { stopWordsMap } from "./config_data";

const getResultText = (
  url,
  accessibility,
  text,
  type,
  present = false,
  searchQuery = "",
  highlight = true
) => {
  if (accessibility === "private") {
    return "This is a private document.";
  }
  if (type === "xlsx" && present) {
    let data = JSON.parse(text);
    return <GoogleSheetStyleTable data={data} url={url} />;
  } else if (type === "xlsx") {
    return "This is a Google Sheet.";
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
          {i > 0 && <span>&nbsp;&nbsp;&nbsp;&nbsp;</span>}{" "}
          {
            <HighlightedText
              text={part}
              searchQuery={highlight ? searchQuery : ""}
              markStyle={{ backgroundColor: "#ffcc00", color: "#343434" }}
            />
          }
        </React.Fragment>
      ))}
      {index !== lines.length - 1 && <br />}
    </React.Fragment>
  ));
  return textWithLineBreaks;
};

const getHeading = (url, type) => {
  if (url === "#") return "Document";
  for (let doc of DOCUMENT_TYPES) {
    if (doc.type === type) return doc.title;
  }
  return "Not Supported";
};

const getSubWords = (searchQuery) => {
  const searchWords = [];
  const tokens = searchQuery.split(" ");

  for (let i = 0; i < tokens.length; i++) {
    for (let j = i; j < tokens.length; j++) {
      const word = tokens.slice(i, j + 1).join(" ");
      if (!stopWordsMap.has(word))
        searchWords.push({ sentence: word, score: Math.pow(2, j - i + 1) });
    }
  }

  return searchWords;
};

function countSubstringOccurrences(text, substring) {
  const regex = new RegExp(substring, "gi");
  const matches = text.match(regex);
  return matches ? matches.length : 0;
}

const getRankedResult = (results, search_query) => {
  const searchWords = getSubWords(search_query);
  const rankedResults = [];
  for (let result of results) {
    const lowerCaseResult = result.text.toLowerCase();
    const lowerCaseHeading = result.heading.toLowerCase();

    let score = 0;
    for (let word of searchWords) {
      score +=
        word.score * countSubstringOccurrences(lowerCaseResult, word.sentence);
      score +=
        word.score * countSubstringOccurrences(lowerCaseHeading, word.sentence);
    }
    rankedResults.push({
      ...result,
      rank: score + result.score * 100,
      ascore: score,
    });
  }
  rankedResults.sort((a, b) => b.rank - a.rank);
  return rankedResults;
};

export { getResultText, getHeading, getRankedResult, getSubWords };

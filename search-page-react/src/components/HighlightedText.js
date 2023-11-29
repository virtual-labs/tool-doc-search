import React from "react";
import Highlighter from "react-highlight-words";
import { getSubWords } from "../utils/utils";

const HighlightedText = ({ text, searchQuery, markStyle }) => {
  const searchWords = getSubWords(searchQuery).map((obj) => obj.sentence);

  return (
    <Highlighter
      searchWords={searchWords}
      autoEscape={true}
      caseSensitive={false}
      textToHighlight={text}
      highlightStyle={markStyle || {}}
    />
  );
};

export default HighlightedText;

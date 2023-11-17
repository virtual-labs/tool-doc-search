import React from "react";

import GoogleSheetStyleTable from "../components/GoogleSheetStyleTable";
import { DOCUMENT_TYPES } from "./config_data";

const getResultText = (url, accessibility, text, type, present = false) => {
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
          {i > 0 && <span>&nbsp;&nbsp;&nbsp;&nbsp;</span>} {part}
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

export { getResultText, getHeading };

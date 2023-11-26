import React from "react";
import { getResultText, getHeading } from "../utils/utils";
import LinkIcon from "../media/link.png";

const ResultViewBox = ({ present }) => {
  const isDrivePDF = (doc) => {
    let slices = present.url.split("#");
    return (
      present.type === "pdf" && slices[slices.length - 1]?.startsWith("page=")
    );
  };

  const getPageSpan = (doc) => {
    let slices = doc.url.split("#");
    let page_comp = slices[slices.length - 1];
    let page_num = Number(page_comp.slice(5, page_comp.length));
    return <span className="drive-pdf-pagenum">Page {page_num}</span>;
  };

  return (
    <>
      <div className="container-header flex flex-row p-4 h-18">
        <div className="section-type">
          {getHeading(present.url, present.type)}
        </div>
      </div>
      <div className="flex-1 flex flex-col p-0 overflow-auto">
        <h1 className="page-title">
          <span
            className="view-box-link"
            onClick={() => {
              window.open(present.base_url, "_blank");
            }}
          >
            {present.document}
          </span>
          <span>
            <img className="h-8 w-4 p-0 ml-2 pb-4" src={LinkIcon} alt="link" />
          </span>
          <span className={`accessibility-view-box ${present.accessibility}`}>
            {present.accessibility}
          </span>
          <span className={`doctype-view-box ${present.type}`}>
            {present.type}
          </span>
        </h1>

        <h3 className="section-heading">
          <span
            className="view-box-link"
            onClick={() => {
              window.open(present.url, "_blank");
            }}
          >
            {present.heading}
          </span>
          <span>
            <img className="h-8 w-4 p-0 ml-2 pb-4" src={LinkIcon} alt="link" />
          </span>
          {isDrivePDF(present) && getPageSpan(present)}
        </h3>
        <div className="section-content">
          {getResultText(
            present.url,
            present.accessibility,
            present.text,
            present.type,
            true
          )}
        </div>
      </div>
    </>
  );
};

export default ResultViewBox;

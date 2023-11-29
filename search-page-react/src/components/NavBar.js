import React from "react";
import NavImg from "../media/download.png";
import { INSERT_DOC_URL } from "../utils/config_data";

const NavBar = () => {
  return (
    <>
      <div className="navbar-no-shadow-container w-nav">
        <div className="navbar-wrapper">
          <img src={NavImg} loading="lazy" width="80" af-el="nav-img" alt="" />
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
    </>
  );
};

export default NavBar;

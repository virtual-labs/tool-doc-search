import { useState } from "react";
import "./css/index.css";
import "./css/App.css";
import { DEFAULT_SECTION } from "./utils/config_data";
import { NavBar, SearchBox, ResultViewBox } from "./components";

function App() {
  const [present, setPresent] = useState(DEFAULT_SECTION);
  const [highlight, setHighlight] = useState(true);

  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden">
      <div className="flex">
        <NavBar />
      </div>
      <div className="flex flex-1 flex-row flex-block overflow-hidden">
        <div className="flex flex-col w-2/5 overflow-hidden">
          <SearchBox
            setPresent={setPresent}
            highlight={highlight}
            setHighlight={setHighlight}
          />
        </div>
        <div className="flex flex-col w-3/5 overflow-hidden">
          <ResultViewBox present={present} highlight={highlight} />
        </div>
      </div>
    </div>
  );
}

export default App;

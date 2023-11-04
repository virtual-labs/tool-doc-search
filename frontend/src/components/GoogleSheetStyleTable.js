import React from "react";
import "../css/index.css";
import "../css/App.css";

function parseData(data) {
  let cleanData = [];
  let n = data.length,
    m = data[0].length;
  for (let i = 0; i < n; i++) {
    let validRow = false;
    for (let j = 0; j < m; j++) {
      let cell = data[i][j].trim();
      validRow |= cell !== "";
    }
    if (validRow) cleanData.push(data[i]);
  }
  let finalData = [];
  let validCols = [];
  for (let i = 0; i < m; i++) {
    let validCol = false;
    for (let j = 0; j < n; j++) {
      let cell = data[j][i].trim();
      validCol |= cell !== "";
    }
    if (validCol) validCols.push(i);
  }
  for (let i = 0; i < n; i++) {
    finalData.push(
      validCols.map((validCol) => {
        return data[i][validCol];
      })
    );
  }
  return finalData;
}

const GoogleSheetStyleTable = ({ data }) => {
  const finalData = parseData(data);
  return (
    <table className="google-sheet-table">
      <tbody>
        {finalData.map((row, rowIndex) => (
          <tr key={rowIndex}>
            {row.map((cell, cellIndex) => (
              <td key={cellIndex}>
                <input type="text" value={cell} />
              </td>
            ))}
          </tr>
        ))}
      </tbody>
      <tfoot>
        <tr className="extend-table-row">
          <td className="extend-table-cell" colSpan="26">
            ...
          </td>
        </tr>
      </tfoot>
    </table>
  );
};

export default GoogleSheetStyleTable;

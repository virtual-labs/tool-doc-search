function generateResultTable(data) {
  let table = "<table>";
  table += "<tr><th>Document</th><th>Accessibility</th><th>Sections</th></tr>";

  for (const item of data) {
    table += `<tr>`;
    table += `<td><a href="${item.base_url}" target='_blank'>${item.page_title}</a></td>`;
    table += `<td>${item.accessibility}</td>`;
    table += `<td>${item.sections}</td>`;
    table += `</tr>`;
  }
  table += "</table>";
  return table;
}
document.getElementById("insert-button").addEventListener("click", function () {
  event.preventDefault();
  var selectedURLs = [];
  var divisionCount = parseInt(document.getElementById("division_count").value);
  let urlMap = {};
  for (var i = 0; i < divisionCount; i++) {
    var tagLabel = document.getElementById("tag_" + i);
    var urlVal = document.getElementById("doc-url-input_" + i);
    //
    var tagValue = tagLabel.innerHTML.trim();

    if (tagValue === "") {
      alert("URL cannot be empty for document " + (i + 1));
      return;
    } else if (tagValue === "unknown") {
      alert("unidentified URL type for document " + (i + 1));
      return;
    } else {
      if (urlMap.hasOwnProperty(urlVal.value.trim())) {
        alert("Duplicate URL found for document " + (i + 1));
        return;
      }
      urlMap[urlVal.value.trim()] = 1;
      selectedURLs.push({
        url: urlVal.value,
        type: tagValue,
      });
    }
  }

  document.getElementById("loader").style.visibility = "visible";
  if (selectedURLs.length > 0) {
    console.log(selectedURLs);
  } else {
    alert("No records selected.");
    return;
  }
  var postData = selectedURLs;
  document.getElementById("loader").style.visibility = "visible";
  fetch("/insert_doc/protected_area", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ action: "upsert", data: postData }),
  })
    .then((response) => response.json())
    .then((data) => {
      document.getElementById("loader").style.visibility = "hidden";

      var result = data;
      let resultPane = document.getElementById("result-pane-insert");
      // alert(result);
      resultPane.innerHTML = "";
      if (result.hasOwnProperty("error")) {
        resultPane.innerHTML += "<h3>Error occurred</h3>";
        resultPane.innerHTML += "<span class='result-attr'>Message</span>";
        resultPane.innerHTML += `<p class='result-msg'>${result.message}</p>`;
        resultPane.innerHTML += "<span class='result-attr'>Status Code</span>";
        resultPane.innerHTML += `<p class='result-msg'>${result.status_code}</p>`;
      } else {
        resultPane.innerHTML += "<h3>Success</h3>";
        resultPane.innerHTML += "<span class='result-attr'>Message</span>";
        resultPane.innerHTML += `<p class='result-msg'>${result.message}</p>`;
        resultPane.innerHTML += generateResultTable(result["result"]);
      }
    })
    .catch((error) => {
      alert("Error:", error);
    });
});

var modal = document.getElementById("id01");
window.onclick = function (event) {
  if (event.target == modal) {
    modal.style.display = "none";
  }
};

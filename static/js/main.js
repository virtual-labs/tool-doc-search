function generateTable(data) {
  let table = "<table>";
  table +=
    "<tr><th></th><th>Document</th><th>Accessibility</th><th>Inserted By</th><th>Type</th></tr>";

  for (const item of data) {
    table += `<tr>`;
    table += `<td><input type="checkbox" name="selected"></td>`;
    table += `<td><a href="${item.base_url}" target='_blank'>${item.page_title}</a></td>`;
    table += `<td><span class="accessibility-label ${item.accessibility}">${item.accessibility}</span></td>`;
    table += `<td>${item.inserted_by}</td>`;
    table += `<td><span class="doctype-label ${item.type}">${item.type}</span></td>`;
    table += `</tr>`;
  }

  table += "</table>";
  return table;
}

async function load_docs(text) {
  document.getElementById("loader").style.visibility = "visible";
  url = `/insert_doc/get_docs?search_query=${text}`;
  console.log(url);
  const response = await fetch(url);

  if (!response.ok) {
    const message = `An error has occured: ${response.status}`;
    throw new Error(message);
  }

  const data = await response.json();
  console.log(data);
  let num = data.length;
  let resultPane = document.getElementById("result-pane");
  resultPane.innerHTML = `<span>${num} ${
    num == 1 ? "document" : "documents"
  }<span>`;
  resultPane.innerHTML += generateTable(data);
  document.getElementById("loader").style.visibility = "hidden";
}
load_docs("");
document.getElementById("postButton").addEventListener("click", function () {
  var selectedURLs = [];

  var checkboxes = document.querySelectorAll('input[type="checkbox"]');

  checkboxes.forEach(function (checkbox, index) {
    if (checkbox.checked) {
      var row = checkbox.closest("tr");
      var documentCell = row.cells[1];
      var typeCell = row.cells[4];
      var documentURL = documentCell.querySelector("a").getAttribute("href");
      var documentType = typeCell.textContent;
      selectedURLs.push({ url: documentURL, type: documentType });
    }
  });
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
      alert("Documents updated successfully.");
    })
    .catch((error) => {
      alert("Error:", error);
    });
});

var form = document.getElementById("myForm");

form.addEventListener("submit", function (event) {
  event.preventDefault();

  var text = document.getElementById("search_query").value;
  text = text.trim();
  if (text === "") {
    alert("Please fill out all fields.");
  } else {
    load_docs(text);
  }
});

document.getElementById("reload").addEventListener("click", function (event) {
  event.preventDefault();
  load_docs("");
});

document
  .getElementById("modal-button")
  .addEventListener("click", function (event) {
    event.preventDefault();
    document.getElementById("id01").style.display = "block";
  });

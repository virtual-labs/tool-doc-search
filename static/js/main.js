function generateTable(data) {
  let table = "<table>";
  table +=
    "<tr><th><button style='padding:0; margin:0;background-color:rgba(0,0,0,0); width:100%' id='clearSelection'><img src='/static/img/clear.png' alt='img' style='height:20px; width:20px; margin:0; '/></button></th><th>Document</th><th>Accessibility</th><th>Inserted By</th><th>Type</th></tr>";

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

let page_object = {
  search_query: "",
  page: 1,
};

async function load_docs(text, page) {
  document.getElementById("loader").style.visibility = "visible";
  url = `/insert_doc/get_docs?search_query=${text}&page=${page}`;
  console.log(url);
  const response = await fetch(url);

  if (!response.ok) {
    const message = `An error has occured: ${response.status}`;
    document.getElementById("loader").style.visibility = "hidden";
    throw new Error(message);
  }

  const data = await response.json();
  console.log(data);
  let num = data.length;
  let pageText = document.getElementById("page-text");
  if (num === 0 && page > 1) {
    alert("No next page.");
    if (page_object.page > 1) page_object.page -= 1;
    document.getElementById("loader").style.visibility = "hidden";
    pageText.innerText = `Page ${page_object.page}`;
    console.log(`Page ${page_object.page}`);
    return;
  }
  pageText.innerText = `Page ${page_object.page}`;
  console.log(`Page ${page_object.page}`);
  let resultPane = document.getElementById("result-pane");
  resultPane.innerHTML = `<span>${num} ${
    num == 1 ? "document" : "documents"
  }<span>`;
  resultPane.innerHTML += generateTable(data);
  document
    .getElementById("clearSelection")
    .addEventListener("click", function () {
      var checkboxes = document.querySelectorAll('input[type="checkbox"]');

      checkboxes.forEach(function (checkbox, index) {
        checkbox.checked = false;
      });
    });
  document.getElementById("loader").style.visibility = "hidden";
}
load_docs(page_object.search_query, page_object.page);

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
      alert("Documents updated successfully.");
    })
    .catch((error) => {
      alert("Error:", error);
    })
    .finally(() => {
      document.getElementById("loader").style.visibility = "hidden";
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
    if (page_object.search_query !== text) {
      page_object.search_query = text;
      page_object.page = 1;
    }
    load_docs(page_object.search_query, page_object.page);
  }
});

document.getElementById("reload").addEventListener("click", function (event) {
  event.preventDefault();
  page_object.page = 1;
  page_object.search_query = "";
  load_docs(page_object.search_query, page_object.page);
});

document
  .getElementById("modal-button")
  .addEventListener("click", function (event) {
    event.preventDefault();
    document.getElementById("id01").style.display = "block";
  });

document.getElementById("deleteButton").addEventListener("click", function () {
  let text = "Are you sure to delete selected document(s)?";

  var selectedURLs = [];

  var checkboxes = document.querySelectorAll('input[type="checkbox"]');

  checkboxes.forEach(function (checkbox, index) {
    if (checkbox.checked) {
      var row = checkbox.closest("tr");
      var documentCell = row.cells[1];
      var documentURL = documentCell.querySelector("a").getAttribute("href");
      selectedURLs.push(documentURL);
    }
  });

  if (selectedURLs.length > 0) {
    console.log(selectedURLs);
  } else {
    alert("No records selected.");
    return;
  }
  if (confirm(text) == false) {
    return;
  }
  var postData = selectedURLs;
  document.getElementById("loader").style.visibility = "visible";
  fetch("/insert_doc/protected_area", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ action: "delete", data: postData }),
  })
    .then((response) => response.json())
    .then((data) => {
      console.log(data);
      load_docs(page_object.search_query, 1);
    })
    .catch((error) => {
      console.log(error);
      alert("Error:", error);
    })
    .finally(() => {
      document.getElementById("loader").style.visibility = "hidden";
    });
});

document.getElementById("prev-button").addEventListener("click", function () {
  if (page_object.page > 1) {
    page_object.page -= 1;
    load_docs(page_object.search_query, page_object.page);
  } else {
    alert("No previous page.");
  }
});

document.getElementById("next-button").addEventListener("click", function () {
  page_object.page += 1;
  load_docs(page_object.search_query, page_object.page);
});

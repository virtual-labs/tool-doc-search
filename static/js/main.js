let total_recs = 0;

function generateTable(data) {
  let table = "<table>";
  table +=
    "<tr><th><input type='checkbox' name='selected' id='clearSelection'></th><th>Document</th><th>Type</th><th>Accessibility</th><th>Last updated</th><th>Updated By</th></tr>";

  for (const item of data) {
    table += `<tr>`;
    table += `<td><input type="checkbox" name="selected"></td>`;
    table += `<td><a href="${item.base_url}" target='_blank'>${item.page_title}</a></td>`;
    table += `<td><span class="doctype-label ${item.type}">${item.type}</span></td>`;
    table += `<td><span class="accessibility-label ${item.accessibility}">${item.accessibility}</span></td>`;
    table += `<td>${new Date(item.last_updated)
      .toString()
      .replace("GMT+0530 (India Standard Time)", "(IST)")}</td>`;
    table += `<td>${item.updated_by}</td>`;
    table += `</tr>`;
  }

  table += "</table>";
  return table;
}

let page_object = {
  search_query: "",
  page: 1,
  page_limit: 0,
};

async function load_docs(text, page) {
  try {
    document.getElementById("loader").style.visibility = "visible";
    url = `/insert_doc/get_docs?search_query=${text}&page=${page}`;
    console.log(url);
    const response = await fetch(url);

    if (!response.ok) {
      const message = `An error has occured: ${response.status}`;
      document.getElementById("loader").style.visibility = "hidden";
      throw new Error(message);
    }

    let data = await response.json();
    if (page == 1) {
      page_object.page_limit = Math.ceil(data.count / data.page_size);
    }
    if (data.count) total_recs = data.count;

    const nextButton = document.getElementById("next-button");
    const prevButton = document.getElementById("prev-button");

    if (page_object.page == page_object.page_limit) {
      nextButton.disabled = true;
    } else {
      nextButton.disabled = false;
    }
    if (page_object.page == 1) {
      prevButton.disabled = true;
    } else {
      prevButton.disabled = false;
    }

    data = data.search_results;
    console.log(data);
    let num = data.length;
    let pageText = document.getElementById("page-text");
    if (num === 0 && page > 1) {
      alert("No next page.");
      if (page_object.page > 1) page_object.page -= 1;
      document.getElementById("loader").style.visibility = "hidden";
      pageText.innerText = `Page ${page_object.page} of ${page_object.page_limit}`;
      console.log(`Page ${page_object.page}`);
      return;
    }

    pageText.innerText = `Page ${page_object.page} of ${page_object.page_limit}`;
    console.log(`Page ${page_object.page}`);
    let resultPane = document.getElementById("result-pane");
    resultPane.innerHTML = `<span>${num} ${
      num == 1 ? "document" : "documents"
    }<span>
    <span style='float:right'>${total_recs} documents</span>
      `;

    resultPane.innerHTML += generateTable(data);
    document
      .getElementById("clearSelection")
      .addEventListener("click", function (evt) {
        var checkboxes = document.querySelectorAll('input[type="checkbox"]');

        checkboxes.forEach(function (checkbox, index) {
          if (evt.target.checked) {
            checkbox.checked = true;
          } else {
            checkbox.checked = false;
          }
        });
      });
  } catch (err) {
    console.log(err);
    alert("Error:", err);
  } finally {
    document.getElementById("loader").style.visibility = "hidden";
  }
}
load_docs(page_object.search_query, page_object.page);

document.getElementById("postButton").addEventListener("click", function () {
  var selectedURLs = [];

  var checkboxes = document.querySelectorAll('input[type="checkbox"]');

  checkboxes.forEach(function (checkbox, index) {
    if (checkbox.checked) {
      var row = checkbox.closest("tr");
      var documentCell = row.cells[1];
      if (documentCell.querySelector("a") === null) return;
      var typeCell = row.cells[2];
      var documentURL = documentCell.querySelector("a").getAttribute("href");
      var documentType = typeCell.textContent;
      let pt_valid =
        !documentTypeIdentifiers[documentType] ||
        documentTypeIdentifiers[documentType].page_title_req;
      // alert(pt_valid);
      selectedURLs.push({
        url: documentURL,
        type: documentType,
        page_title: pt_valid ? documentCell.querySelector("a").text : "",
      });
      // alert(
      //   JSON.stringify({
      //     url: documentURL,
      //     type: documentType,
      //     page_title: pt_valid ? documentCell.querySelector("a").text : "",
      //   })
      // );
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
    body: JSON.stringify({ action: "update", data: postData }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data["error"]) {
        alert(data["error"] + " " + data["message"]);
      } else alert("Documents updated successfully.");
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
      if (documentCell.querySelector("a") === null) return;
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
      load_docs(page_object.search_query, page_object.page);
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

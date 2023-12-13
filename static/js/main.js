let total_recs = 0;

let page_object = {
  search_query: "",
  page: 1,
  page_limit: 0,
};

function generateMainTable(data) {
  let table = "<table>";
  table +=
    "<tr><th><input type='checkbox' name='selected' id='clearSelection'></th><th>Document</th><th></th><th>Type</th><th>Accessibility</th><th>Last updated</th><th>Updated By</th></tr>";

  for (const item of data) {
    let dir = item.dir === 0 ? "file" : "dir";
    table += `<tr>`;
    table += `<td><input type="checkbox" name="selected"></td>`;
    table += `<td><a href="${item.base_url}" target='_blank'>${item.page_title}</a></td>`;
    table += `<td><span class="doctype-label ${dir}">${dir}</span></td>`;
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
      num == 1 ? "document" : "entries"
    }<span>
    <span style='float:right'>${total_recs} entries</span>
      `;

    resultPane.innerHTML += generateMainTable(data);

    document
      .getElementById("clearSelection")
      .addEventListener("click", function (evt) {
        let checkboxes = document.querySelectorAll('input[type="checkbox"]');

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
    alert("Error: " + err);
  } finally {
    document.getElementById("loader").style.visibility = "hidden";
  }
}

document.getElementById("updateButton").addEventListener("click", function () {
  let selectedURLs = [];

  let checkboxes = document.querySelectorAll('input[type="checkbox"]');

  checkboxes.forEach(function (checkbox, index) {
    if (checkbox.checked) {
      let row = checkbox.closest("tr");
      let documentCell = row.cells[1];
      if (documentCell.querySelector("a") === null) return;
      let typeCell = row.cells[3];
      let documentURL = documentCell.querySelector("a").getAttribute("href");
      let documentType = typeCell.textContent;
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
  let isDirSelected = 0;
  if (selectedURLs.length > 0) {
    console.log(selectedURLs);
    let dirMap = new Map();
    selectedURLs.forEach(function (item, index) {
      if (item.type === "dir") {
        if (!dirMap.get("dir", -1)) dirMap["dir"] = 1;
        else dirMap["dir"] += 1;
      } else {
        if (!dirMap.get("file", -1)) dirMap["file"] = 1;
        else dirMap["file"] += 1;
      }
    });
    if (dirMap["dir"] > 0 && dirMap["file"] > 0) {
      alert("Please select either files or directories at a time.");
      return;
    } else if (dirMap["dir"] > 1) {
      alert(`Please select only one directory at a time.`);
      return;
    } else if (dirMap["dir"] === 1) {
      isDirSelected = 1;
    }
  } else {
    alert("No records selected.");
    return;
  }
  let postData = isDirSelected
    ? [{ folderURL: selectedURLs[0].url }]
    : selectedURLs;
  let body = {
    action: isDirSelected ? "folder-update" : "update",
    data: postData,
  };
  // alert(JSON.stringify(body));
  // return;
  document.getElementById("loader").style.visibility = "visible";
  fetch("/insert_doc/protected_area", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  })
    .then((response) => response.json())
    .then((data) => {
      console.log(data);
      document.getElementById("id03").style.display = "block";
      let resultPane = document.getElementById("result-pane-update");
      showResult(resultPane, data);
      // if (data["error"]) {
      //   alert(data["error"] + " " + data["message"]);
      // } else alert("Documents updated successfully.");
    })
    .catch((error) => {
      alert("Error: " + error);
    })
    .finally(() => {
      document.getElementById("loader").style.visibility = "hidden";
    });
});

let form = document.getElementById("myForm");

form.addEventListener("submit", function (event) {
  event.preventDefault();

  let text = document.getElementById("search_query").value;
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

document.getElementById("deleteButton").addEventListener("click", function () {
  let text = "Are you sure to remove selected document(s)?";

  let selectedURLs = [];
  let urlTypes = [];

  let checkboxes = document.querySelectorAll('input[type="checkbox"]');

  checkboxes.forEach(function (checkbox, index) {
    if (checkbox.checked) {
      let row = checkbox.closest("tr");
      if (!row) return;
      let documentCell = row.cells[1];
      let typeCell = row.cells[2];
      if (documentCell.querySelector("a") === null) return;
      let documentURL = documentCell.querySelector("a").getAttribute("href");
      selectedURLs.push(documentURL);
      let documentType = typeCell.textContent;
      urlTypes.push(documentType);
    }
  });

  let isDirSelected = 0;
  if (selectedURLs.length > 0) {
    console.log(selectedURLs);
    let dirMap = new Map();
    selectedURLs.forEach(function (item, index) {
      if (urlTypes[index] === "dir") {
        if (!dirMap.get("dir", -1)) dirMap["dir"] = 1;
        else dirMap["dir"] += 1;
      } else {
        if (!dirMap.get("file", -1)) dirMap["file"] = 1;
        else dirMap["file"] += 1;
      }
    });
    if (dirMap["dir"] > 0 && dirMap["file"] > 0) {
      alert("Please select either files or directories at a time.");
      return;
    } else if (dirMap["dir"] > 1) {
      alert(`Please select only one directory at a time.`);
      return;
    } else if (dirMap["dir"] === 1) {
      isDirSelected = 1;
    }
  } else {
    alert("No records selected.");
    return;
  }

  if (confirm(text) == false) {
    return;
  }
  // alert(JSON.stringify(selectedURLs));
  // alert(JSON.stringify(urlTypes));
  // alert(isDirSelected);
  // return;

  if (isDirSelected) {
    let dirMessage =
      "You have selected a directory. All files present inside it at the time of insertion will be removed. Are you sure?";
    if (confirm(dirMessage) == false) {
      return;
    }
  }
  let postData = isDirSelected ? [selectedURLs[0]] : selectedURLs;
  let body = {
    action: isDirSelected ? "folder-delete" : "delete",
    data: postData,
  };

  // return;
  document.getElementById("loader").style.visibility = "visible";
  fetch("/insert_doc/protected_area", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  })
    .then((response) => response.json())
    .then((data) => {
      console.log(data);
      load_docs(page_object.search_query, page_object.page);
    })
    .catch((error) => {
      console.log(error);
      alert("Error: " + error);
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

document
  .getElementById("modal-button")
  .addEventListener("click", function (event) {
    event.preventDefault();
    document.getElementById("id01").style.display = "block";
  });

document
  .getElementById("drive-folder-button")
  .addEventListener("click", function (event) {
    event.preventDefault();
    document.getElementById("id02").style.display = "block";
  });

load_docs(page_object.search_query, page_object.page);

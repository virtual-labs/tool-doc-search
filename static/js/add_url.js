function generate_url_div(i) {
  var division = document.createElement("div");
  division.className = "division";

  var indexLabel = document.createElement("span");
  indexLabel.textContent = `${i + 1}`;
  indexLabel.className = `index-label`;

  var urlInput = document.createElement("input");
  urlInput.type = "text";
  urlInput.name = "url_" + i;
  urlInput.placeholder = "Enter URL";
  urlInput.className = "url-input";
  urlInput.id = "doc-url-input_" + i;

  var tagLabel = document.createElement("span");
  tagLabel.textContent = "";
  tagLabel.className = `doctype-label`;
  tagLabel.id = "tag_" + i;

  var hiddenLabel = document.createElement("input");
  hiddenLabel.type = "hidden";
  hiddenLabel.value = "";
  hiddenLabel.name = "hidden_" + i;

  urlInput.addEventListener("keyup", function (evt) {
    let url = evt.target.value;
    let doc_type = identifyDocumentType(url);
    hiddenLabel.value = `${doc_type}`;
    tagLabel.textContent = `${doc_type}`;
    tagLabel.className = `doctype-label ${doc_type}`;
    if (url.length && !division.querySelector(".page-title-input")) {
      var pageTitleInput = document.createElement("input");
      pageTitleInput.type = "text";
      pageTitleInput.id = "page-title_" + i;
      pageTitleInput.placeholder = "(Optional) Page title";
      pageTitleInput.className = "page-title-input";
      division.insertBefore(pageTitleInput, urlInput.nextSibling);
    }
  });
  division.appendChild(indexLabel);
  division.appendChild(urlInput);
  division.appendChild(tagLabel);
  division.appendChild(hiddenLabel);
  return division;
}

document.getElementById("divisionContainer").append(generate_url_div(0));

document
  .getElementById("division_count")
  .addEventListener("change", function () {
    var divisionCount = parseInt(
      document.getElementById("division_count").value
    );
    var divisionContainer = document.getElementById("divisionContainer");
    divisionContainer.innerHTML = "";
    for (var i = 0; i < divisionCount; i++) {
      divisionContainer.appendChild(generate_url_div(i));
    }
  });

function validate_gdoc(url) {
  let pref = "https://docs.google.com/document/d/";
  url = url.trim();
  return url.startsWith(pref) && url.length > pref.length;
}

// https://github.com/virtual-labs/app-exp-create-web/blob/master/docs/developer-doc.md
function validate_md(url) {
  let pref = "https://github.com/";
  url = url.trim();
  let tokens = url.slice(8).split("/");
  return url.startsWith(pref) && tokens[3] === "blob" && url.endsWith(".md");
}

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
  urlInput.id = "doc-url-input_" + i;
  //   urlInput.required = true;
  // <input type="hidden" id="custId" name="custId" value="3487">
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
    if (validate_gdoc(url)) {
      hiddenLabel.value = "gdoc";
      tagLabel.textContent = "gdoc";
      tagLabel.className = `doctype-label gdoc`;
    } else if (validate_md(url)) {
      hiddenLabel.value = "md";
      tagLabel.textContent = "md";
      tagLabel.className = `doctype-label md`;
    } else {
      hiddenLabel.value = "unknown";
      tagLabel.textContent = "unknown";
      tagLabel.className = `doctype-label`;
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

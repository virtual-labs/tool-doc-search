function validateGitHubURL(url) {
  let tokens = url
    .slice(8)
    .split("/")
    .filter((x) => x !== "");
  return (
    url.startsWith("https://github.com/") &&
    tokens[3] === "blob" &&
    tokens[tokens.length - 1].endsWith(".md")
  );
}

function validateGDocURL(url) {
  let tokens = url.slice(8).split("/");
  return (
    url.startsWith("https://docs.google.com/document/d/") &&
    tokens[tokens.length - 1].trim() !== ""
  );
}

function getDivisionElement(i) {
  let division = document.createElement("div");
  division.className = `division`;
  let urlInput = document.createElement("input");
  urlInput.type = "text";
  urlInput.name = "url_" + i;
  urlInput.placeholder = "Enter URL";
  let tagLabel = document.createElement("span");
  tagLabel.textContent = "";
  let indexLabel = document.createElement("span");
  indexLabel.textContent = `${i + 1}`;
  urlInput.addEventListener("keyup", function (evt) {
    let value = evt.target.value;
    if (validateGDocURL(value)) {
      tagLabel.textContent = "gdoc";
    } else if (validateGitHubURL(value)) {
      tagLabel.textContent = "md";
    } else {
      tagLabel.textContent = "unknown";
    }
  });
  division.appendChild(indexLabel);
  division.appendChild(urlInput);
  division.appendChild(tagLabel);
  return division;
}

document.getElementById("divisionContainer").append(getDivisionElement(0));

document
  .getElementById("division_count")
  .addEventListener("change", function (evt) {
    evt.preventDefault();
    let divisionCount = parseInt(
      document.getElementById("division_count").value
    );
    let divisionContainer = document.getElementById("divisionContainer");
    divisionContainer.innerHTML = "";
    for (let i = 0; i < divisionCount; i++) {
      divisionContainer.appendChild(getDivisionElement(i));
    }
  });

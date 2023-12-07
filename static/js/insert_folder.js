document
  .getElementById("insert-folder-button")
  .addEventListener("click", function (event) {
    event.preventDefault();
    let folderURL = document.getElementById("folder-url-input").value;
    folderURL = folderURL.trim();

    if (folderURL === "") {
      alert("Please specify folder URL");
      return;
    }

    document.getElementById("loader").style.visibility = "visible";

    var postData = [folderURL];

    document.getElementById("loader").style.visibility = "visible";

    fetch("/insert_doc/protected_area", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ action: "folder-insert", data: postData }),
    })
      .then((response) => response.json())
      .then((data) => {
        console.log(data);
        const result = data;
        let resultPane = document.getElementById("result-pane-folder-insert");
        showResult(resultPane, result);
      })
      .catch((error) => {
        console.error(error);
        alert("Error:", error);
      })
      .finally(() => {
        document.getElementById("loader").style.visibility = "hidden";
      });
  });

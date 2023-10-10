function deleteCookies() {
  var allCookies = document.cookie.split(";");
  for (var i = 0; i < allCookies.length; i++)
    document.cookie = allCookies[i] + "=;expires=" + new Date(0).toUTCString();
}

function logout() {
  deleteCookies();
  window.location.href = "/insert_doc/logout";
}

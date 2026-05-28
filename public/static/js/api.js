export function getCookie(name) {
  const matches = document.cookie.match(new RegExp(
    "(?:^|; )" + name.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, '\\$1') + "=([^;]*)"
  ));
  return matches ? decodeURIComponent(matches[1]) : undefined;
}

export function isAuthenticated() {
  return document.body?.dataset?.userAuth === "1";
}

export function loginUrl() {
  return document.body?.dataset?.loginUrl ?? "/login/";
}

export async function postJSON(url, data) {
  try {
    const resp = await fetch(url, {
      method: "POST",
      credentials: "same-origin",
      headers: {
        "X-CSRFToken": getCookie("csrftoken"),
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        Accept: "application/json",
      },
      body: new URLSearchParams(data),
    });
    const json = await resp.json();
    return { status: resp.status, body: json };
  } catch (err) {
    return {
      status: 500,
      body: { ok: false, error: "Invalid server response" },
    };
  }
}

export function handleAuthRedirect() {
  const next = encodeURIComponent(
    window.location.pathname + window.location.search,
  );
  window.location.href = loginUrl() + "?next=" + next;
}

export function showError(message) {
  alert(message || "Something went wrong");
}

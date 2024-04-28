const postInput = document.getElementById("postInput");
// const postBtn = document.getElementById("post-btn");

postInput.addEventListener("input", () => {
  postInput.style.height = "230px"; // Reset height to shrink if content is deleted
  postInput.style.height = `${postInput.scrollHeight}px`; // Set height to fit content
});

// copy to clipboard
function copyText() {
  var copyText = document.getElementById("postInput").value;

  navigator.clipboard
    .writeText(copyText)
    .then(() => {
      showToast("Copied");
    })
    .catch((error) => console.error("Could not copy text: ", error));
}

function showToast(message) {
  var toast = document.createElement("div");
  toast.className = "toast";
  toast.textContent = message;
  toast.style.backgroundColor = "#ea0707"; // Set the background color of the toast
  toast.style.color = "#ffffff"; // Set the text color of the toast
  document.body.appendChild(toast);

  setTimeout(() => {
    toast.classList.add("show");
  }, 100);

  setTimeout(() => {
    toast.classList.remove("show");
    setTimeout(() => {
      document.body.removeChild(toast);
    }, 500);
  }, 2000);
}

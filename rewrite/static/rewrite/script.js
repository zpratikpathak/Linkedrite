function adjustHeight() {
  const postInput = document.getElementById("postInput");
  postInput.style.height = "230px"; // Reset height to shrink if content is deleted
  postInput.style.height = `${postInput.scrollHeight}px`; // Set height to fit content
}

postInput.addEventListener("input", adjustHeight);

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
  toast.style.padding = "10px"; // Add padding for better text distribution
  toast.style.textAlign = "center"; // Center the text
  toast.style.width = "fit-content"; // Adjust width to fit content
  toast.style.margin = "0 auto"; // Center the toast horizontally
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

const emojiCheckbox = document.getElementById("emojiNeeded");
emojiCheckbox.addEventListener("change", function () {
  if (this.checked) {
    showToast("Emojis will now be included in your posts!");
  } else {
    showToast("Emojis will be excluded from your posts.");
  }
});

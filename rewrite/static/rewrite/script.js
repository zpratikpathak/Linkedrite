const postInput = document.getElementById("postInput");
// const postBtn = document.getElementById("post-btn");

postInput.addEventListener("input", () => {
  postInput.style.height = "230px"; // Reset height to shrink if content is deleted
  postInput.style.height = `${postInput.scrollHeight}px`; // Set height to fit content
});

// copy to clipboard
function copyText() {
  var copyText = document.getElementById("postInput");
  copyText.select();
  copyText.setSelectionRange(0, 99999); // For mobile devices

  document.execCommand("copy");
  // alert("Copied the text: " + copyText.value);
}

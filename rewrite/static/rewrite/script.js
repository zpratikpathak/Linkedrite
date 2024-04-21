const postInput = document.getElementById("post-input");
const postBtn = document.getElementById("post-btn");

postInput.addEventListener("input", () => {
  postBtn.disabled = !postInput.value.trim();
});

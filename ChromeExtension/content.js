// Function to add red buttons for AI post rewriting
function addRedButtons(shareBoxElement) {
  const listItem = shareBoxElement.querySelector(
    ".artdeco-carousel__slider.ember-view"
  );
  const parentDiv = shareBoxElement.querySelector(".artdeco-carousel__content");

  // Check if buttons are already added
  if (listItem) {
    var existingButtons = listItem.querySelectorAll(".toolbar");

    if (!existingButtons || existingButtons.length < 1) {
      let toast = document.getElementById("toast");
      if (!toast) {
        const toastDiv = document.createElement("div");
        toastDiv.id = "toast";
        toastDiv.className = "toast";
        parentDiv.appendChild(toastDiv);
      }

      // Create new buttons
      const div = document.createElement("div");
      div.className = "toolbar";
      div.innerHTML = `
        <div class="toggle-group">
          <input type="checkbox" id="emoji-toggle" class="toggle-input" style="margin:0px !important">
          <label for="emoji-toggle" class="button toggle-label" style="margin:0px !important">
            <span class="toggle-switch"></span>
            Emojis😀
          </label>
          <input type="checkbox" id="htag-toggle" class="toggle-input" style="margin:0px !important">
          <label for="htag-toggle" class="button toggle-label" style="margin:0px !important">
            <span class="toggle-switch"></span>
            HashTag🔖
          </label>
        </div>
        <button id="postButton" class="button red-button" style="margin-left:5px !important">Rewrite with AI✨</button>
        <div id="loading" style="display: none;">
          <div class="loader-3"><span></span></div>
        </div>
        <div id="failed" style="display: none;">
          <img src="data:image/png;base64" alt="reload" style="height:28px;width:28px;padding:5px 0px 0px 5px;">
        </div>
      `;

      // Append buttons to the list item
      listItem.appendChild(div);

      // Add event listener for the "Rewrite with AI" button
      let postButton = document.getElementById("postButton");
      postButton.addEventListener("click", initiatePostData);
    }
  }
}

// Function to initiate the process of posting data to the server for rewriting
function initiatePostData() {
  var textContent = document.querySelector(".ql-editor").textContent;
  if (textContent != "") {
    // Disable the button to prevent multiple clicks
    document.getElementById("postButton").disabled = true;
    document.getElementById("postButton").style.backgroundColor = "#bdbebf";

    // Show loading animation
    document.getElementById("loading").style.display = "block";

    // Get toggle values for emojis and hashtags
    var emojiToggle = document.getElementById("emoji-toggle").checked;
    var htagToggle = document.getElementById("htag-toggle").checked;

    // Make POST request to the server
    fetchPostData(textContent, emojiToggle, htagToggle);
  } else {
    showToast("Write something to generate with AI");
  }
}

// Function to send POST request to the server for rewriting the content
function fetchPostData(textContent, emojiToggle, htagToggle) {
  fetch("http://127.0.0.1:8000/rewrite/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      postInput: textContent,
      emojiNeeded: emojiToggle,
      htagNeeded: htagToggle,
    }),
  })
    .then(handleResponse)
    .then((data) => {
      const responseAI = data.rewriteAI;
      const editor = document.querySelector(".ql-editor");
      editor.textContent = ""; // Clear the .ql-editor content
      let i = 0;
      const typingEffect = setInterval(() => {
        editor.textContent += responseAI.charAt(i);
        i++;
        if (i > responseAI.length) {
          clearInterval(typingEffect);
          // Re-enable the button
          document.getElementById("postButton").disabled = false;
          document.getElementById("postButton").style.backgroundColor =
            "#ff4d4d";
          document.getElementById("loading").style.display = "none";
        }
      }, 5);
    })
    .catch(handleError);
}

// Function to handle response from the server
function handleResponse(response) {
  if (!response.ok) {
    showToast("Bad Request");
    return { rewriteAI: "" };
  }
  return response.json();
}

// Function to handle errors during the POST request
function handleError(error) {
  // Update button style and show error toast
  document.getElementById("postButton").style.backgroundColor = "#ff4d4d";
  showToast("An Error Occurred");

  // Re-enable the button and hide loading animation
  document.getElementById("postButton").disabled = false;
  document.getElementById("loading").style.display = "none";
}

// Function to display toast message
function showToast(message) {
  var toast = document.getElementById("toast");
  toast.textContent = message;
  toast.style.display = "block";

  // Hide the toast after a certain duration (e.g., 3 seconds)
  setTimeout(function () {
    toast.style.display = "none";
  }, 3000); // Adjust the duration as needed
}

// Mutation observer for the target node
const targetNode = document.getElementById("artdeco-modal-outlet");
let observer;
let observer1;

// Function to observe mutations in the target node
function observeMutations() {
  observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
      const modalOutlet = targetNode;

      if (modalOutlet) {
        const shareBoxElement = modalOutlet.querySelector(".share-box");

        if (shareBoxElement) {
          if (observer1) {
            observer1.disconnect();
            observer1 = null;
          }
          observer1 = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
              addRedButtons(shareBoxElement);
            });
          });
          observer1.observe(shareBoxElement, { childList: true });

          addRedButtons(shareBoxElement);
        }
      }
    });
  });

  // Start observing mutations in the target node
  observer.observe(targetNode, { childList: true });
}

// Start observing mutations
observeMutations();

// Event listener for beforeunload event to disconnect observers
window.addEventListener("beforeunload", function (e) {
  disconnectObservers();
});

// Function to disconnect the observers
function disconnectObservers() {
  if (observer) {
    observer.disconnect();
    observer = null;
  }
  if (observer1) {
    observer1.disconnect();
    observer1 = null;
  }
}

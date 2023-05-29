var button = document.getElementById("submit");

    // Add a click event listener to the button
    button.addEventListener("click", function() {
      // Get the message element
      var message = document.getElementById("message");
      
      // Set the message text
      message.textContent = "Successfully register";
    });
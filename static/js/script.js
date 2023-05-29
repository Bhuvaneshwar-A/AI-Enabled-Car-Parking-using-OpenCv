const form = document.querySelector('form-group');
form.addEventListener('submit', handleFormSubmit);

function handleFormSubmit(event) {
  event.preventDefault();
  // Perform login validation or submit form data
  // You can add your own logic here
  console.log('Form submitted');
}

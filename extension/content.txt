// An alert to let the broswer know it could take a bit
alert("Reading reviews (and drinking coffee), this may take a moment.");

// This function converts unicode to characters
function unicodeToChar(text) {
	return text.replace(/\\u[\dA-F]{4}/gi, 
	      function (match) {
	           return String.fromCharCode(parseInt(match.replace(/\\u/g, ''), 16));
	      });
}

// Grab the text I want to process
var textToSend = document.body.innerText;

// This is the url to my python file
const api_url = 'MY_GOOGLE_CLOUD_FUNCTION_URL';

// Fetch calls the fucntion
fetch(api_url, {
	method: 'POST',
	body: JSON.stringify(textToSend),
	headers:{
		'Content-Type': 'application/json'
	} })

.then(data => { return data.json() })
.then(response => response.text()
.catch(error => console.error('Error:', error));
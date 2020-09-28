// An alert to let the broswer know it could take a bit
alert("Reading reviews (and drinking coffee), this may take a moment.");

// This function converts unicode to characters
function unicodeToChar(text) {
	return text.replace(/\\u[\dA-F]{4}/gi, 
	      function (match) {
	           return String.fromCharCode(parseInt(match.replace(/\\u/g, ''), 16));
	      });
}

// Grab the review text
var textToSend = document.body.getElementsByClassName('a-size-base review-text review-text-content');

// This is the url to my python file (for once I deploy)
const api_url = 'https://edf4jelo3f.execute-api.us-east-1.amazonaws.com/dev/builder-v1-call';

// Fetch calls the fucntion
fetch(api_url, {
	method: 'POST',
	body: JSON.stringify(textToSend),
	headers:{
		'Content-Type': 'application/json'
	} })
// This gets the data in json format
.then(data => { return data.json() })
// What effect does my function return have?
.then(response => response.text()
// This catches errors and prints to console
.catch(error => console.error('Error:', error));

// fetch(api_url, {
//   method: 'POST',
//   body: JSON.stringify(textToSend),
//   headers:{
//     'Content-Type': 'application/json'
//   } })
// .then(data => { return data.json() })
// .then(res => { 
// 	$.each(res, function( index, value ) {
// 		value = unicodeToChar(value).replace(/\\n/g, '');
// 		document.body.innerHTML = document.body.innerHTML.split(value).join('<span style="background-color: #fff799;">' + value + '</span>');
// 	});
//  })
// .catch(error => console.error('Error:', error));
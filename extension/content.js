// An alert to let the broswer know it could take a bit
alert("Reading reviews (and drinking coffee), this may take a moment.");

// This function converts unicode to characters
function unicodeToChar(text) {
	return text.replace(/\\u[\dA-F]{4}/gi, 
	      function (match) {
	           return String.fromCharCode(parseInt(match.replace(/\\u/g, ''), 16));
	      });
}

// // This function will get reviews from multiple Amazon review pages
// function getReviewBodies(url) {

// 	// Remove the pagenumber for the url

// 	// Loop through review pages
// 	var i;
// 	for (i = 0; i < 5; i++) {
// 		// Get all review text on each page
// 		var textToSend = document.body.getElementsByClassName('a-size-base review-text review-text-content');
// 	}
// }

// We need to check whether the page is Wayfair or Amazon
var currentPage = window.location.href;
var searchParams = new URLSearchParams(currentPage);
// A boolean that is true if we are on Wayfair
var isWayfair = searchParams.has("wayfair");

if (isWayfair) {
	// We are on a Wayfair page
	var textToSend = document.body.getElementsByClassName('ProductCollapsibleText is-collapsed');
} else {
	// We are on Amazon (loop through review pages... )
	var textToSend = document.body.getElementsByClassName('a-size-base review-text review-text-content');
}

alert("Sending text: " + textToSend)

// This is the url to my python file (for once I deploy)
// const api_url = 'https://edf4jelo3f.execute-api.us-east-1.amazonaws.com/dev/builder-v1-call';
const api_url = 'https://edf4jelo3f.execute-api.us-east-1.amazonaws.com/dev'

// Fetch calls the fucntion
fetch(api_url, {
	method: 'POST',
	body: JSON.stringify(textToSend),
	headers:{
		'Content-Type': 'application/json'
	} })
// This gets the data in json format
.then(data => {
	alert("Returning data... ")
	return data.json();
})
// What effect does my function return have?
.then(response => {
	assemblyRating = response.text();
	alert("Ease of assemby: " + assemblyRating);
})
// This catches errors and prints to console
.catch(error => console.error('Error:', error));


// This is an example call to a serverless system
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


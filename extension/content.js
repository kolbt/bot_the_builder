// An alert to let the broswer know it could take a bit
alert("Reading reviews (and drinking coffee), this may take a moment.");

// This is the url to my python file (for once I deploy)
const api_url = 'https://z27ce31j6d.execute-api.us-east-1.amazonaws.com/public/compute';

// This gives you a list of the review elements from Wayfair
var text = document.body.getElementsByClassName('ProductReview-comments')
// Call them by index and grab the text
var out = [];
var i;
for (i = 0; i < text.length; i++) { 
	// This is a list of review strings
	out.push(text[i].innerText);
}

// Convert this array to a JSON-friendly format
var jsonOut = JSON.stringify(out)

// Make sure you've got the data
alert("Okay, I've read the reviews, let me think for a second... ");

fetch(api_url, {
	method: 'POST',
	body: jsonOut,
	headers:{
		'Content-Type': 'application/json'
	} })
.then(response => response.text())
.then(result => alert("Ease of assembly: " + result))
.catch(error => console.log('error'.error));

// An alert to let the broswer know it could take a bit
// alert("Reading reviews (and drinking coffee), this may take a moment.");

// This is the url to my python file (for once I deploy)
// const api_url = 'https://z27ce31j6d.execute-api.us-east-1.amazonaws.com/public/compute';

// Ideally I want to open the reviews automatically
function openReviews(nOpen) {
	var elements = document.getElementsByClassName('Button Button--alternate Button--large Button--plainText');
	var requiredElement = elements[0];
	requiredElement.click();
}

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
// alert("Okay, I've read the reviews, let me think for a second... ");

// Store the output here
var output = "?"

const request = async () => {
    var response = await fetch('https://z27ce31j6d.execute-api.us-east-1.amazonaws.com/public/compute', {method: 'POST', body: jsonOut, headers:{'Content-Type': 'application/json'}});
    output = await response.text();
    alert("Your assembly summary is ready to read, cheers!")
    chrome.runtime.onMessage.addListener(
	    function(message, sender, sendResponse) {
	        switch(message.type) {
	            case "getOutput":
	                sendResponse(output);
	                break;
	            default:
	                console.error("Unrecognised message: ", message);
	        }
	    }
	);
}

request();


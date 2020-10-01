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

// This sample output works...
// var out = ["Really comfortable, love the style , however it’s not leather , so if you sit on chair for a while the fabric will begin to move. It is over priced I think but I really loved the chair so for me it was worth it .",
// "Good chair. Very easy to assemble...very adjustable. Faux gives it a great leather appearance",
// "It’s only been one week, but that’s 50 hours of zoom meetings without any issues. I wish it went about an inch lower because my feet aren’t quite flat, but it’s comfortable and feels sturdy. I also wish the arms were adjustable, but the high back is a life-saver. Easy to assemble, but I made a few mistakes due to very poor written instructions. But overall, I think I’m going to be happy with this chair for quite a while."]
// var jsonOut = JSON.stringify(out)

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

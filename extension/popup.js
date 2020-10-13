// This will execute the content.js file when my button is clicked
function assemble() {
	chrome.tabs.executeScript(null, { file: "jquery-3.5.1.js" }, function() {
		chrome.tabs.executeScript(null, { file: "content.js" });
	});
}

// An event listener waiting for me to click the button
document.getElementById('clickme').addEventListener('click', assemble);

chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
        chrome.tabs.sendMessage(tabs[0].id, {type: "getOutput"}, function(output) {
        	if(output)
        	{
        		var display = JSON.parse(output)
                document.getElementById('ease-rating').innerHTML = display[0] + " out of 5";
                document.getElementById('tool-rating').innerHTML = display[1] + " out of 5";
                document.getElementById('time-rating').innerHTML = display[2] + " out of 5";
                document.getElementById('quality-rating').innerHTML = display[3] + " out of 5";
	        	document.getElementById('positive-review').innerHTML = "\"" + display[4] + "\"";
	        	document.getElementById('negative-review').innerHTML = "\"" + display[5] + "\"";
                // Update the popup
                //location.reload();
        	}
        });
    });

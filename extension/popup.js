// This will execute the content.js file when my button is clicked
function assemble() {
	chrome.tabs.executeScript(null, { file: "jquery-3.5.1.js" }, function() {
		chrome.tabs.executeScript(null, { file: "content.js" });
	});
}
// An event listener waiting for me to click the button
document.getElementById('clickme').addEventListener('click', assemble);
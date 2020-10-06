var output;
chrome.runtime.onMessage.addListener(function(message,sender,sendResponse){
	if(message.type == 'setData')
    	output = message.info;
  	else if(message.method == 'getData')
    	sendResponse(title);
});
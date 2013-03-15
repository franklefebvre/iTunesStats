displayPieChart = function(containerName, jsonPath) {
	var xhr = new XMLHttpRequest();

	xhr.onreadystatechange = function () {
	  if (xhr.readyState == 4 && (xhr.status == 200 || xhr.status == 0)) {
		graphData = eval(xhr.responseText);
		var container = document.getElementById(containerName),
		graph;
		graph = Flotr.draw(container, graphData,
			{pie : {show : true, explode : 6},
			xaxis : {showLabels:false},
			yaxis : {showLabels:false},
			HtmlText: false,
			grid : {verticalLines : false,
				horizontalLines : false},
				mouse : { track : true },
				legend : {
					position : 'n',
					backgroundColor : '#D2E8FF'
				}
			});
	  };
	};

	xhr.open("GET", jsonPath, true);
	xhr.send();
};

displayBarGraph = function(containerName, jsonPath) {
	var xhr = new XMLHttpRequest();

	xhr.onreadystatechange = function () {
		if (xhr.readyState == 4 && (xhr.status == 200 | xhr.status == 0)) {
			graphData = eval(xhr.responseText);
			var container = document.getElementById(containerName), graph;
			graph = Flotr.draw(container, [graphData],
				{bars : {show : true, horizontal: false, shadowSize : 0, barWidth : 1},
				mouse : {track : true, relative : true},
				yaxis: {min: 0}
			});
		};
	};

	xhr.open("GET", jsonPath, true);
	xhr.send();
};

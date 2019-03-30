function viewTree(el_id, divHeight, fileName) {
	/**
	 * Interactive, zoomable treemap, using D3 v4
	 * http://bl.ocks.org/guglielmo/16d880a6615da7f502116220cb551498
	 *
	 * A port to D3 v4 of Jacques Jahnichen's Block, using the same budget data
	 * see: http://bl.ocks.org/JacquesJahnichen/42afd0cde7cbf72ecb81
	 *
	 * Author: Guglielmo Celata
	 * Date: sept 1st 2017
	 **/
	var obj = document.getElementById(el_id);
	var divWidth = obj.offsetWidth;
	var margin = {top: 30, right: 0, bottom: 20, left: 0},
		width = divWidth -25,
		height = divHeight - margin.top - margin.bottom,
		transitioning,
		formatSize = d3.format(".2s"),
		formatP = d3.format(".2p"),
		// totalSize is initialized when the data is loaded, below.
		totalSize = 1;
	function formatNumber(x) {
		// Display size both as absolute value and percentage.
		return formatSize(x) + " / " + formatP(x/totalSize);
	}

	// sets x and y scale to determine size of visible boxes
	var x = d3.scaleLinear()
		.domain([0, width])
		.range([0, width]);
	var y = d3.scaleLinear()
		.domain([0, height])
		.range([0, height]);

	// Initialize the treemap visualization.
	var treemap = d3.treemap()
		.tile(d3.treemapSquarify)
		.size([width, height])
		.paddingInner(0)
		.round(false);

	// color is further initialized when the data is loaded.
	var color;

	// Create the SVG.
	var svg = d3.select('#'+el_id).append("svg")
		.attr("width", width + margin.left + margin.right)
		.attr("height", height + margin.bottom + margin.top)
		.style("margin-left", -margin.left + "px")
		.style("margin.right", -margin.right + "px")
		.append("g")
		.attr("transform", "translate(" + margin.left + "," + margin.top + ")")
		.style("shape-rendering", "crispEdges");

	var grandparent = svg.append("g")
		.attr("class", "grandparent");
	grandparent.append("rect")
		.attr("y", -margin.top)
		.attr("width", width)
		.attr("height", margin.top)
		.attr("fill", '#bbbbbb');
	grandparent.append("text")
		.attr("x", 6)
		.attr("y", 6 - margin.top)
		.attr("dy", ".75em");

	console.log("init done");

	function display(d) {
		// write text into grandparent and activate click's handler.
		grandparent
			.datum(d.parent)
			.on("click", transition)
			.select("text")
			.text(name(d));
		var g1 = svg.insert("g", ".grandparent")
			.datum(d)
			.attr("class", "depth");
		var g = g1.selectAll("g")
			.data(d.children)
			.enter().
			append("g");
		// add class and click handler to all g's with childre.n
		g.filter(function (d) {
			return d.children;
		})
			.classed("children", true)
			.on("click", transition);

		g.selectAll(".child")
			.data(function (d) {
				return d.children || [d];
			})
			.enter().append("rect")
			.attr("class", "child")
			.call(rect);

		// add title to parents.
		g.append("rect")
			.attr("class", "parent")
			.call(rect)
			.append("title")
			.text(function (d){
				return d.data.name;
			});

		/* Adding a foreign object instead of a text object, allows
		 * for text wrapping */
		g.append("foreignObject")
			.call(rect)
			.attr("class", "foreignobj")
			.append("xhtml:div")
			.attr("dy", ".75em")
			.html(function (d) {
				return '' +
					'<p class="title"> ' + d.data.name + '</p>' +
					'<p>' + formatNumber(d.value) + '</p>'
				;
			})
			.attr("class", "textdiv");


		function transition(d) {
			if (transitioning || !d) return;

			transitioning = true;

			var g2 = display(d),
				t1 = g1.transition().duration(650),
				t2 = g2.transition().duration(650);

			// Update the domain only after entering new elements.
			x.domain([d.x0, d.x1]);
			y.domain([d.y0, d.y1]);

			// Enable anti-aliasing during the transition.
			svg.style("shape-rendering", null);

			// Draw child nodes on top of parent nodes.
			svg.selectAll(".depth").sort(function (a, b) {
				return a.depth - b.depth;
			});

			// Fade-in entering text.
			g2.selectAll("text").style("fill-opacity", 0);
			g2.selectAll("foreignObject div").style("display", "none");

			// Transition to the new view.
			t1.selectAll("text").call(text).style("fill-opacity", 0);
			t2.selectAll("text").call(text).style("fill-opacity", 1);
			t1.selectAll("rect").call(rect);
			t2.selectAll("rect").call(rect);
			/* Foreign object */
			t1.selectAll(".textdiv").style("display", "none");
			t1.selectAll(".foreignobj").call(foreign);
			t2.selectAll(".textdiv").style("display", "block");
			t2.selectAll(".foreignobj").call(foreign);

			// Remove the old node when the transition is finished.
			t1.on("end.remove", function(){
				this.remove();
				transitioning = false;
			});
		}
		return g;
	}
	function text(text) {
		text
			.attr("x", function (d) {
				return x(d.x) + 6;
			})
			.attr("y", function (d) {
				return y(d.y) + 6;
			});
	}
	function rect(rect) {
		rect
			.attr("x", function (d) {
				return x(d.x0);
			})
			.attr("y", function (d) {
				return y(d.y0);
			})
			.attr("width", function (d) {
				return x(d.x1) - x(d.x0);
			})
			.attr("height", function (d) {
				return y(d.y1) - y(d.y0);
			})
			.attr("fill", function (d) {
				return color(breadcrumbs(d)); //'#bbbbbb';
			});
	}
	function foreign(foreign) { /* added */
		foreign
			.attr("x", function (d) {
				return x(d.x0);
			})
			.attr("y", function (d) {
				return y(d.y0);
			})
			.attr("width", function (d) {
				return x(d.x1) - x(d.x0);
			})
			.attr("height", function (d) {
				return y(d.y1) - y(d.y0);
			});
	}
	function name(d) {
		return breadcrumbs(d) + " — (" + formatNumber(d.value) + ")" +
			(d.parent
			 ? " — Click to zoom out"
			 : " — Click inside square to zoom in");
	}
	function breadcrumbs(d) {
		var res = "";
		d.ancestors().reverse().forEach(function(i){
			res += i.data.name;
		});
		return res;
	}
	console.log("start done");

	var data;
	function valFnSize(d) { return d.value }
	function valFnCount(d) { return d.value ? 1 : 0 }
	var valFn = valFnSize;

	function doDisplay() {
		var root = data
			.sum(valFn)
			.sort(function (a, b) {
				return /* b.height - a.height || */ b.value - a.value
			})

		// Initialize the total size for percentages.
		totalSize = root.value;
		console.log("total size:", totalSize);

		// Create the color spectrum.
		var l = [];
		root.eachBefore(function (d) {
			l.push(breadcrumbs(d));
		});
		colors = []
		for (var i in l) {
			colors.push(d3.interpolateSpectral(i / (l.length-1)));
		}
		color = d3.scaleOrdinal().domain(l).range(colors);

		// Display.
		treemap(root);
		display(root);
	}

	d3.json(fileName, function(fdata) {
		console.log("load done");

		// Interpret the dict as a hierarchy.
		data = d3.hierarchy(fdata);

		var p = d3.select('#'+el_id);
		p.append("br");
		p
			.append("button")
			.text("size")
			.on("click", function(d,i) {
				valFn = valFnSize;
				doDisplay();
			});
		p
			.append("button")
			.text("count")
			.on("click", function(d,i) {
				valFn = valFnCount;
				doDisplay();
			});
		doDisplay();
	});
}

jQuery(function($){
  $(document).ready(function(){

    // Update the chart when interpolation value changes
    $('div.chart-container #interpolation').change(function(e) {
      loadChart($(this).val());
    });

    // By default, use "cardinal" interpolation
    loadChart('cardinal');

    function loadChart(interpolation) {
      if ($("#chart svg").length > 0) {
          $("#chart").css('height', $("#chart").innerHeight());
          $("#chart").css('width', $("#chart").innerWidth());
      }

      $("#chart").html("");

      d3.json("historicjson", function(error, data) {
        if (error || data.length < 2) {
            $(".chart-container").hide();
            return;
        }
        $(".chart-container").show();
        var margin = {top: 20, right: 120, bottom: 30, left: 50},
            width = $('#chart').innerWidth() - margin.left - margin.right,
            height = 250 - margin.top - margin.bottom;

        var parseDate = d3.time.format("%Y-%m-%d %H:%M %p").parse;

        var x = d3.time.scale()
            .range([0, width]);

        var y = d3.scale.linear()
            .range([height, 0]);

        var color = d3.scale.category10();

        var xAxis = d3.svg.axis()
            .scale(x)
            .orient("bottom");

        var yAxis = d3.svg.axis()
            .scale(y)
            .orient("left");

        var line = d3.svg.line()
            .interpolate(interpolation)
            .x(function(d) { return x(d.date); })
            .y(function(d) { return y(d.result); });

        $('#chart').append('<svg></svg>');
        var svg = d3.select("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
          .append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

        color.domain(d3.keys(data[0]).filter(function(key) { return key !== "date"; }));
        data.forEach(function(d) {
            d.date = parseDate(d.date);
        });

        var series = color.domain().map(function(name) {
            return {
              name: name,
              values: data.map(function(d) {
                return {date: d.date, result: +d[name]};
              })
            };
        });

        x.domain(d3.extent(data, function(d) { return d.date; }));

        y.domain([
            d3.min(series, function(c) { return d3.min(c.values, function(v) { return v.result; }); }),
            d3.max(series, function(c) { return d3.max(c.values, function(v) { return v.result; }); })
        ]);

        svg.append("g")
          .attr("class", "x axis")
          .attr("transform", "translate(0," + height + ")")
          .call(xAxis);

        svg.append("g")
          .attr("class", "y axis")
          .call(yAxis)
        .append("text")
          .attr("transform", "rotate(-90)")
          .attr("y", 6)
          .attr("dy", ".71em")
          .style("text-anchor", "end")
          .text("Result");

        var serie = svg.selectAll(".serie")
          .data(series)
        .enter().append("g")
          .attr("class", "serie");

        serie.append("path")
          .attr("class", "line")
          .attr("d", function(d) { return line(d.values); })
          .style("stroke", function(d) { return color(d.name); });

        serie.append("text")
          .datum(function(d) { return {name: d.name, value: d.values[d.values.length - 1]}; })
          .attr("transform", function(d) { return "translate(" + x(d.value.date) + "," + y(d.value.result) + ")"; })
          .attr("x", 10)
          .attr("dy", ".35em")
          .text(function(d) { return d.name; });

        series.forEach(function(d) {
            res = d.results;
            vals = d.values;
            col = color(d.name);
            vals.forEach(function(v) {
                svg.append("circle")
                  .attr("r", 4)
                  .style("fill", col)
                  .attr("cx", x(v.date))
                  .attr("cy", y(v.result))
               /* svg.append("text")
                  .attr("x", x(v.date)-5)
                  .attr("dy", y(v.result)-5)
                  .text(parseFloat(v.result).toFixed(2))*/

            });
        });
      });
    }

  });
});
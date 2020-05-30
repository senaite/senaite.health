jQuery(function($){
  $(document).ready(function(){

    // Update the chart when interpolation value changes
    $('div.chart-container #interpolation').change(function(e) {
      loadChart($(this).val());
    });

    // By default, use "linear" interpolation
    loadChart("linear");

    function loadChart(interpolation) {
      if ($("#chart svg").length > 0) {
        $("#chart").css("height", $("#chart").innerHeight());
        $("#chart").css("width", $("#chart").innerWidth());
      }

      $("#chart").html("");

      d3.json("historicjson", function(error, data) {

        // Do not display the chart if less than two results
        if (error || data.length < 2) {
          $(".chart-container").hide();
          return;
        }

        $(".chart-container").show();

        var margin = {top: 20, right: 120, bottom: 30, left: 50},
          width = $('#chart').innerWidth() - margin.left - margin.right,
          height = 250 - margin.top - margin.bottom;

        var parse_date = d3.time.format("%Y-%m-%d %H:%M").parse;

        var color = d3.scale.category10();

        var x = d3.time.scale()
          .range([0, width]);

        var y = d3.scale.linear()
          .range([height, 0]);

        var xAxis = d3.svg.axis()
          .scale(x)
          .orient("bottom")
          .tickSize(0);

        var yAxis = d3.svg.axis()
          .scale(y)
          .orient("left")
          .tickSize(0);

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

        // Extract the keys for series (data series might be unbalanced)
        var keys = d3.set()
        data.forEach(function(d) {
          var row_keys = d3.keys(d);
          row_keys.forEach(function(key) {
            if (key !== "date") {
              keys.add(key);
            }
          });
        });
        color.domain(keys.values());

        // Apply valid format to date (x-axis)
        data.forEach(function(d) {
          d.date = parse_date(d.date);
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
          d3.min(series, function(c) {
            return d3.min(c.values, function(v) {
              return (typeof v === 'undefined') ? "" : v.result;
            });
          }),
          d3.max(series, function(c) {
            return d3.max(c.values, function(v) {
              return (typeof v === 'undefined') ? "" : v.result;
            });
          })
        ]);

        svg.append("g")
          .attr("class", "x axis")
          .attr("fill", "#3f3f3f")
          .style("font-size", "11px")
          .attr("transform", "translate(0," + height + ")")
          .call(xAxis)
            .append("text")
              .attr("x", width)
              .attr("dy", "-0.71em")
              .attr("text-anchor", "end")
              .text("Date captured");

        svg.append("g")
          .attr("class", "y axis")
          .attr("fill", "#3f3f3f")
          .style("font-size", "11px")
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
          .attr("fill", "none")
          .attr("d", function(d) {
            var vals = d.values;
            return line(
              // Bail out empty values
              vals.filter(function(value) {
                  return !(Number.isNaN(value.result));
              })
            );
          })
          .attr("stroke-width", "1.5px")
          .style("stroke", function(d) { return color(d.name); })
          .on("mouseout", function() {
            d3.select(this)
              .attr("stroke-width", "1.5px");
          })
          .on("mouseover",  function() {
            d3.select(this)
              .attr("stroke-width", "4px");
          });

        // Place the legend for the series
        serie.append("text")
          .datum(function(d) {
            // Get the last non empty value for this serie
            var last_val = 0;
            for (var i = d.values.length - 1; i >= 0; i--) {
              var val = d.values[i];
              console.log(val);
              if (!Number.isNaN(val.result)) {
                last_val = val;
                break;
              }
            }
            return {name: d.name, value: last_val};
          })
          .attr("transform", function(d) { return "translate(" + x(d.value.date) + "," + y(d.value.result) + ")"; })
          .attr("x", 10)
          .attr("dy", ".35em")
          .style("font-size", "11px")
          .style("fill", function(d) { return color(d.name);})
          .text(function(d) { return d.name; });

        series.forEach(function(d) {
          res = d.results;
          vals = d.values;
          col = color(d.name);
          vals.forEach(function(v) {
            // Do not create dots for empty values
            if (Number.isNaN(v.result)) {
              return;
            }
            svg.append("circle")
              .attr("r", 3)
              .style("fill", col)
              .attr("cx", x(v.date))
              .attr("cy", y(v.result))
              .on("mouseout", function() {
                last = this.parentNode.children.length;
                d3.select(this)
                  .attr("r", 3);
                d3.select(this.parentNode.children[last-1])
                  .remove();
              })
              .on("mouseover",  function() {
                d3.select(this)
                  .attr("r", 6);
                d3.select(this.parentNode)
                  .append("text")
                    .attr("fill", "#000000")
                    .style("font-size", "11px")
                    .attr("x", x(v.date) - 10)
                    .attr("y", y(v.result) - 10)
                    .text(v.result)
              })
          });
        });
      });
    }

  });
});
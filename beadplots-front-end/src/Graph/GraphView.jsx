import React, { useState, useEffect } from "react";
import d3 from "d3";
import { Component as D3Component } from "react-d3-library";

const GraphView = () => {
  let [d3Node, setD3Node] = useState('');

  useEffect(() => {
    var node = document.createElement("div");
    let width = 950,
      height = 500;

    var svg = d3
      .select(node)
      .append("svg")
      .attr("width", width)
      .attr("height", height);

    var defs = svg.append("defs");

    defs
      .append("clipPath")
      .attr("id", "circle1")
      .append("circle")
      .attr("cx", 350)
      .attr("cy", 200)
      .attr("r", 180)
      .attr('fill',  'red');

    defs
      .append("clipPath")
      .attr("id", "circle2")
      .append("circle")
      .attr("cx", 550)
      .attr("cy", 200)
      .attr("r", 180)
      .attr('fill',  'red');
    
    setD3Node(node);
  }, [])

  return (
    <div id="data-viz">
      <D3Component data={d3Node} />
    </div>
  );
};

export default GraphView;

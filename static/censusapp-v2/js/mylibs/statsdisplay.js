protovis_sex_age = function(male, female, renderTarget) {
    var w = 50,
        h = 50,
        x = pv.Scale.linear(0, 700).range(0, w),
        y = pv.Scale.ordinal(pv.range(10)).splitBanded(0, h, 9/10);

    console.debug(x);
    var vis = new pv.Panel()
        .width(w)
        .height(h)
        .bottom(0)
        .left(25)
        .right(0)
        .top(5);


    var bar = vis.add(pv.Bar)
        .data(female)
        .top(function() y(this.index))
        .height(y.range().band)
        .left(25)
        .width(x);

    var bar = vis.add(pv.Bar)
        .data(male)
        .top(function() y(this.index))
        .height(y.range().band)
        .right(w-25)
        .width(x)
        .fillStyle('red');

    /*
    bar.anchor('right').add(pv.Label)
        .textStyle('white')
        .text(function(d) d.toFixed(0));
    */    
    /*
    bar.anchor('left').add(pv.Label)
        .textMargin(5)
        .textAlign('right')
        .text(function() "ABCDEFGHIJK".charAt(this.index));
    */
    /*
    vis.add(pv.Rule)
        .data(x.ticks(5))
        .left(x)
        .strokeStyle(function(d) d ? "rgba(255,255,255,.3)" : "#000")
      .add(pv.Rule)
        .bottom(0)
        .height(5)
        .strokeStyle("#000")
      .anchor("bottom").add(pv.Label)
        .text(x.tickFormat);
    */
    vis.canvas(renderTarget);
    vis.render();

};

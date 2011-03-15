protovis_sex_age = function(male, female, renderTarget) {
    var w = 100,
        h = 50,
        x = pv.Scale.linear(0,800).range(0, w/2),
        y = pv.Scale.ordinal(pv.range(8)).splitBanded(0, h, 8/10);

    console.debug(x);
    var vis = new pv.Panel()
        .width(w)
        .height(h)
        .bottom(0)
        .left(25)
        .right(0)
        .top(5);


    var femalebar = vis.add(pv.Bar)
        .data(female)
        .top(function() y(this.index))
        .height(y.range().band)
        .left(25)
        .width(x);

    var malebar = vis.add(pv.Bar)
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
    
    femalebar.add(pv.Label)
        .textMargin(5)
        .top(function() y(this.index)+10)
        .left(100)
        .textAlign('right')
        .text(function() ['15', '', '', '44', '', '', '', '79'][this.index]);
    
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

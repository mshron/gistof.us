var fetch_url = 'http://localhost:8080/tracts';
var global_data_url = 'http://localhost:8080/static/censusapp-v3/histograms.json';
var colorscale = ['#e78dc5', '#f8daec', '#fbfbfb', '#dbf0c2', '#a6d592']
var language_names = ['Only English','Spanish or Spanish Creole','French (incl. Patois, Cajun)','French Creole','Italian','Portuguese or Portuguese Creole','German','Yiddish','Other West Germanic languages','Scandinavian languages','Greek','Russian','Polish','Serbo-Croatian','Other Slavic languages','Armenian','Persian','Gujarati','Hindi','Urdu','Other Indic languages','Other Indo-European languages','Chinese','Japanese','Korean','Mon-Khmer, Cambodian','Hmong','Thai','Laotian','Vietnamese','Other Asian languages','Tagalog','Other Pacific Island languages','Navajo','Other Native North American languages','Hungarian','Arabic','Hebrew','African languages','Other and unspecified languages']

function which_bin(bin_edges, v) {
    for (var i=0; i<bin_edges.length; i++) {
        if (v < bin_edges[i]) {
            return i
        }

    }
    return bin_edges.length-1
}

function quintilebg(x) {
    try {
        //expects a decimal from 0.0 to 1.0
        return colorscale[Math.floor(x*5)]
    } catch(e) {
        return colorscale[2]
    } 
}

function setuplegend() {
    for (var i = 0; i < 5; i++) {
        $('#quintilelegend #'+i+'.legend').css('background-color',colorscale[i])
    }
}

function mapinit() {
  var myLatlng = new google.maps.LatLng(47.7, -122.3);//-34.397, 150.644);
  var myOptions = {
    zoom: 6,
    center: myLatlng,
    disableDefaultUI: true,
    mapTypeId: google.maps.MapTypeId.ROADMAP,
    draggingCursor: 'pointer',
    draggableCursor: 'pointer'
  }
  var map = new google.maps.Map(document.getElementById("map_canvas"), myOptions);
  return map;
}

function raise(e) {
    console.debug(e);
}   


function latlon(d) {
    try {
        var lat = d.loc.lat;
        var lon = d.loc.lon;

        var loc_string = lat+", "+lon;
        $('#lat_lon').html(loc_string);

    } catch(e) {
        raise(e)
    }
}

function population(d) {
    try {
            var pop_total = d.population.total;
            var pop_moe = d.population.total_moe;
            $('#population-stat .stat_local').html(pop_total);
            //age
            var age_distribution = d.age.distribution;
            $age_stat = $('#age-distribution-stat .inlinebar');
            $age_stat.sparkline(age_distribution, {type: 'bar', barColor: 'blue'});

    } catch (e) {
       raise(e);
    }
}


function race(d) {
    try {
// ['White', 'Black', 'Native', 'Asian', 'Pacific Islander', 'Other', 'Two or More'];
        var pop_total = d.population.total;
        var pct_wnl = d.race.pct_white_not_latino;

        pct_wnl = percentify(pct_wnl, 2);
        pct_wnl = parseFloat(pct_wnl).toFixed(2) + "%"
        $('#race-stat .stat_local').html(pct_wnl);

        var percentile = d.race.pct_white_not_latino_percentile;
        // the 1- makes "highest" mean "highest diversity"... does this
        // make sense? Or should we change the stat to be % NOT wnl?
        bgcolor = quintilebg(0.99-percentile/100);
        $('div#race-stat').css('background-color',bgcolor);
        

    } catch(e) {
        raise(e);
    }
    



}
function poverty(d) {
    try {
            var pct_below_100pc = d.poverty.pct_below_100pc;
            var fontsize = 18;
            if (pct_below_100pc < 0.1) {
                fontsize = 12;
            }

            pct_below_100pc = percentify(pct_below_100pc, 0);
            var percentile = d.poverty.pct_below_100pc_percentile;
            bgcolor = quintilebg(percentile/100);
            $('div#below-poverty-stat').css('background-color',bgcolor);
            $('#below-poverty-stat .stat_local').html(pct_below_100pc);
            //$('#below-poverty-stat .stat_local').animate({fontSize: fontsize}, 2000);
    } catch(e) {
        raise(e);
    }
}


function veteran(d) {
   try {
      var name = 'pct_veteran';
      var pct_veterans = d.veteran_status.pct_veteran;
      pct_veterans = (pct_veterans * 100).toFixed(0);
      pct_veterans = pct_veterans + '%';

      $('#veteran-status-stat .stat_local').html(pct_veterans);

      var percentile = d.veteran_status[name+'_percentile']
      bgcolor = quintilebg(percentile/100);
      $('div#veteran-status-stat').css('background-color',bgcolor);
    } catch(e) {
       raise(e);
    }
}

function sex(d) {
    try {
       var female_total = d.sex.female;
       var female_moe = d.sex.female_moe;
       var male_total = d.sex.male;
       var male_moe = d.sex.male_moe;

       var sex_dom = $('#sex-stat .stat_local')[0];
       $('#sex-stat .stat_local').sparkline(
           [male_total, female_total],
           {type: 'pie', sliceColors: ['#4985D6', '#EA8DFE'],
            offset: -90,
            width: '70px', height: '70px'});
       //protovis_sex(male_total, female_total, sex_dom);
    } catch(e) {
        raise(e);
    }
}

function sex_by_age(d) {
    try {
       var female = d.sex_by_age.female;
       var male = d.sex_by_age.male;
       
       var sex_by_age_dom = $('#age-distribution-stat .stat_local')[0];
       //protovis_sex_age(male.reverse(), female.reverse(), sex_by_age_dom);
    } catch(e) {
        raise(e);
    }
}

function latino(d) {
    try {
        var name = 'pct_hispanic_or_latino';
        var pct_latino = percentify(d.hispanic_or_latino.pct_hispanic_or_latino, 0);
        $('#latino-stat .stat_local').html(pct_latino);

        var percentile = d.hispanic_or_latino[name+'_percentile']
        bgcolor = quintilebg(percentile/100);
        $('div#latino-stat').css('background-color',bgcolor);
    } catch(e) {
        raise(e);
    }
}

function placename(d) {
    try {
        $('#lat').html(parseFloat(d.loc.lat).toFixed(2))
        $('#lon').html(parseFloat(d.loc.lon).toFixed(2))
        $('#county').html(d.loc.county)
        $('#state').html(d.loc.state)
    } catch(e) {
       raise(e);
    }
}

function percentify(n, places) {
    var string = (n*100).toFixed(places);
    return string + "%";
}    

var markers = [null];

function updateMap(map, lat, lng) {
    var LL = new google.maps.LatLng(lat,lng);
    map.panTo(LL); 
    //console.debug(lat,lng);
    var newMarker = new google.maps.Marker({
        position: LL,
        animation: google.maps.Animation.DROP,
        map: map});
    var old = markers[0];
    if (old != null) {
        old.setMap(null)
        }
    markers[0] = newMarker;
}

function update_map(d, map) {
    try {
        var lat = d.loc.lat;
        var lon = d.loc.lon;
        updateMap(map, lat,lon);
    } catch (e) {
        raise(e)
    }
}

render_functions = [population, poverty, veteran, sex, sex_by_age, update_map, latino, race, latlon, placename]



/*function handlekeys(event) {
    switch (event.keycode) {
        37: //left
        38: //up
        39: //right
        40: //down
    }
}*/

$(function() {
    // layout
    setuplegend();

    // map
    var map = mapinit();

    // API communication
    
    
    Tract = Backbone.Model.extend({
        initialize: function() {
            App.addOneView(this);
        }
    });
    
    TractRing = Backbone.Collection.extend({

        model: Tract,
        
        // url used for the initial fetch of "default" values
        url: function() {
            // server has a default n (amt of context)
            // so no need to specify one
            var url = fetch_url;
            var hash = window.location.hash;            
            if (hash !== '' && !isNaN(hash)) { 
                url += '?j='+hash; 
            }             
            return url;
        },
        
        initialize: function() {
            this.bind('refresh', function() {            
                    if (this.length === 0) { return; }            
                    // center of non-empty list is floor(length/2)
                    var center = Math.floor(this.length/2)  ;
                    this.currentTract = this.at(center);
                    this.currentTractIndex = center;
                });
                
            this.bind('add:left', this.fixDisplacedIndex);
            
            this.global_data = null;
            this.getGlobalData();


            // create a new TractDataManager
            this.manager = new TractDataManager(this);
            
            this.currentTract = null;
            this.currentTractIndex = null;

        },             
        
        getGlobalData: function() {
            request = $.ajax({
                            url: global_data_url,
                            type: 'GET',
                            dataType: 'json',
                            context: this,         //context for callbacks
                            success: function(json) {
                                this.global_data = json;
                            }
                            //error: this.retryAjax
            });
        },

        addLeft: function(models, options) {
            if (_.isArray(models)) {
                for (var i = 0, l = models.length; i < l; i++) {
                    this._addLeft(models[i], options);
                }
            } 
            else {
                this._addLeft(models, options);
            }
            return this;
        },

        _addLeft: function(model, options) {

               options || (options = {});
               if (!(model instanceof Backbone.Model)) {
                   model = new this.model(model, {collection: this});
               }
               var already = this.getByCid(model);
               if (already) throw new Error(["Can't add the same model to a set twice", already.id]);
               this._byId[model.id] = model;
               this._byCid[model.cid] = model;
               model.collection = this;
               this.models.unshift(model);  //to the left!
               model.bind('all', this._boundOnModelEvent);
               this.length++;
               if (!options.silent) model.trigger('add:left', model, this, options);
               return model;


        },
        
        moveLeft: function() {            
            //all the way left?  let everyone know
            // this only happens when we haven't succeeded in fetching
            // more tract data from the left
            if (this.currentTractIndex == 0) {
                this.trigger('nav:block', 'left');
            }
            else {                
                this.currentTract = this.at(--this.currentTractIndex);
                this.trigger('nav:tract', 'left');
            }
        },
            
        moveRight: function() {
            // all the way right?  let everyone know
            // this only happens when we haven't succeeded in fetching
            // more tract data from the right
            lastIndex = this.length-1;
            if (this.currentTractIndex == lastIndex) {
                this.trigger('nav:block', 'right');
            }
            else {
                this.currentTract = this.at(++this.currentTractIndex);
                this.trigger('nav:tract', 'right');
            }
        },
        
        // This function is called when an 'add:left' event is
        // fired on the collection.        
        fixDisplacedIndex: function() {        
            // each time, we simply have to move the currentTractIndex
            // one to the right
                             
            // example: currentTractIndex is 1
            // we add an element on the left
            // the current tract is now the 2th element, instead of the 1th
            // (the new one is the 0th)
            // so we increment currentTractIndex
            
            // if there's no currentTract, don't bother trying
            // to fix things that don't exist
            if (this.currentTract == null)           { return; }
            
            // orig is the currentTractIndex we had stored
            // before we added in more tracts
            this.currentTractIndex++;
            
        }
                
    });    
    
    TractView = Backbone.View.extend({
       
        tagName: 'div',

        template: _.template($('#tract-template').html()),
        imgDivTemplate: _.template($('#imgdiv-template').html()),
        
        
        initialize: function() {
            // need to _.bind render to always run in the context
            // of the view since it is often run on a 'change' event
            // fired by the Tract model changing, which would otherwise
            // cause it to run in the context of the model
            _.bindAll(this, 'render', 'setRenderDistance');
            
            // doubly-linked, can be convenient
            this.model.view = this;
            
            // keeping track of which image we're viewing at any given time
            this.numPictures = this.model.get('pictures').length;
            this.imgDivs = Array(this.numPictures);
            this.nowImgDiv = null;
            this.nowImgIndex = 0;
            
            // initial render
            // create the first imgdiv
            templateParams = this.model.toJSON();
            templateParams['nowImgIndex'] = this.nowImgIndex;
            $(this.el).html(this.template(templateParams));            

            //this.setRenderDistance(true, 0);
            this.setRenderDistance(false, 0);
        },

        // this function sets the img caching parameters for the View
        // and then renders it
        setRenderDistance: function(on, distance) {
            //console.debug(this.model.get('tractid'), on, distance);
            if (this.on && (on == false)) {
                this.dumpDivs();
            }
            this.on = on;               //whether ANY img divs should be kept

            this.distance = distance;   //how many right and left of current 
                                        //we require to be present
                                        //0 means "just the current"
                                        //> numPictures/2 means all

            this.render();


        },

        //$.remove()s all the imgDivs of the View to clear up space
        dumpDivs: function() {
            _.each(this.imgDivs, function(div) {
                if (div) { $(div).remove(); }   
            });
        },

        //render always returns this (the view rendered) to permit
        //chaining of calls like (view.render().el).hide()
        render: function() {            
            if (!this.on)                           { return this; }

            //ensure that sufficient context exists left and right

            //current one
            this.createImgDiv(this.nowImgIndex);

            //actual distance
            // (limited to half the number of pictures we have)
            var dist = Math.min(Math.floor(this.numPictures/2), this.distance); 
            
            //context
            for (var i=1; i<=dist; i++) {
               var rightIndex = (this.nowImgIndex+i) % this.imgDivs.length;
               var leftIndex = (this.nowImgIndex-i);
               if (leftIndex < 0) {
                   leftIndex = this.imgDivs.length + leftIndex;
               }

               this.createImgDiv(rightIndex);
               this.createImgDiv(leftIndex);
            }

            var newImgDiv = this.imgDivs[this.nowImgIndex];
            $(this.nowImgDiv).hide();
            $(newImgDiv).show();
            this.nowImgDiv = newImgDiv;

            return this;
        },
        
        createImgDiv: function(index) {
            var newImgDiv = (this.imgDivs[index] || null);
            
            // create a new div if it hasn't been created yet
            if (newImgDiv === null) {
                templateParams = this.model.toJSON();
                templateParams['nowImgIndex'] = index;
                if (templateParams.pictures.length != 0) {
                    newImgDiv = $(this.imgDivTemplate(templateParams));
                }
                else {
                    newImgDiv = $('<div>No pictures here, move along</div>');
                }
                this.imgDivs[index] = newImgDiv.hide();
                this.$('.tract-pictures').append(newImgDiv);
            }                        
            
        },
        
        nextPicture: function() {            
            var imgIndex = this.nowImgIndex;
            var maxImgIndex = this.model.get('pictures').length-1;

            this.trigger('nav:img', 'right');
                                              
            // roll around to start if overflowing the end of the pictures
            if (imgIndex === maxImgIndex) { this.gotoImg(0) }
            // otherwise, increment
            else                          { this.gotoImg(imgIndex+1)  }
                                                           
        },
        
        previousPicture: function() {
            var imgIndex = this.nowImgIndex;
            var maxImgIndex = this.model.get('pictures').length-1;
            
            this.trigger('nav:img', 'left');

            // roll around to end if going negative
            if (imgIndex <= 0)        { this.gotoImg(maxImgIndex) }
            // otherwise, decrement
            else                       { this.gotoImg(imgIndex-1 ) }
        },
        
        gotoImg: function(imgIndex) {
            this.nowImgIndex = imgIndex;
            this.render();
        }

    });
    
    TractDataManager = function(ring) {
        this.ring = ring;
        this.width = 2;       //number of tracts of context required
        this.initialize();
    }
    
    //include Backbone Events in the TractDataManager
    _.extend(TractDataManager.prototype, Backbone.Events);
    
    //give real functionality to the TractDataManager
    _.extend(TractDataManager.prototype, {
        
        initialize: function() {
            _.bindAll(this, 'addTractsCB', 'reach', 'manageImages');
            this.ring.bind('nav:tract', this.reach);
            this.ring.bind('nav:tract', this.manageImages);
            this.ring.bind('refresh', this.manageImages);
            this.pending = {};
            this.pending.left = this.pending.right = null;
        },
        
        manageImages: function() {
            var r = this.ring;
            var i = r.currentTractIndex;
            var ct = r.currentTract;
            
            if (!ct) { return; }
            
            //set the current tract's view to 3
            if (ct.view) {
                ct.view.setRenderDistance(true, 3);
            }
            
            //adjacent to 1
            if (r.at(i+1)) {
                r.at(i+1).view.setRenderDistance(true, 1);
            }
            if (r.at(i-1)) {
                r.at(i-1).view.setRenderDistance(true, 1);
            }
        
            //doubly adjacent to on/0
            if (r.at(i+2)) {
                r.at(i+2).view.setRenderDistance(true, 0);
            }
            if (r.at(i-2)) {
                r.at(i-2).view.setRenderDistance(true, 0);
            }
        },

        //direction comes from the second argument to the Backbone.trigger call
        //that caused this callback to fire
        reach: function(direction) {
            var needContext = false;
            var from = -1;
            var amount = 10;

            var allowable = (this.ring.length - 1) - this.width;
            if (this.ring.currentTractIndex < this.width &&
                                   direction === 'left') {
                needContext = true;
                from = this.ring.first().get('order');
            }
            else if (this.ring.currentTractIndex > allowable &&
                                      direction === 'right') {
                needContext = true;
                from = this.ring.last().get('order');
            }
            
            //if we don't need context, we're done
            if (!needContext)                         { return; }
            // if we already are fetching context in this direction,
            // don't do it again!
            if (this.pending[direction])              { return; }

            // GET parameters for the AJAX request
            var getParams = {
                n: amount,
                j: from,
                dir: direction,
            };

            // make the request
            request = $.ajax({
                            url: fetch_url,
                            data: getParams,
                            type: 'GET',
                            dataType: 'json',
                            context: this,         //context for callbacks
                            success: function(tracts) {
                                this.addTractsCB(tracts, direction, from);
                            },
                            error: this.retryAjax
            });

            //and note the request in this.pending
            this.pending[direction] = request;
        },

        addTractsCB: function(newTracts, direction, from) {
            //if the server gave back context that includes j,
            //don't add j again right after itself
            if (newTracts[0].order === from) { 
                newTracts.shift(); 
                console.debug('Server gave j back with results, not duping it');
            }
            
	        //for each new tract
            _.each(newTracts, function(newTract) {
                if (direction === 'right') {
                    this.ring.add(newTract);
                }
                else {
                    this.ring.addLeft(newTract);
                }
                console.debug('adding: '+newTract.order);
                
            }, this);  //set the context for the _.each to the manager

            //request is finished, note it
            this.pending[direction] = null;
	    },

        //not a very good retrying function... TODO rewrite it 
        retryAjax: function(xhr, textStatus, errorThrown) {
            if (textStatus == 'timeout') {
                this.trigger('error:fetch-timeout');
                // failure?  try again in 10 seconds
                setTimeout($.ajax(this), 10000);
            }
        }
        
    });
    
    
    // the AppView handles controls for next/prev tract/img
    AppView = Backbone.View.extend({

        el: $('#census-app'),
        
        events: {            
            'click #left':              'left',
            'click #right':             'right',
            'click #nextPicture':       'nextPicture',
            'click #previousPicture':   'previousPicture',
        },
        
        initialize: function() {
            // might have to do some bindAlling here...
            _.bindAll(this, 'addOneView', 'render');            
        
            this.currentTractOrder = 0;
            this.shownView = null;  
                        
            Tracts.bind('all',       this.render);
            Tracts.fetch();


        },
        
        
        render: function() {            
            var currentTract = (Tracts.currentTract || null);  
            if (currentTract === null) { return; }
            var currentView = (currentTract.view || null);
            if (currentView === null) { return; }
           
    	    var $debug_numTracts = ($('#DEBUG-numTracts') || null);
            if ($debug_numTracts.length > 0) {
        	    $debug_numTracts.html(Tracts.length-1);
            }
            var $debug_nowTract = ($('#DEBUG-nowTract') || null);
            if ($debug_nowTract.length > 0) {
                $debug_nowTract.html(Tracts.currentTractIndex);
            }
 
            // show the new tract's view, hide the old one
            if (this.shownView !== null) { 
                $(this.shownView.el).hide(); 
            }
            $(currentView.el).show();
            this.shownView = currentView;

            // show the correct stats for this new tract            
            this.displayStats(this.shownView.model);       

            // pan the map/set a marker for the new location we're viewing
            // updateMap(lat, lng)
        },

        displayStats: function(tract) {

            summaryTemplate = _.template($('#summary-template').html()),
            console.debug('displaying stats:');
            console.debug(tract);
            // displaying stats is now displaying summaries
            // for the first 3 items in tract.summaries
                var display_count = 3;
                var list_html = '';
                s = tract.get('summaries');
                for (var i=0; i<display_count; i++) {
                    console.debug('sentence:');
                    console.debug(s);
                    console.debug(s[i].sentence);
                    var t = {'sentence': s[i].sentence,
                             'statName': s[i].category+s[i].name};
                                          
                    list_html += summaryTemplate(t);
                }
                
                $('#stat-summaries').html(list_html);

            /*
            var data = tract.get('data');
            for (var i=0;i<render_functions.length;i++) {
                render_functions[i](data, map);
            }
            */
        },


        //
        addOneView: function(tract) {                  
            var view = new TractView({model: tract});
            $(view.render().el).hide();
            this.$('#tract-view-box').append(view.el);
        },
        
        left:  function() { Tracts.moveLeft(); },
        right: function() { Tracts.moveRight(); },
        
        nextPicture: function() {
            Tracts.currentTract.view.nextPicture();
        },
        
        previousPicture: function() {
            Tracts.currentTract.view.previousPicture();
        }
    });

    Tracts = new TractRing();
    App = new AppView();

    DEBUGON = function() {
        $debugElements = $('.debug');
        $debugElements.addClass('.debugVisible');
    }
    DEBUGOFF = function() {
        $debugElements = $('.debug');
        $debugElements.removeClass('.debugVisible');
    }

    
});

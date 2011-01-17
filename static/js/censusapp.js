var fetch_url = 'http://localhost:8080/context';

$(function() {

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
            var url = 'http://localhost:8080/context';
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
                
            this.bind('add', this.fixDisplacedIndex);
                
            // create a new TractDataManager
            this.manager = new TractDataManager(this);
            
            this.currentTract = null;
            this.currentTractIndex = null;

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
               this.models.unshift(model);
               model.bind('all', this._boundOnModelEvent);
               this.length++;
               if (!options.silent) model.trigger('add', model, this, options);
               return model;


        },
        //comparator: function(tract) { return tract.get('order'); },   
        
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
        
        // This function is called when an 'add' event is
        // fired on the collection.        
        fixDisplacedIndex: function() {        
            // locate the correct index in the collection
            // for this.currentTract
            
            // if we added stuff only to the right,
            // this will be the same as the current 
            // this.currentTractIndex
            
            // if we added stuff to the left, then the new
            // index is GREATER THAN the stored value
            // and searching UP will find it quickly
            
            // the search wraps around until it comes back to
            // the starting value, in case of big problems
            
            // if there's no currentTract, don't bother trying
            // to fix things that don't exist
            if (this.currentTract == null)           { return; }
            
            // orig is the currentTractIndex we had stored
            // before we added in more tracts
            var orig = this.currentTractIndex;        

            // we will compare tracts by id rather than
            // === in order to make sure that if a tract is
            // overwritten by a duplicate tract, they still
            // compare as the same thing.
            var origID = this.currentTract.get('tractid')
            
            // current correct?
            // if so, no need to modify the currentTractIndex
            if (this.at(orig).get('tractid') == origID)   { 
//              console.debug('leaving currentTractIndex at '+orig);
                return; 
            }
            
            // climb to max, loop to 0, climb to orig
            var counter = orig+1;
            if (counter > this.length-1) {
                counter = 0;
            }
            while (counter != orig) {
                if (this.at(counter).get('tractid') == origID) {
                    this.currentTractIndex = counter;
//                  console.debug('setting currentTractIndex to '+counter+' (originally '+orig+')');
                    return;                
                }
                
                counter++;
                if (counter > this.length-1) { 
                    counter = 0; 
                }
            }
            // if we get here, somehow the tract wasn't in
            // the collection after adding more tracts
            // UHhhh....
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
            _.bind(this, 'render');
            
            // doubly-linked, can be convenient
            this.model.view = this;
            
            // keeping track of which image we're viewing at any given time
            this.nowImgIndex = 0;
            this.imgDivs = [];
            this.nowImgDiv = null;
            
            // initial render
            // create the first imgdiv
            templateParams = this.model.toJSON();
            templateParams['nowImgIndex'] = this.nowImgIndex;
            $(this.el).html(this.template(templateParams));            

            var nowImgDiv = null;
            if (templateParams.pictures.length != 0) {
                nowImgDiv = $(this.imgDivTemplate(templateParams));
            }
            else {
                nowImgDiv = $('<div>No pictures here, move along</div>');
            }
            this.imgDivs[this.nowImgIndex] = this.nowImgDiv;   
            this.$('.tract-pictures').append(this.nowImgDiv);
        },
        
        render: function() {            
            var newImgDiv = (this.imgDivs[this.nowImgIndex] || null);
            
            // create a new div if it hasn't been created yet
            if (newImgDiv === null) {
                templateParams = this.model.toJSON();
                templateParams['nowImgIndex'] = this.nowImgIndex;
                var newImgDiv = null;
                if (templateParams.pictures.length != 0) {
                    newImgDiv = $(this.imgDivTemplate(templateParams));
                }
                else {
                    nowImgDiv = '<div>No pictures here, move along</div>';
                }
                this.imgDivs[this.nowImgIndex] = newImgDiv;
                this.$('.tract-pictures').append(newImgDiv); 
            }                        
            
            $(this.nowImgDiv).hide();
            $(newImgDiv).show();
            this.nowImgDiv = newImgDiv;

            return this;
        },
        
        nextPicture: function() {            
            var imgIndex = this.nowImgIndex;
            var maxImgIndex = this.model.get('pictures').length-1;
            
            // roll around to start if overflowing the end of the pictures
            if (imgIndex === maxImgIndex) { this.gotoImg(0) }
            // otherwise, increment
            else                          { this.gotoImg(imgIndex+1)  }
        },
        
        previousPicture: function() {
            var imgIndex = this.nowImgIndex;
            var maxImgIndex = this.model.get('pictures').length-1;
            
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
        this.width = 2;
        this.initialize();
    }
    
    //include Backbone Events in the TractDataManager
    _.extend(TractDataManager.prototype, Backbone.Events);
    
    //give real functionality to the TractDataManager
    _.extend(TractDataManager.prototype, {
        
        initialize: function() {
            _.bindAll(this, 'addTractsCB', 'reach')//, 'reachLeft', 'reachRight');
            this.ring.bind('nav:tract', this.reach);
            this.pending = {};
            this.pending.left = this.pending.right = null;
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
    
    ImageDataManager = function(view) {
    
    };
    
    // the AppView handles controls for next/prev tract/img
    AppView = Backbone.View.extend({

        el: $('#census-app'),
        
        events: {            
            'click #left':              'left',
            'click #right':             'right',
            'click #nextPicture':       'nextPicture',
            'click #previousPicture':   'previousPicture'
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
 
            $('.inlinesparkline').sparkline(Tracts.map(function(t) { return t.get('order'); }));
            if (this.shownView !== null) { 
                $(this.shownView.el).hide(); 
            }
            $(currentView.el).show();
            this.shownView = currentView;
                   
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

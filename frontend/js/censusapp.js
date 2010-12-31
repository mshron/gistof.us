var fetch_url = 'localhost:8080/context';

$(function() {

    Tract = Backbone.Model.extend({});
    
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
                }
                
            this.bind('add', fixDisplacedIndex);
                
            // create a new TractDataManager
            this.manager = new TractDataManager(this);
            
            this.currentTract = null;
            this.currentTractIndex = null;
        },             
        
        comparator: function(tract) { return tract.get('order'); },   
        
        moveLeft: function() {            
            //all the way left?  let everyone know
            // this only happens when we haven't succeeded in fetching
            // more tract data from the left
            if (this.currentTractIndex == 0) {
                this.trigger('nav:block-left');
            }
            else {                
                this.currentTract = this.at(--this.currentTractIndex);
                this.trigger('nav:tract-left');
            }
        },
            
        moveRight: function() {
            // all the way right?  let everyone know
            // this only happens when we haven't succeeded in fetching
            // more tract data from the right
            lastIndex = this.length-1;
            if (this.currentTractIndex == lastIndex) {
                this.trigger('nav:block-right');
            }
            else {
                this.currentTract = this.at(--this.currentTractIndex);
                this.trigger('nav:tract-right');
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
            var origID = this.currentTract.get('id')
            
            // current correct?
            // if so, no need to modify the currentTractIndex
            if (this.at(orig).get('id') == origID)   { return; }
            
            // climb to max, loop to 0, climb to orig
            var counter = orig+1;
            if (counter > this.length-1) {
                counter = 0;
            }
            while (counter != orig) {
                if (this.at(counter).get('id') == origID) {
                    this.currentTractIndex = counter;
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
            _.bindAll(this, 'render');
            
            // doubly-linked, can be convenient
            this.model.view = this;
            
            // keeping track of which image we're viewing at any given time
            this.nowImgIndex = 0;
            this.imgDivs = [];
            this.nowImgDiv = null;
            
            // initial render
            templateParams = this.model.toJSON();
            templateParams['nowImgIndex'] = this.nowImgIndex;
            $(this.el).html(this.template(templateParams));            
            this.nowImgDiv = this.$('.imgdiv');
            this.imgDivs[this.nowImgIndex] = this.nowImgDiv;

        },
        
        render: function() {            
            var newImgDiv = (this.imgDivs[this.nowImgIndex] || null);
            
            // create a new div if it hasn't been created yet
            if (newImgDiv === null) {
                templateParams = this.model.toJSON();
                templateParams['nowImgIndex'] = this.nowImgIndex;
                newImgDiv = $(this.imgDivTemplate(templateParams));
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
            if (imgIndex === 0)        { this.gotoImg(maxImgIndex) }
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
        this.width = 10;
        this.initialize();
    }
    
    //include Backbone Events in the TractDataManager
    _.extend(TractDataManager.prototype, Backbone.Events);
    
    //give real functionality to the TractDataManager
    _.extend(TractDataManager.prototype, {
        
        initialize: function() {
            //bind to tract-nav events
            this.bind('nav:tract-left', reachLeft);
            this.bind('nav:tract-right', reachRight);
            
            _.bindAll(this, lhCallback, rhCallback);
            
            this.pending.left = this.pending.right = null;
        
        },
        
        reachLeft: function() {
            //if this.ring.currentTractIndex is
            //within this.width of 0
            if (this.ring.currentTractIndex < this.width) {
                //if there's no leftwards request pending
                if (this.pending.left === null) {
                    //get more context to the left, calling back
                    //to lhCallback
                    var getParams = {
                        n: 20,
                        j: this.ring.first.get('id'),
                        direction: 'left',
                    };
                    request = $.ajax({
                                    url: url,
                                    data: getParams,
                                    type: 'GET',
                                    success: lhCallback,
                                    dataType: 'json',
                                    error: retryAjax
                    
                    });
                    //and noting the request in this.pending
                    this.pending.left = request;
                }
            }
        },
        
                
        reachRight: function() {
            //if this.ring.currentTractIndex is
            //within this.width of this.ring.length
            var allowable = (this.ring.length - 1) - this.width;
            if (allowable < 0) { allowable = 0; }            
            if (this.ring.currentTractIndex > allowable) {
                //if there's no rightwards request pending
                //get more context to the right, calling 
                //back to rhCallback...
                if (this.pending.right === null) {
                    var getParams = {
                        n: 20,
                        j: this.ring.last.get('id'),
                        direction: 'right',
                    };
                    request = $.ajax({
                                    url: url,
                                    data: getParams,
                                    type: 'GET',
                                    success: rhCallback,
                                    dataType: 'json',
                                    error: retryAjax
                    
                    });
                    //and noting the request in this.pending
                    this.pending.right = request;
                }
            }
        },
        
        lhCallback: function(tracts) {
            //add the new tracts to the collection
            this.ring.add(tracts);            
            //clear the request from this.pending
            this.pending.left = null;
        },
        
        rhCallback: function(tracts) {
            //add the new tracts to the collection
            this.ring.add(tracts);            
            //clear the request from this.pending
            this.pending.right = null;
        },
        
        retryAjax: function(xhr, textStatus, errorThrown) {
            if (textStatus == 'timeout') {
                this.trigger('error:fetch-timeout');
                // failure?  try again in 10 seconds
                setTimeout($.ajax(this), 10000);
            }
            
        }
        
    });
    
    ImageDataManager(view) = function(view) {
    
    }
    
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
            _.bindAll(this, 'addOneView', 'render');//'addAllViews', 'render')
            // not going to do it until I understand why
        
            this.currentTractOrder = 0;
            this.shownView = null;  
                        
            Tracts.bind('all',       this.render);
            //Tracts.bind('refresh',   this.addAllViews);                
            Tracts.fetch();


        },
        
        
        render: function() {            
            var currentTract = (Tracts.currentTract || null);  
            if (currentTract === null) { return; }
            
            var currentView = (currentTract.view || null);
            if (currentView === null) { return; }
           
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
    
}
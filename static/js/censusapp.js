var fetch_url = 'localhost:8080/context';

$(function() {

    Tract = Backbone.Model.extend({});

    TractRing = Backbone.Collection.extend({});
    
    TractView = Backbone.View.extend({});
    
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
    
    AppView = Backbone.View.extend({});

    Tracts = new TractRing();
    App = new AppView();
    
}
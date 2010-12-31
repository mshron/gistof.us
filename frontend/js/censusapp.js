$(function() {

    Tract = Backbone.Model.extend({});

    TractRing = Backbone.Collection.extend({

        model: Tract,
        
        // url used for the initial fetch of "default" values
        url: function() {
            var url = 'http://localhost:8080/context?n=11';
            var hash = window.location.hash;
            
            if (hash !== '' && !isNaN(hash)) { 
                url += '/'+hash; 
            } 
            
            return url;
        },
        
        initialize: function() {
            this.bind('refresh', this.initOrder);        
            
            this.currentOrder = 0;
            this.currentTract = null;            
        },
             
        
        comparator: function(tract) { return tract.get('order'); },        
        
        addLeft: function(tract) {},    
        addRight: function(tract) {},    
        leftmostOrder: function() { return this.first().get('order'); },
        rightmostOrder: function() { return this.last().get('order'); },   
        
        moveLeft: function() {
            order = this.currentOrder;
            nextTract = (this.at(order-1) || null);
            
            if (nextTract === null) { return; }
            else {
                this.currentOrder = order-1;
                this.currentTract = nextTract
            }
            this.trigger('change');
        },
            
            
        moveRight: function() {
            order = this.currentOrder;
            nextTract = (this.at(order+1) || null);
            
            if (nextTract === null) { return; }
            else {
                this.currentOrder = order+1;
                this.currentTract = nextTract;
            }
            this.trigger('change');
        },
        
        fetchLeft: function() {},
        fetchRight: function() {},        
        
        initOrder: function() {
            var len = this.length;
            if (len === 0) { return; }

            // center index of a list of any non-zero length is always
            // at floor(length/2)
            var center = Math.floor(this.length/2)
            this.currentTract = this.at(center);
            this.currentOrder = this.currentTract.get('order');
            
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
            
            // mostly this is changes to nowImgIndex
            // this.model.bind('change', this.render);
           
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
            else                          { this.gotoImg(imgIndex+1)  }
        },
        
        previousPicture: function() {
            var imgIndex = this.nowImgIndex;
            var maxImgIndex = this.model.get('pictures').length-1;
            
            // roll around to end if going negative
            if (imgIndex === 0)        { this.gotoImg(maxImgIndex) }
            else                       { this.gotoImg(imgIndex-1 ) }
        },
        
        gotoImg: function(imgIndex) {
            this.nowImgIndex = imgIndex;
            this.render();
        }

    });

    // the AppView contains the controls for next/prev
    // and the area where the current TractView is displayed?
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
            _.bindAll(this, 'addOneView', 'addAllViews', 'render')
            // not going to do it until I understand why
        
            this.currentTractOrder = 0;
            this.shownView = null;  
                        
            Tracts.bind('all',       this.render);
            Tracts.bind('refresh',   this.addAllViews);                
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
        
        // 
        addAllViews: function() {                       
            Tracts.each(this.addOneView);
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
});